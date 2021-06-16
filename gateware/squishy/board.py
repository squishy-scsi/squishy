# SPDX-License-Identifier: BSD-3-Clause
from nmigen.build import *
from nmigen.vendor.lattice_ice40 import *
from nmigen_boards.resources.memory import SPIFlashResources

__all__ = ('Rev1')

class Rev1(LatticeICE40Platform):
	device      = 'iCE40HX8K'
	package     = 'BG121'
	default_clk = 'clk'
	toolchain   = 'Trellis'

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
				Pins('E1 E2 F1 F2 H1 H2 J1 J2', dir = 'io')
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
			Subsignal('tp_en',
				Pins('A1', dir = 'o')
			),
			Subsignal('tx_en',
				Pins('K11', dir = 'o')
			),
			Subsignal('aa_en',
				Pins('G8', dir = 'o')
			),
			Subsignal('bsy_en',
				Pins('G9', dir = 'o')
			),
			Subsignal('sel_en',
				Pins('F9', dir = 'o')
			),
			Subsignal('mr_en',
				Pins('E8', dir = 'o')
			),

			Attrs(IO_STANDARD = 'SB_LVCMOS')
		),

		Resource('leds', 0,
			Subsignal('led_1',
				Pins('L1', dir = 'o')
			),
			Subsignal('led_2',
				Pins('L2', dir = 'o')
			),
			Subsignal('led_3',
				Pins('K3', dir = 'o')
			),
			Subsignal('led_4',
				Pins('L3', dir = 'o')
			),
			Subsignal('led_5',
				Pins('K4', dir = 'o')
			),

			Attrs(IO_STANDARD = 'SB_LVCMOS')
		),

		*SPIFlashResources(0,
			cs_n = 'K10', clk = 'L10', copi = 'K9', cipo = 'J9',

			attrs = Attrs(IO_STANDARD="SB_LVCMOS")
		)
	]

	connectors = []
