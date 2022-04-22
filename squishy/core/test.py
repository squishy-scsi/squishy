# SPDX-License-Identifier: BSD-3-Clause
from functools       import wraps
from unittest        import TestCase

from math            import ceil

from amaranth        import Signal
from pathlib         import Path
from amaranth.sim    import Simulator
from amaranth.hdl.ir import Fragment

__all__ = (
	'SquishyGatewareTestCase',
)


class SquishyGatewareTestCase(TestCase):
	domain    = 'sync'
	freq      = 1e8
	out_dir   = None
	platform  = None
	_dut      = None
	_dut_args = {}

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

	@property
	def vcd_name(self) -> str:
		return f'test-{self.__class__.__name__}'

	@property
	def clk_period(self) -> float:
		return 1 / self.freq

	def sim(self, *, suffix : str = None) -> None:
		out_name = f'{self.vcd_name}{f"-{suffix}" if suffix is not None else ""}'
		out_file = self.out_dir / out_name
		with self.sim.write_vcd(f'{out_file}.vcd', f'{out_file}.gtkw'):
			self.sim.reset()
			self.sim.run()

	def setUp(self) -> None:
		self.dut     = Fragment.get(self._dut, platform = self.platform)
		self.sim     = Simulator(self.dut)
		if self.out_dir is None:
			self.out_dir = Path.cwd() / 'tests'

		self.sim.add_clock(self.clk_period, domain = self.domain)

		if not self.out_dir.exists():
			self.out_dir.mkdir()

	def init_dut(self):
		return self.dut(**self.dut_args)

	def init_signals(self):
		yield Signal()

	def wait_for(self, time : float):
		c = ceil(time / self.clk_period)
		yield from self.step(c)

	@staticmethod
	def pulse(sig : Signal , *, post_step = True):
		yield sig.eq(1)
		yield
		yield sig.eq(0)
		if post_step:
			yield

	@staticmethod
	def step(cycles : int):
		for _ in range(cycles):
			yield

	@staticmethod
	def wait_until_high(strobe : Signal, *, timeout : int = None):
		elapsed = 0
		while not (yield strobe):
			yield
			elapsed += 1
			if timeout and elapsed > timeout:
				raise RuntimeError(f'Timeout waiting for \'{strobe.name}\' to go high')

	@staticmethod
	def wait_until_low(strobe : Signal, *, timeout : int = None):
		elapsed = 0
		while (yield strobe):
			yield
			elapsed += 1
			if timeout and elapsed > timeout:
				raise RuntimeError(f'Timeout waiting for \'{strobe.name}\' to go low')

def sim_test(func, *, domain = 'sync', freq : float = 1e8):
	def _run(self):
		@wraps(func)
		def sim_case():
			yield from self.init_signals()
			yield from func(self)

		self.domain = domain
		self.freq   = freq
		self.sim.add_sync_process(sim_case, domain = domain)
		self.sim(suffix = func.__name__)
	return _run
