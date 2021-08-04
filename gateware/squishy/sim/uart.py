# SPDX-License-Identifier: BSD-3-Clause
from nmigen                import *
from nmigen.sim            import Simulator, Settle

from .                     import sim_case, SimPlatform
from ..core.interface.uart import UARTInterface

SIM_NAME = 'UART'

_uart_config = {
	'enabled'  : True,
	'baud'     : 9600,
	'parity'   : 'none',
	'data_bits': 8,
}

_wb_cfg = {
	'addr': 8,	# Address width
	'data': 8,	# Data Width
	'gran': 8,	# Bus Granularity
	'feat': {	# Bus Features
		'cti', 'bte'
	}
}

uart = UARTInterface(
			config    = _uart_config,
			wb_config = _wb_cfg
		)

@sim_case(domains = [ ('sync', 1e8) ], dut = uart, platform = SimPlatform())
def sim_uart(sim, dut):
	def nya():
		from random import randint
		yield Settle()
		for _ in range(1024):
			yield
			yield
			yield dut._uart.rx.data.eq(randint(0,255))

	return [
		(nya, 'sync')
	]

SIM_CASES = [
	sim_uart,
]
