# SPDX-License-Identifier: BSD-3-Clause
from nmigen import *
from nmigen_stdio.serial import AsyncSerial

from .usb import USBInterface
from .scsi import SCSIInterface

__all__ = ('Squishy')

class Squishy(Elaboratable):
	def __init__(self, *, uart_config, usb_config, scsi_config):
		# PHY Options
		self.uart_config = uart_config
		self.usb_config  = usb_config
		self.scsi_config = scsi_config

		# Module References
		self.uart = None
		self.scsi = None
		self.usb  = None

	def elaborate(self, platform):
		if self.uart_config['enabled']:
			self.uart = AsyncSerial(
				# TODO: Figure out how to extract the global clock freq and stuff it into the divisor calc
				divisor      = int(48e6 // self.uart_config['baud']),
				divisor_bits = None, # Will force use of `bits_for(divisor)`,
				data_bits    = self.uart_config['data_bits'],
				parity       = self.uart_config['parity'],
				pins         = platform.request('uart')
			)

		self.scsi = SCSIInterface(config = self.scsi_config)
		self.usb  = USBInterface(config = self.usb_config)

		m = Module()

		if self.uart_config['enabled']:
			m.submodules.uart = self.uart

		m.submodules.scsi = self.scsi
		m.submodules.usb  = self.usb

		leds = platform.request('leds')

		m.d.comb += [
			leds.led_1.eq(self.scsi.activity),
			leds.led_2.eq(self.usb.activity)
		]

		return m
