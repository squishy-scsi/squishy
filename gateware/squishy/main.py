# SPDX-License-Identifier: BSD-3-Clause
from nmigen import *

from .leds import LEDInterface
from .uart import UARTInterface
from .scsi import SCSIInterface
from .usb  import USBInterface
from .spi  import SPIInterface

__all__ = ('Squishy')

class Squishy(Elaboratable):
	def __init__(self, *, uart_config, usb_config, scsi_config):
		# PHY Options
		self.uart_config = uart_config
		self.usb_config  = usb_config
		self.scsi_config = scsi_config

		# Module References
		self.leds = LEDInterface()
		self.spi  = SPIInterface()
		if self.uart_config['enabled']:
			self.uart = UARTInterface(config = self.uart_config)
		else:
			self.uart = None
		self.scsi = SCSIInterface(config = self.scsi_config)
		self.usb  = USBInterface(config = self.usb_config)

	def elaborate(self, platform):
		m = Module()

		m.submodules.leds = self.leds
		if self.uart is not None:
			m.submodules.uart = self.uart

		m.submodules.scsi = self.scsi
		m.submodules.usb  = self.usb
		m.submodules.spi  = self.spi

		return m
