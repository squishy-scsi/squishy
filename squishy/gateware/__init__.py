# SPDX-License-Identifier: BSD-3-Clause

from typing import (
	Optional, Dict, Any,
)

import logging as log

from amaranth import (
	Elaboratable, Module
)

from .applet import AppletElaboratable


from .usb import (
	Rev1USB, Rev2USB
)

from .scsi import (
	SCSI1Device, SCSI1Initiator,
	SCSI2Device, SCSI2Initiator,
	SCSI3Device, SCSI3Initiator
)

__all__ = (
	'AppletElaboratable',
	'Squishy',
)

__doc__ = '''\

.. todo: Refine this section

The Squishy gateware library is broken into three main parts. The first is the
:py:mod:`squishy.gateware.core` module, this contains all of the core infra for
Squishy. Next is the :py:mod:`squishy.gateware.platform` module, this contains
the Amaranth platform definitions for various bits of Squishy hardware.
Finally there is the :py:mod:`squishy.gateware.scsi` module, this is where all
of the SCSI machinery is for use in Amaranth HDL projects.

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
		self.usb = Rev1USB(
			config              = self.usb_config,
			applet_desc_builder = self.applet.usb_init_descriptors
		)
		# SCSI
		self.scsi = ({
			1: SCSI1Device,
			2: SCSI2Device,
			3: SCSI3Device,
		}.get(self.applet.scsi_version))(config = self.scsi_config)

	def _rev2_init(self) -> None:
		log.warning('Rev2 Gateware is unimplemented')

	def __init__(self, *, revision: int,
		uart_config: Dict[str, Any],
		usb_config: Dict[str, Any],
		scsi_config: Dict[str, Any],
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


	def elaborate(self, platform: Optional[Any]) -> Module:
		m = Module()

		# Setup Submodules
		m.submodules.pll    = platform.clock_domain_generator()
		m.submodules.usb    = self.usb
		m.submodules.scsi   = self.scsi
		m.submodules.applet = self.applet

		return m
