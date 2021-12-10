# SPDX-License-Identifier: BSD-3-Clause
from amaranth              import *
from amaranth.lib.fifo     import AsyncFIFO
from amaranth_stdio.serial import AsyncSerial
from amaranth_soc.wishbone import Interface


__all__ = (
	'UARTInterface',
)

class UARTInterface(Elaboratable):
	def __init__(self, *, config, wb_config):
		self.config = config
		self._wb_cfg = wb_config

		self.ctl_bus = Interface(
			addr_width  = self._wb_cfg['addr'],
			data_width  = self._wb_cfg['data'],
			granularity = self._wb_cfg['gran'],
			features    = self._wb_cfg['feat']
		)

		self._status_led = None

		self._output_fifo = AsyncFIFO(
			width    = 8,
			depth    = 128,
			r_domain = 'sync',
			w_domain = 'sync',
		)

		self._uart = None

	def elaborate(self, platform):
		self._status_led = platform.request('led', 0)

		self._uart = AsyncSerial(
			# TODO: Figure out how to extract the global clock freq and stuff it into the divisor calc
			divisor      = int(platform.pll_config['freq'] // self.config['baud']),
			divisor_bits = None, # Will force use of `bits_for(divisor)`,
			data_bits    = self.config['data_bits'],
			parity       = self.config['parity'],
			pins         = platform.request('uart')
		)

		m = Module()

		uart_in  = Signal(self.config['data_bits'])
		uart_out = Signal(self.config['data_bits'])

		m.submodules += self._uart, self._output_fifo

		m.d.comb += [
			self._uart.rx.ack.eq(0)
		]

		# TODO: Handle commands w/ more than one byte

		with m.FSM(reset = 'idle'):
			with m.State('idle'):
				m.d.sync += self._status_led.eq(0)

				with m.If(self._uart.rx.rdy):
					m.d.sync += [
						uart_in.eq(self._uart.rx.data),
						self._status_led.eq(1)
					]

					m.next = 'uart_ack'

			with m.State('uart_ack'):
				m.d.comb += self._uart.rx.ack.eq(1)
				m.next = 'cmd_proc'

			with m.State('cmd_proc'):
				with m.Switch(uart_in):
					with m.Case(0x00):
						pass
					with m.Default():
						m.next = 'idle'



			with m.State('data_write'):

				m.next = 'idle'


			m.d.sync += [
				self._output_fifo.r_en.eq(self._uart.tx.rdy),
				self._uart.tx.data.eq(self._output_fifo.r_data),
				self._uart.tx.ack.eq(self._output_fifo.r_rdy),
			]

		return m
