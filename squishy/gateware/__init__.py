# SPDX-License-Identifier: BSD-3-Clause

from typing             import Any
import logging          as log

from torii              import Elaboratable, Module

from .applet            import AppletElaboratable
from .usb               import Rev1USB, Rev2USB
from .scsi              import SCSI1, SCSI2, SCSI3
from .platform.platform import SquishyPlatform

__all__ = (
	'AppletElaboratable',
	'SquishyPlatform',
	'Squishy',
)

__doc__ = '''\

.. todo: Refine this section

The Squishy gateware library is broken into three main parts. The first is the
:py:mod:`squishy.gateware.core` module, this contains all of the core infra for
Squishy. Next is the :py:mod:`squishy.gateware.platform` module, this contains
the torii platform definitions for various bits of Squishy hardware.
Finally there is the :py:mod:`squishy.gateware.scsi` module, this is where all
of the SCSI machinery is for use in torii HDL projects.

'''

'''
	Squishy Architecture

               ┌──────────┐
      ┌────────►RAM BUFFER◄───────┐
      │        └────▲─────┘       │
  ┌───▼───┐    ┌────▼─────┐  ┌────▼───┐
┌─┤USB PHY◄────►  APPLET  ◄──►SCSI PHY│
│ └───────┘    └▲───▲───┬─┘  └───┬────┘
│       ┌───────┘   │   └────────┤
│       │           │            │
│ ┌─────▼─┐     ┌───▼──┐       ┌─▼──┐
├─┤SPI PHY│     │ UART ├───────►LEDS│
│ └───────┘     └──────┘       └─▲──┘
│                                │
└────────────────────────────────┘

''' # noqa: E101

class Squishy(Elaboratable):
	def _rev1_init(self) -> None:
		# USB
		# Re-work so the USB device is passed into the applet
		# to collect endpoints
		self.usb = Rev1USB(
			config              = self.usb_config,
			applet_desc_builder = self.applet.usb_init_descriptors
		)
		# SCSI
		if self.applet.scsi_version < 1:
			raise ValueError('Squishy rev1 can only talk to SCSI-1 buses')

		self.scsi = SCSI1(config = self.scsi_config)

	def _rev2_init(self) -> None:
		log.warning('Rev2 Gateware is unimplemented')

	def __init__(self, *, revision: int,
		uart_config: dict[str, Any],
		usb_config: dict[str, Any],
		scsi_config: dict[str, Any],
		applet: AppletElaboratable
	) -> None:
		# Applet
		self.applet = applet

		# PHY Options
		self.uart_config = uart_config
		self.usb_config  = usb_config
		self.scsi_config = scsi_config

		{
			1: self._rev1_init,
			2: self._rev2_init
		}.get(revision, lambda s: None)()


	def elaborate(self, platform: SquishyPlatform | None) -> Module:
		m = Module()

		# Setup Submodules
		m.submodules.pll    = platform.clock_domain_generator()
		m.submodules.usb    = self.usb
		m.submodules.scsi   = self.scsi
		m.submodules.applet = self.applet

		return m
