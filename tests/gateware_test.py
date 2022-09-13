# SPDX-License-Identifier: BSD-3-Clause
import logging        as log
from functools        import wraps
from pathlib          import Path
from unittest         import TestCase
from math             import ceil
from os               import getenv

from amaranth         import Signal
from amaranth.sim     import Simulator
from amaranth.hdl.ir  import Fragment
from amaranth.hdl.rec import Record, DIR_FANIN, DIR_FANOUT

__all__ = (
	'SquishyGatewareTestCase',
)

class _MockRecord(Record):
	"""Mock Amaranth Record

	This class is a modified version of :py:class:`Record`
	that dynamically allocates a record for every field
	requested by name, and caches it.

	This allows :py:class:`_MockPlatform` to return an object
	of :py:class:`_MockRecord` from ``request`` and have it
	always be "correct".

	This is done by shiming the ``__getitem__`` call and when
	the field lookup fails to allocate a new record with the
	requested name and return that.

	..warning:: This only returns a record with 1-wide ``o`` and ``i`` fields

	"""

	def _insert_field(self, item: str):
		"""Construct mocked Record

		When the call to ``__getitem__`` runs into a field that
		we have not mocked before, and the field is a str, then
		we insert a mocked record with an ``i`` and ``o`` field
		into the parent records fields.

		..warning:: The field widths are currently set at 1

		Parameters
		----------
		item : str
			The requested field to mock

		"""

		self.fields[item] = Record((
			('o', 1, DIR_FANOUT),
			('i', 1, DIR_FANIN )
		), name = f'{item}')

	def __init__(self, *args, **kwargs) -> None:
		super().__init__((), *args, **kwargs)
		self.fields = {}

	def __getitem__(self, item):
		"""Return record field

		If the field doesn't exist, we create it with a call
		to ``_insert_field`` then return the generated field.

		Parameters
		----------
		item : Any
			The name of the requested field

		"""

		if isinstance(item, str):
			try:
				return self.fields[item]
			except KeyError:
				self._insert_field(item)
			return self.fields[item]
		else:
			return super().__getitem__(item)

class _MockPlatform:
	"""Mock Amaranth Platform

	This is a mock platform that returns a :py:class:`_MockRecord`
	whenever any call to ``request`` is made, regardless of the
	resource being requested.

	"""

	def request(self, name: str, number: int = 0) -> _MockRecord:
		"""Request a resource from the platform

		This call returns a :py:class:`_MockRecord` regardless
		of any of the parameters passed in.

		Parameters
		----------
		name : str
			The name of the resource to request
		number : int
			The index of the resource to request

		"""

		return _MockRecord()


class SquishyGatewareTestCase(TestCase):
	'''Gateware test case wrapper for pythons unittest library

	This class wraps the :py:class:`TestCase` class from the `unittest` module
	from the python standard lib. It has useful methods for testing and simulating
	Amaranth based gateware.

	Attributes
	----------
	domain : List[Tuple[str, float]]
		The collection of clock domains and frequencies
	out_dir : str
		The test output directory.
	dut : Elaboratable
		The elaboratable to test.
	dut_args : dict[str, Any]
		The initialization arguments for the elaboratable.
	platform : _MockPlatform, Any
		The platform passed to the Elaboratable DUT

	'''

	domains   = (('sync', 1e8),)
	out_dir   = None
	dut       = None
	dut_args  = {}
	platform  = _MockPlatform()

	def __init__(self, *args, **kwargs) -> None:
		super().__init__(*args, **kwargs)
		self._frag = None

	@property
	def vcd_name(self) -> str:
		'''The name of the VCD for this test case'''

		return f'test-{self.__class__.__name__}'

	def clk_period(self, domain: str = None) -> float:
		'''The clock period of the domain'''
		if domain is None:
			return 1 / self.domains[0][1]

		freq = next(d[1] for d in self.domains if d[0] == domain)

		return 1 / freq

	def run_sim(self, *, suffix : str = None) -> None:
		'''Run the simulation

		If the environment variable ``SQUISHY_TEST_INHIBIT_VCD``
		is set, then no VCDs will be generated.

		Keyword Args
		------------
		suffix : str
			The option VCD test case suffix.

		'''

		if getenv('SQUISHY_TEST_INHIBIT_VCD', default = False):
			log.warning('SQUISHY_TEST_INHIBIT_VCD is set! No VCDs will be generated for gateware tests!')

			self.sim.reset()
			self.sim.run()
		else:
			out_name = f'{self.vcd_name}{f"-{suffix}" if suffix is not None else ""}'
			out_file = self.out_dir / out_name
			with self.sim.write_vcd(f'{out_file}.vcd'):
				self.sim.reset()
				self.sim.run()

	def setUp(self) -> None:
		'''Initialize the test case with the given DUT'''

		self.dut     = self.init_dut()
		self._frag   = Fragment.get(self.dut, self.platform)
		self.sim     = Simulator(self._frag)
		if self.out_dir is None:
			if (Path.cwd() / 'build').exists():
				self.out_dir = Path.cwd() / 'build' / 'tests'
			else:
				self.out_dir = Path.cwd() / 'test-vcds'

		for d, _ in self.domains:
			self.sim.add_clock(self.clk_period(d), domain = d)

		if not self.out_dir.exists():
			self.out_dir.mkdir()

	def init_dut(self):
		'''Initialize the DUT with the given DUT arguments'''

		return self.dut(**self.dut_args)

	def init_signals(self) -> Signal:
		''' Initialize any signals from the DUT instance to a known state'''

		yield Signal()

	def wait_for(self, time: float, domain: str = None):
		''' Waits for the number time units.

		Parameters
		----------
		time : float
			The unit of time to wait.

		'''

		c = ceil(time / self.clk_period(domain))
		yield from self.step(c)

	@staticmethod
	def pulse(sig: Signal , *, neg: bool = False, post_step: bool = True):
		'''Pulse a given signal.

		Pulse a given signal to 1 then 0, or if `neg` is set to `True` pulse
		from 1 to 0.

		Parameters
		----------
		sig : Signal
			The signal to pulse.

		Keyword Args
		------------
		neg : bool
			Inverts the pulse direction.
		post_step : bool
			Instert additional simulation step after pulse.

		'''
		if not neg:
			yield sig.eq(1)
			yield
			yield sig.eq(0)
		else:
			yield sig.eq(0)
			yield
			yield sig.eq(1)
		if post_step:
			yield

	@staticmethod
	def pulse_pos(sig : Signal, *, post_step: bool = True):
		'''Inserts a positive pulse on the given signal

		Parameters
		----------
		sig : Signal
			The signal to pulse.

		Keyword Args
		------------
		post_step : bool
			Instert additional simulation step after pulse.

		'''

		yield from SquishyGatewareTestCase.pulse(sig, neg = False, post_step = post_step)

	@staticmethod
	def pulse_neg(sig: Signal, *, post_step: bool = True):
		'''Inserts a negative pulse on the given signal

		Parameters
		----------
		sig : Signal
			The signal to pulse.

		Keyword Args
		------------
		post_step : bool
			Instert additional simulation step after pulse.

		'''

		yield from SquishyGatewareTestCase.pulse(sig, neg = True, post_step = post_step)

	@staticmethod
	def step(cycles: int):
		'''Step simulator.

		This advances the simulation by the given number of cycles.

		Parameters
		----------
		cycles : int
			Number of cycles to step the simulator.

		'''

		for _ in range(cycles):
			yield

	@staticmethod
	def wait_until_high(strobe: Signal, *, timeout: int = None):
		'''Run simulation until signal goes high.

		Runs the simulation while checking for the positive edge of the `strobe`
		signal.

		Will run until a positive edge is seen, or if `timeout` is set, will run
		for at most that many cycles.

		This is the positive counterpart for the :py:func:`wait_until_low` method.

		Parameters
		----------
		strobe : Signal
			The signal to check the strobe for.

		Keyword Args
		------------
		timeout : int
			The max number of cycles to wait.
		'''

		elapsed_cycles = 0
		while not (yield strobe):
			yield
			elapsed_cycles += 1
			if timeout and elapsed_cycles > timeout:
				raise RuntimeError(f'Timeout waiting for \'{strobe.name}\' to go high')

	@staticmethod
	def wait_until_low(strobe: Signal, *, timeout: int = None):
		'''Run simulation until signal goes low.

		Runs the simulation while checking for the negative edge of the `strobe`
		signal.

		Will run until a negative edge is seen, or if `timeout` is set, will run
		for at most that many cycles.

		This is the negative counterpart for the :py:func:`wait_until_high` method.

		Parameters
		----------
		strobe : Signal
			The signal to check the strobe for.

		Keyword Args
		------------
		timeout : int
			The max number of cycles to wait.
		'''

		elapsed_cycles = 0
		while (yield strobe):
			yield
			elapsed_cycles += 1
			if timeout and elapsed_cycles > timeout:
				raise RuntimeError(f'Timeout waiting for \'{strobe.name}\' to go low')

def sim_test(*, domain = None):
	'''Simulation test case decorator

	Parameters
	----------
	func
		The decorated function.

	Keyword Args
	------------
	domain : str
		The clock domain this case belongs to.

	'''
	def _test(func):
		def _run(self):
			@wraps(func)
			def sim_case():
				yield from self.init_signals()
				yield from func(self)

			if domain is None:
				test_domain = self.domains[0][0]
			else:
				test_domain = domain

			self.sim.add_sync_process(sim_case, domain = test_domain)
			self.run_sim(suffix = func.__name__)
		return _run
	return _test
