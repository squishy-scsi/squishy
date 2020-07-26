# SPDX-License-Identifier: BSD-3-Clause
from nmigen.build import *
from nmigen.vendor.lattice_ice40 import *

__all__ = ['Rev0']

class Rev0(LatticeICE40Platform):
	device      = 'iCE40HX8K'
	package     = 'bg121'
	default_clk = 'clk'
	toolchain   = 'Trellis'

	resources = [
		Resource('clk', 0,
			Pins('F3', dir='i'),
			Clock(48000000),
			Attrs(GLOBAL=True, IO_STANDARD='LVCMOS33')
		),

		Resource('uart_fifo', 0,
			# FTDI FIFO data bus
			Subsignal('d0', Pins('E1', dir='io')),
			Subsignal('d1', Pins('D2', dir='io')),
			Subsignal('d2', Pins('D1', dir='io')),
			Subsignal('d3', Pins('B2', dir='io')),
			Subsignal('d4', Pins('E2', dir='io')),
			Subsignal('d5', Pins('C2', dir='io')),
			Subsignal('d6', Pins('B1', dir='io')),
			Subsignal('d7', Pins('C1', dir='io')),

			# FTDI FIFO Control lines
			Subsignal('siwu', Pins('F2', dir='o')),
			Subsignal('rd',   Pins('F1', dir='o')),
			Subsignal('wr',   Pins('G2', dir='o')),
			Subsignal('txe',  Pins('H2', dir='i')),
			Subsignal('rxf',  Pins('G1', dir='i')),

			Attrs(IO_STANDARD='LVCMOS33'),
		),

		Resource('scsi', 0,
			Subsignal('db0_tx',  Pins('A2',  dir='o')),
			Subsignal('db0_rx',  Pins('C3',  dir='i')),

			Subsignal('db1_tx',  Pins('B4',  dir='o')),
			Subsignal('db1_rx',  Pins('A3',  dir='i')),

			Subsignal('db2_tx',  Pins('B6',  dir='o')),
			Subsignal('db2_rx',  Pins('A5',  dir='i')),

			Subsignal('db3_tx',  Pins('A7',  dir='o')),
			Subsignal('db3_rx',  Pins('C7',  dir='i')),

			Subsignal('db4_tx',  Pins('C9',  dir='o')),
			Subsignal('db4_rx',  Pins('A8',  dir='i')),

			Subsignal('db5_tx',  Pins('C11', dir='o')),
			Subsignal('db5_rx',  Pins('D9',  dir='i')),

			Subsignal('db6_tx',  Pins('F9',  dir='o')),
			Subsignal('db6_rx',  Pins('D10', dir='i')),

			Subsignal('db7_tx',  Pins('F10', dir='o')),
			Subsignal('db7_rx',  Pins('F11', dir='i')),

			Subsignal('dbp_tx',  Pins('H10', dir='o')),
			Subsignal('dbp_rx',  Pins('H11', dir='i')),

			Subsignal('atn_tx',  Pins('B3',  dir='o')),
			Subsignal('atn_rx',  Pins('C4',  dir='i')),

			Subsignal('bsy_tx',  Pins('B5',  dir='o')),
			Subsignal('bsy_rx',  Pins('D5',  dir='i')),

			Subsignal('ack_tx',  Pins('B7',  dir='o')),
			Subsignal('ack_rx',  Pins('A6',  dir='i')),

			Subsignal('rst_tx',  Pins('B8',  dir='o')),
			Subsignal('rst_rx',  Pins('C8',  dir='i')),

			Subsignal('msg_tx',  Pins('B11', dir='o')),
			Subsignal('msg_rx',  Pins('A10', dir='i')),

			Subsignal('sel_tx',  Pins('E9',  dir='o')),
			Subsignal('sel_rx',  Pins('E8',  dir='i')),

			Subsignal('cd_tx',   Pins('E10',  dir='o')),
			Subsignal('cd_rx',   Pins('E11',  dir='i')),

			Subsignal('req_tx',  Pins('G10', dir='o')),
			Subsignal('req_rx',  Pins('G11', dir='i')),

			Subsignal('io_tx',   Pins('J10', dir='o')),
			Subsignal('io_rx',   Pins('J11', dir='i')),

			Subsignal('bnk0_oe', Pins('A1',  dir='o')),
			Subsignal('bnk1_oe', Pins('A4',  dir='o')),
			Subsignal('bnk2_oe', Pins('D7',  dir='o')),
			Subsignal('bnk3_oe', Pins('A11', dir='o')),
			Subsignal('bnk4_oe', Pins('D11', dir='o')),
			Subsignal('bnk5_oe', Pins('G9',  dir='o')),

			Attrs(IO_STANDARD='LVCMOS33'),
		),

		Resource('leds', 0,
			Subsignal('led0', Pins('H1', dir='o')),
			Subsignal('led1', Pins('J1', dir='o')),
			Subsignal('led2', Pins('K1', dir='o')),
			Subsignal('led3', Pins('L1', dir='o')),
			Subsignal('led4', Pins('L2', dir='o')),

			Attrs(IO_STANDARD='LVCMOS33')
		)
	]

	connectors = []
