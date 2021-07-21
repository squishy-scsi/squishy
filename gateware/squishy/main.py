# SPDX-License-Identifier: BSD-3-Clause
from nmigen import *

from .usb import USBInterface
from .scsi import SCSIInterface
from .uart import UARTInterface

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
		# Pull in the individual components
		if self.uart_config['enabled']:
			self.uart = UARTInterface(config = self.uart_config)
		self.scsi = SCSIInterface(config = self.scsi_config)
		self.usb  = USBInterface(config = self.usb_config)

		m = Module()

		if self.uart is not None:
			m.submodules.uart = self.uart

		m.submodules.scsi = self.scsi
		m.submodules.usb  = self.usb

		leds = platform.request('leds')

		m.d.comb += [
			leds.led_1.eq(self.scsi.activity),
			leds.led_2.eq(self.usb.activity)
		]

		return m
