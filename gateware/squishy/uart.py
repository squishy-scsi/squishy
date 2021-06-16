# SPDX-License-Identifier: BSD-3-Clause
from nmigen import Elaboratable, Module, Signal


class UARTDevice(Elaboratable):
	def __init__(self):
		self.activity_tx = Signal()
		self.activity_rx = Signal()

	def elaborate(self, platform):
		m = Module()

		uart_fifo = platform.request('uart_fifo')

		return m
