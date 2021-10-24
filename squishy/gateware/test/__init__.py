# SPDX-License-Identifier: BSD-3-Clause
from unittest import TestCase

from nmigen   import Signal

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
	def vcd_name(self):
		return f'test-{self.__class__.__name__}'

	@property
	def clk_period(self):
		return 1 / self.freq

	def sim(self, *, suffix = None):
		out_name = f'{self.vcd_name}{f"-{suffix}" if suffix is not None else ""}'
		out_file = path.join(self.out_dir, out_name)
		with self.sim.write_vcd(f'{out_file}.vcd', f'{out_file}.gtkw'):
			self.sim.reset()
			self.sim.run()

	def setUp(self):
		from os            import path, mkdir, getcwd
		from nmigen.sim    import Simulator
		from nmigen.hdl.ir import Fragment

		self.dut     = Fragment.get(self._dut, platform = self.platform)
		self.sim     = Simulator(self.dut)
		if self.out_dir is None:
			self.out_dir = getcwd()

		self.sim.add_clock(self.clk_period, domain = self.domain)

		if not path.exists(self.out_dir):
			mkdir(self.out_dir)

	def init_dut(self):
		return self.dut(**self.dut_args)

	def init_signals(self):
		yield Signal()

	def wait_for(self, time):
		c = math.ceil(time / self.clk_period)
		yield from self.step(c)

	@staticmethod
	def pulse(sig, *, post_step = True):
		yield sig.eq(1)
		yield
		yield sig.eq(0)
		if post_step:
			yield

	@staticmethod
	def step(cycles):
		for _ in range(cycles):
			yield

	@staticmethod
	def wait_until_high(strb, *, timeout = None):
		elapsed = 0
		while not (yield strb):
			yield
			elapsed += 1
			if timeout and elapsed > timeout:
				raise RuntimeError(f'Timeout waiting for \'{strb.name}\' to go high')

	@staticmethod
	def wait_until_low(strb, *, timeout = None):
		elapsed = 0
		while (yield strb):
			yield
			elapsed += 1
			if timeout and elapsed > timeout:
				raise RuntimeError(f'Timeout waiting for \'{strb.name}\' to go low')

def sim_test(func, *, domain = 'sync', freq = 1e8):
	def _run(self):
		@wraps(func)
		def sim_case():
			yield from self.init_signals()
			yield from func(self)

		self.domain = domain
		self.freq   = freq
		self.sim.add_sync_process(sim_case, domain = domain)
		self.sim(suffix = func.__name__)
