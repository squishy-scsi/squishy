# SPDX-License-Identifier: BSD-3-Clause

__all__ = (
	'Squishy',
)

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

from nmigen              import *
from nmigen.lib.fifo     import AsyncFIFO
from nmigen_soc.wishbone import Decoder, Arbiter

from .interface import UARTInterface
from .interface import SCSIInterface
from .interface import USBInterface
from .interface import SPIInterface



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
		self.spi  = SPIInterface()
		if self.uart_config['enabled']:
			self.uart = UARTInterface(
				config    = self.uart_config,
				wb_config = self._wb_cfg
			)
			self._wb_arbiter.add(self.uart.ctl_bus)

		else:
			self.uart = None
		self.scsi = SCSIInterface(
			config    = self.scsi_config,
			wb_config = self._wb_cfg
		)
		self._wb_decoder.add(self.scsi.bus, addr = 0)
		self._wb_arbiter.add(self.scsi.ctl_bus)

		self.usb  = USBInterface(
			config    = self.usb_config,
			wb_config = self._wb_cfg
		)
		self._wb_decoder.add(self.usb.bus, addr = 16)
		self._wb_arbiter.add(self.usb.ctl_bus)

		self._fifo_cfg = {
			'width': 8,
			'depth': 1024,
		}

		self._scsi_in_fifo = AsyncFIFO(
			width = self._fifo_cfg['width'],
			depth = self._fifo_cfg['depth'],
			r_domain = 'sync',
			w_domain = 'usb'
		)

		self._usb_in_fifo = AsyncFIFO(
			width = self._fifo_cfg['width'],
			depth = self._fifo_cfg['depth'],
			r_domain = 'usb',
			w_domain = 'sync'
		)

		self._status_led = None

	def elaborate(self, platform):
		self._status_led = platform.request('led', 4)
		m = Module()

		m.submodules.nya = platform.clock_domain_generator(
			pll_cfg = platform.pll_config
		)

		# Wishbone stuff
		m.submodules.arbiter = self._wb_arbiter
		m.submodules.decoder = self._wb_decoder

		if self.uart is not None:
			m.submodules.uart = self.uart

		# USB <-> SCSI FIFOs
		m.submodules += self._usb_in_fifo, self._scsi_in_fifo

		self.usb.connect_fifo(
			usb_in   = self._usb_in_fifo,
			scsi_out = self._scsi_in_fifo
		)

		self.scsi.connect_fifo(
			scsi_in = self._scsi_in_fifo,
			usb_out = self._usb_in_fifo
		)


		m.submodules.scsi = self.scsi
		m.submodules.usb  = self.usb
		m.submodules.spi  = self.spi

		m.d.comb += [
			self._wb_arbiter.bus.connect(self._wb_decoder.bus)
		]

		return m
