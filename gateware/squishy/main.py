# SPDX-License-Identifier: BSD-3-Clause
from nmigen              import *
from nmigen_soc.wishbone import Decoder, Arbiter

from .leds import LEDInterface
from .uart import UARTInterface
from .scsi import SCSIInterface
from .usb  import USBInterface
from .spi  import SPIInterface

__all__ = ('Squishy')

"""
	Squishy Architecture

               ┌──────────┐
      ┌────────►RAM BUFFER◄───────┐
      │        └──────────┘       │
  ┌───▼───┐                  ┌────▼───┐
┌─┤USB PHY◄─────────┬────────►SCSI PHY│
│ └─┬──▲──┘         │        └───┬────┘
│   │  │            │            │
│   │  │            │            │
│ ┌─▼──┴──┐   ┌─────▼───────┐    │
├─┤SPI PHY│   │BUS INITIATOR│    │
│ └───────┘   └────┬──▲───┬─┘    │
│                  │  │   │      │
└───────────┐      │  │   │      │
            │     ┌▼──┴┐  │    ┌─▼──┐
            │     │UART├──┴────►LEDS│
            │     └────┘       └▲───┘
            │                   │
            └───────────────────┘

"""

class Squishy(Elaboratable):
	def __init__(self, *, uart_config, usb_config, scsi_config):
		# PHY Options
		self.uart_config = uart_config
		self.usb_config  = usb_config
		self.scsi_config = scsi_config

		# Wishbone bus stuff
		self._wb_cfg = {
			'addr': 8,	# Address width
			'data': 8,	# Data Width
			'gran': 8,	# Bus Granularity
			'feat': {	# Bus Features
				'cti', 'bte'
			}
		}

		self._wb_arbiter = Arbiter(
			addr_width  = self._wb_cfg['addr'],
			data_width  = self._wb_cfg['data'],
			granularity = self._wb_cfg['gran'],
			features    = self._wb_cfg['feat']
		)

		self._wb_decoder = Decoder(
			addr_width  = self._wb_cfg['addr'],
			data_width  = self._wb_cfg['data'],
			granularity = self._wb_cfg['gran'],
			features    = self._wb_cfg['feat']
		)

		# Module References
		self.leds = LEDInterface()
		self.spi  = SPIInterface()
		if self.uart_config['enabled']:
			self.uart = UARTInterface(
				config  = self.uart_config,
				ctl_bus = self._wb_decoder.bus
			)

		else:
			self.uart = None
		self.scsi = SCSIInterface(
			config    = self.scsi_config,
			wb_config = self._wb_cfg
		)

		self.usb  = USBInterface(
			config    = self.usb_config,
			wb_config = self._wb_cfg
		)


	def elaborate(self, platform):
		m = Module()

		# Wishbone stuff
		m.submodules.arbiter = self._wb_arbiter
		m.submodules.decoder = self._wb_decoder

		m.submodules.leds = self.leds
		if self.uart is not None:
			m.submodules.uart = self.uart

		m.submodules.scsi = self.scsi
		m.submodules.usb  = self.usb
		m.submodules.spi  = self.spi

		m.d.comb += [
			self._wb_arbiter.bus.connect(self._wb_decoder.bus)
		]

		return m
