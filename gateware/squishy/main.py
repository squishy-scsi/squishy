# SPDX-License-Identifier: BSD-3-Clause
from nmigen import *

from .uart import UARTDevice
from .scsi import SCSIInterface

class SquishyTop(Elaboratable):
	def elaborate(self, platform):
		m = Module()

		clk = platform.request('clk')
		m.domains.sync = ClockDomain()
		m.d.comb += ClockSignal().eq(clk.i)

		m.submodules.scsi = scsi = SCSIInterface()
		m.submodules.uart = uart = UARTDevice()

		leds = platform.request('leds')

		m.d.comb += [
			leds.led0.o.eq(scsi.activity_tx),
			leds.led1.o.eq(scsi.activity_rx),

			leds.led3.o.eq(uart.activity_tx),
			leds.led4.o.eq(uart.activity_rx),
		]

		return m
