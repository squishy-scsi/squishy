# SPDX-License-Identifier: BSD-3-Clause
from nmigen import *

__all__ = (
	'ICE40ClockDomainGenerator',
	'ECP5ClockDomainGenerator',
)

class ICE40ClockDomainGenerator(Elaboratable):
	def elaborate(self, platform):
		m = Module()

		m.domains.usb  = ClockDomain()
		m.domains.sync = ClockDomain()


		platform.lookup(platform.default_clk).attrs['GLOBAL'] = False

		clk100 = Signal()
		m.submodules.pll = Instance(
			'SB_PLL40_PAD',
			i_PACKAGEPIN = platform.request(platform.default_clk, dir = 'i'),
			i_RESETB     = Const(1),
			i_BYPASS     = Const(0),

			o_PLLOUTGLOBAL = clk100,

			p_FEEDBACK_PATH = 'SIMPLE',
			p_PLLOUT_SELECT = 'GENCLK',

			# 200MHz
			p_DIVR         = platform.pll_config['divr'],
			p_DIVF         = platform.pll_config['divf'],
			p_DIVQ         = platform.pll_config['divq'],
			p_FILTER_RANGE = platform.pll_config['frange'],
		)


		platform.add_clock_constraint(clk100, platform.pll_config['freq'])

		m.d.comb += [
			ClockSignal('sync').eq(clk100),
		]

		return m

class ECP5ClockDomainGenerator(Elaboratable):
	def __init__(self):
		self.pll_locked = Signal()

	def elaborate(self, platform):
		m = Module()

		m.domain.usb   = ClockDomain()
		m.domains.sync = ClockDomain()

		platform.lookup(platform.default_clk).attrs['GLOBAL'] = False

		clk = Signal()

		# TODO: Actually do pll nyoom things
		m.submodules.pll = Instance()

		platform.add_clock_constraint(clk, platform.pll_config['freq'])

		m.d.comb += [
			ClockSignal('sync').eq(clk)
		]

		return m
