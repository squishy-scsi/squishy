# SPDX-License-Identifier: BSD-3-Clause
from nmigen import *
from nmigen_stdio.serial import AsyncSerial


from .usb import USBInterface
from .scsi import SCSIInterface

class Squishy(Elaboratable):
	def __init__(self, *,
		enable_uart = True,
		uart_baud   = 9600,
		uart_parity = 'none',
		uart_data   = 8,

		vid = 0xFEED,
		pid = 0xACA7,

		manufacturer  = 'aki-nyan',
		product       = 'squishy',
		serial_number = 'ニャ〜'
	):
		# Debug UART
		self.enable_uart = enable_uart
		self.uart_baud   = uart_baud
		self.uart_parity = uart_parity
		self.uart_data   = uart_data

		# USB
		self.vid = vid
		self.pid = pid

		self.manufacturer  = manufacturer
		self.product       = product
		self.serial_number = serial_number

		# Module References
		self.uart = None
		self.scsi = None
		self.usb  = None

	def elaborate(self, platform):
		if self.enable_uart:
			self.uart = AsyncSerial(
				# TODO: Figure out how to extract the global clock freq and stuff it into the divisor calc
				divisor      = int(48e6 // self.uart_baud),
				divisor_bits = None, # Will force use of `bits_for(divisor)`,
				data_bits    = self.uart_data,
				parity       = self.uart_parity,
				pins         = platform.request('uart')
			)

		self.scsi = SCSIInterface(
			rx     = platform.request('scsi_rx'),
			tx     = platform.request('scsi_tx'),
			tx_ctl = platform.request('scsi_tx_ctl')
		)

		self.usb  = USBInterface(
			vid = self.vid,
			pid = self.pid,

			manufacturer  = self.manufacturer,
			product       = self.product,
			serial_number = self.product
		)


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
