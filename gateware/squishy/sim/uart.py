# SPDX-License-Identifier: BSD-3-Clause
from nmigen                import *
from nmigen.sim            import Simulator, Settle
from nmigen.hdl.ir         import Fragment
from nmigen.hdl            import Record

from .                     import sim_case
from ..core.interface.uart import UARTInterface

SIM_NAME = 'UART'

class DummyPlatform():
	pll_config = {
		'freq': 1e8,
	}

	def request(self, name, num = 0):
		if name == 'led':
			return Signal(name = f'led_{num}')
		if name == 'uart':
			return Record([
				('rx', Record([
					('i', 1),
					('o', 1)
				])),
				('tx', Record([
					('i', 1),
					('o', 1)
				]))
			])

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

uart = Fragment.get(
	UARTInterface(config = _uart_config, wb_config = _wb_cfg),
	platform = DummyPlatform()
)

@sim_case(domains = [ ('sync', 1e8) ], dut = uart)
def sim_uart(sim, dut):


	return [
		()
	]

SIM_CASES = [
	sim_uart,
]
