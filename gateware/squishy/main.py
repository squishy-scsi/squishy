# SPDX-License-Identifier: BSD-3-Clause
from nmigen import *
from nmigen_stdio.serial import AsyncSerial


from .usb import USBInterface
from .scsi import SCSIInterface

class Squishy(Elaboratable):
	def __init__(self, *,
		uart_baud = 9600 , enable_uart = True,

		vid = 0xFEED, pid = 0xACA7
	):
		# Debug UART
		self.uart_baud   = uart_baud
		self.enable_uart = enable_uart
		# USB
		self.vid = vid
		self.pid = pid

		self.uart = None
		self.scsi = None
		self.usb  = None

	def elaborate(self, platform):
		if self.enable_uart:
			self.uart = AsyncSerial(
				divisor      = int(48e6 // self.uart_baud),
				divisor_bits = None, # Will force use of `bits_for(divisor)`,
				data_bits    = 8,
				parity       = 'none',
				pins         = platform.request('uart')
			)

		self.scsi = SCSIInterface(
			rx     = platform.request('scsi_rx'),
			tx     = platform.request('scsi_tx'),
			tx_ctl = platform.request('scsi_tx_ctl')
		)
		self.usb  = USBInterface(vid = self.vid, pid = self.pid)


		m = Module()

		if self.enable_uart:
			m.submodules.uart = self.uart

		m.submodules.scsi = self.scsi
		m.submodules.usb  = self.usb

		leds = platform.request('leds')

		m.d.comb += [
			leds.led_1.eq(self.scsi.activity),
			leds.led_2.eq(self.usb.activity)
		]

		return m
