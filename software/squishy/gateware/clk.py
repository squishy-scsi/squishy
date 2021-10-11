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

		# TODO: Verify PLL settings
		m.submodules.pll = Instance(
			'EHXPLLL',

			i_CLKI    = platform.request(platform.default_clk, dir = 'i'),

			o_CLKOP   = clk,
			i_CLKFB   = clk,
			i_ENCLKOP = Const(1),
			o_LOCK    = self.pll_locked,

			i_RST       = Const(0),
			i_STDBY     = Const(0),

			i_PHASESEL0    = Const(0),
			i_PHASESEL1    = Const(0),
			i_PHASEDIR     = Const(1),
			i_PHASESTEP    = Const(1),
			i_PHASELOADREG = Const(1),
			i_PLLWAKESYNC  = Const(0),

			# Params
			p_PLLRST_ENA      = 'DISABLED',
			p_INTFB_WAKE      = 'DISABLED',
			p_STDBY_ENABLE    = 'DISABLED',
			p_DPHASE_SOURCE   = 'DISABLED',
			p_OUTDIVIDER_MUXA = 'DIVA',
			p_OUTDIVIDER_MUXB = 'DIVB',
			p_OUTDIVIDER_MUXC = 'DIVC',
			p_OUTDIVIDER_MUXD = 'DIVD',
			p_CLKOP_ENABLE    = 'ENABLED',
			p_CLKOP_CPHASE    = Const(0),
			p_CLKOP_FPHASE    = Const(0),
			p_FEEDBACK_PATH   = 'CLKOP',

			p_CLKI_DIV        = platform.pll_config['clki_div'],
			p_CLKOP_DIV       = platform.pll_config['clkop_div'],
			p_CLKFB_DIV       = platform.pll_config['clkfb_div'],


			# Attributes for synth
			a_FREQUENCY_PIN_CLKI     = str(platform.pll_config['ifreq']),
			a_FREQUENCY_PIN_CLKOP    = str(platform.pll_config['ofreq']),
			a_ICP_CURRENT            = '12',
			a_LPF_RESISTOR           = '8',
			a_MFG_ENABLE_FILTEROPAMP = '1',
			a_MFG_GMCREF_SEL         = '2',
		)

		platform.add_clock_constraint(clk, platform.pll_config['freq'])

		m.d.comb += [
			ClockSignal('sync').eq(clk)
		]

		return m
