# SPDX-License-Identifier: BSD-3-Clause
from nmigen import *
from nmigen_stdio.serial import AsyncSerial


from .usb import USBDevice
from .scsi import SCSIInterface

class Squishy(Elaboratable):
	def __init__(self, *, uart_baud = 9600):
		self.uart_baud = uart_baud
		self.uart = None
		self.scsi = None
		self.usb  = None

	def elaborate(self, platform):
		self.uart = AsyncSerial(divisor = int(45e6 // self.uart_baud))
		self.scsi = SCSIInterface(
			rx     = platform.request('scsi_rx'),
			tx     = platform.request('scsi_tx'),
			tx_ctl = platform.request('scsi_tx_ctl')
		)
		self.usb  = USBDevice()


		m = Module()

		clk = platform.request('clk')
		m.domains.sync = ClockDomain()
		m.d.comb += ClockSignal().eq(clk.i)

		m.submodules.uart = self.uart
		m.submodules.scsi = self.scsi
		m.submodules.usb  = self.usb

		leds = platform.request('leds')

		m.d.comb += [
			leds.led_1.eq(self.scsi.activity)
		]

		return m
