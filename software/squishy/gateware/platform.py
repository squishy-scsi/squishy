# SPDX-License-Identifier: BSD-3-Clause
from nmigen                            import *
from nmigen.build                      import *
from nmigen.vendor.lattice_ice40       import *
from nmigen_boards.resources.memory    import SPIFlashResources
from nmigen_boards.resources.user      import LEDResources
from nmigen_boards.resources.interface import UARTResource

__all__ = (
	'Rev1',


	'AVAILABLE_PLATFORMS',
	'ICE40ClockDomainGenerator',
)

class ICE40ClockDomainGenerator(Elaboratable):
	def __init__(self, *, pll_cfg):
		self._pll_cfg = pll_cfg

	def elaborate(self, platform):
		m = Module()

		m.domains.usb    = ClockDomain()
		m.domains.sync   = ClockDomain()


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
			p_DIVR         = self._pll_cfg['divr'],
			p_DIVF         = self._pll_cfg['divf'],
			p_DIVQ         = self._pll_cfg['divq'],
			p_FILTER_RANGE = self._pll_cfg['frange'],
		)


		platform.add_clock_constraint(clk100, self._pll_cfg['freq'])

		m.d.comb += [
			ClockSignal('sync').eq(clk100),
		]

		return m

class Rev1(LatticeICE40Platform):
	device      = 'iCE40HX8K'
	package     = 'BG121'
	default_clk = 'clk'
	toolchain   = 'Trellis'

	clock_domain_generator = ICE40ClockDomainGenerator

	pll_config = {
		'freq'  : 1e8,
		'divr'  : 2,
		'divf'  : 49,
		'divq'  : 3,
		'frange': 1,
	}

	resources = [
		Resource('clk', 0,
			Pins('L5', dir = 'i'),
			Clock(48e6),
			Attrs(GLOBAL = True, IO_STANDARD = 'SB_LVCMOS')
		),

		Resource('ulpi', 0,
			Subsignal('clk',
				Pins('G1', dir = 'i'),
				Clock(60e6)
			),
			Subsignal('data',
				Pins('E1 E2 F1 F2 G2 H1 H2 J1', dir = 'io')
			),
			Subsignal('dir',
				Pins('D1', dir = 'i')
			),
			Subsignal('nxt',
				Pins('D2', dir = 'i')
			),
			Subsignal('stp',
				Pins('C2', dir = 'o')
			),
			Subsignal('rst',
				Pins('C1', dir = 'o')
			),

			Attrs(IO_STANDARD = 'SB_LVCMOS')
		),

		Resource('scsi_rx', 0,
			Subsignal('data',
				# 0, 1, 2, 3, 4, 5, 6, 7, P
				Pins('J10 G10 F10 D10 A11 C7 A9 A7 A5', dir = 'i')
			),
			Subsignal('io',
				Pins('A2', dir = 'i')
			),
			Subsignal('cd',
				Pins('A4', dir = 'i')
			),
			Subsignal('req',
				Pins('A3', dir = 'i')
			),
			Subsignal('sel',
				Pins('A6', dir = 'i')
			),
			Subsignal('msg',
				Pins('A8', dir = 'i')
			),
			Subsignal('rst',
				Pins('D9', dir = 'i')
			),
			Subsignal('ack',
				Pins('B11', dir = 'i')
			),
			Subsignal('bsy',
				Pins('E10', dir = 'i')
			),
			Subsignal('atn',
				Pins('H10', dir = 'i')
			),

			Attrs(IO_STANDARD = 'SB_LVCMOS')
		),

		Resource('scsi_tx', 0,
			Subsignal('data',
				# 0, 1, 2, 3, 4, 5, 6, 7, P
				Pins('J11 G11 F11 D11 A10 C8 C9 B8 B6', dir = 'o')
			),
			Subsignal('io',
				Pins('B3', dir = 'o')
			),
			Subsignal('cd',
				Pins('B5', dir = 'o')
			),
			Subsignal('req',
				Pins('B4', dir = 'o')
			),
			Subsignal('sel',
				Pins('B7', dir = 'o')
			),
			Subsignal('msg',
				Pins('B9', dir = 'o')
			),
			Subsignal('rst',
				Pins('E9', dir = 'o')
			),
			Subsignal('ack',
				Pins('C11', dir = 'o')
			),
			Subsignal('bsy',
				Pins('E11', dir = 'o')
			),
			Subsignal('atn',
				Pins('H11', dir = 'o')
			),

			Attrs(IO_STANDARD = 'SB_LVCMOS')
		),

		Resource('scsi_tx_ctl', 0,
			Subsignal('tp_en_n',
				Pins('A1', dir = 'o')
			),
			Subsignal('tx_en_n',
				Pins('K11', dir = 'o')
			),
			Subsignal('aa_en_n',
				Pins('G8', dir = 'o')
			),
			Subsignal('bsy_en_n',
				Pins('G9', dir = 'o')
			),
			Subsignal('sel_en_n',
				Pins('F9', dir = 'o')
			),
			Subsignal('mr_en_n',
				Pins('E8', dir = 'o')
			),

			Attrs(IO_STANDARD = 'SB_LVCMOS')
		),

		Resource('scsi_ctl', 0,
			Subsignal('diff_sense',
				PinsN('D7', dir = 'i')
			),
			Attrs(IO_STANDARD = 'SB_LVCMOS')
		),

		*LEDResources(
			pins = [
				'L1', # [0] BLUE
				'L2', # [1] PINK
				'K3', # [2] WHITE
				'L3', # [3] PINK
				'K4'  # [4] BLUE
			],
			attrs = Attrs(IO_STANDARD = 'SB_LVCMOS'),
		),

		*SPIFlashResources(0,
			cs_n = 'K10', clk = 'L10', copi = 'K9', cipo = 'J9',

			attrs = Attrs(IO_STANDARD = 'SB_LVCMOS')
		),

		UARTResource(0,
			rx = 'L7', tx = 'K7',
			attrs = Attrs(IO_STANDARD = 'SB_LVCMOS')
		),
	]

	connectors = []




AVAILABLE_PLATFORMS = {
	'rev1': Rev1,
}
