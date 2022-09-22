# SPDX-License-Identifier: BSD-3-Clause

from abc                                import (
	ABCMeta, abstractmethod
)
from typing                             import (
	Optional, List, Any, Type
)

from amaranth                           import (
	Elaboratable, Module
)
from luna.gateware.usb.usb2.request     import (
	USBRequestHandler
)

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

class AppletElaboratable(Elaboratable, metaclass = ABCMeta):
	def __init__(self, ) -> None:
		super().__init__()

	@property
	def scsi_request_handlers(self) -> Optional[List[Any]]:
		return None

	@property
	def usb_request_handlers(self) -> Optional[List[USBRequestHandler]]:
		return None

	@property
	def scsi_version(self) -> int:
		return 1

	@classmethod
	def usb_init_descriptors(cls: Type['AppletElaboratable'], dev_desc) -> None:
		'''  '''
		return 0


	@abstractmethod
	def elaborate(self, platform) -> Module:
		''' '''
		raise NotImplementedError('Applet Elaboratables must implement this method')



class Squishy(Elaboratable):
	def _rev1_init(self):
		self.usb = Rev1USB(
			config              = self.usb_config,
			applet_desc_builder = self.applet.usb_init_descriptors
		)

	def _rev2_init(self):
		pass

	def __init__(self, *, revision: int,
		uart_config, usb_config, scsi_config,
		applet: AppletElaboratable
	):
		# Applet
		self.applet = applet

		# PHY Options
		self.uart_config = uart_config
		self.usb_config  = usb_config
		self.scsi_config = scsi_config

		{
			1: self._rev1_init,
			2: self._rev2_init
		}.get(revision)()


	def elaborate(self, platform):
		m = Module()

		m.submodules.pll = platform.clock_domain_generator()
		m.submodules.usb = self.usb

		m.submodules.applet = self.applet

		return m
