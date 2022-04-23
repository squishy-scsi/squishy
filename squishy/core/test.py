# SPDX-License-Identifier: BSD-3-Clause
from functools       import wraps
from unittest        import TestCase

from math            import ceil

from amaranth        import Signal
from pathlib         import Path
from amaranth.sim    import Simulator

__all__ = (
	'SquishyGatewareTestCase',
)


class SquishyGatewareTestCase(TestCase):
	'''Gateware test case wrapper for pythons unittest library

	This class wraps the :py:class:`TestCase` class from the `unittest` module
	from the python standard lib. It has usefull methods for testing and simulating
	Amaranth based gateware.

	Attributes
	----------
	domain : str
		The root clock domain.
	freq : float
		The frequency of the domain.
	out_dir : str
		The test output directory.
	dut : Elaboratable
		The elaboratable to test.
	dut_args : dict[str, Any]
		The initialization arguments for the elaboratable.

	'''

	domain    = 'sync'
	freq      = 1e8
	out_dir   = None
	dut       = None
	dut_args  = {}

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

	@property
	def vcd_name(self) -> str:
		'''The name of the VCD for this test case'''

		return f'test-{self.__class__.__name__}'

	@property
	def clk_period(self) -> float:
		'''The clock period of the domain'''

		return 1 / self.freq

	def run_sim(self, *, suffix : str = None) -> None:
		'''Run the simulation

		Keyword Args
		------------
		suffix : str
			The option VCD test case suffix.

		'''

		out_name = f'{self.vcd_name}{f"-{suffix}" if suffix is not None else ""}'
		out_file = self.out_dir / out_name
		with self.sim.write_vcd(f'{out_file}.vcd'):
			self.sim.reset()
			self.sim.run()

	def setUp(self) -> None:
		'''Initialize the test case with the given DUT'''

		self.dut     = self.init_dut()
		self.sim     = Simulator(self.dut)
		if self.out_dir is None:
			if (Path.cwd() / 'build').exists():
				self.out_dir = Path.cwd() / 'build' / 'tests'
			else:
				self.out_dir = Path.cwd() / 'test-vcds'

		self.sim.add_clock(self.clk_period, domain = self.domain)

		if not self.out_dir.exists():
			self.out_dir.mkdir()

	def init_dut(self):
		'''Initialize the DUT with the given DUT arguments'''

		return self.dut(**self.dut_args)

	def init_signals(self):
		''' Initialize any signals from the DUT instance to a known state'''

		yield Signal()

	def wait_for(self, time : float):
		''' Waits for the number time units.

		Parameters
		----------
		time : float
			The unit of time to wait.

		'''

		c = ceil(time / self.clk_period)
		yield from self.step(c)

	@staticmethod
	def pulse(sig : Signal , *, neg : bool = False, post_step : bool = True):
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
	def pulse_pos(sig : Signal, *, post_step : bool = True):
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
	def pulse_neg(sig : Signal, *, post_step : bool = True):
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
	def step(cycles : int):
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
	def wait_until_high(strobe : Signal, *, timeout : int = None):
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
	def wait_until_low(strobe : Signal, *, timeout : int = None):
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

def sim_test(func, *, domain = 'sync'):
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

	def _run(self):
		@wraps(func)
		def sim_case():
			yield from self.init_signals()
			yield from func(self)

		self.domain = domain
		self.sim.add_sync_process(sim_case, domain = domain)
		self.run_sim(suffix = func.__name__)
	return _run
