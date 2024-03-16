# SPDX-License-Identifier: BSD-3-Clause

from abc       import ABCMeta, abstractmethod
from torii     import Elaboratable

from .mixins   import SquishyCacheMixin

from ...config import USB_VID, USB_PID_APPLICATION, USB_PID_BOOTLOADER
from ...config import USB_MANUFACTURER, USB_PRODUCT
from ...config import SCSI_VID

__all__ = (
	'SquishyPlatform'
)

class SquishyPlatform(SquishyCacheMixin, metaclass = ABCMeta):
	'''
	Squishy Base Platform

	This is a base platform for Squishy hardware designs. It is built to abstract away a chunk of
	the things that would be constantly repeated for new Squishy platforms and variants.

	The primary things that are here are as follows:
		* ``usb_vid`` - The USB Vendor ID
		* ``usb_pid_app`` - The USB PID for the main gateware
		* ``usb_pid_boot`` - This USB PID for the bootloader
		* ``usb_mfr`` - The USB Manufacturer string
		* ``usb_prod`` - The USB PID to string mapping
		* ``scsi_vid`` - The default SCSI Vendor ID

	The things that the platforms are expected to provide are as follows:
		* ``revision`` - The platform revision
		* ``clock_domain_generator`` - The Torii Elaboratable PLL/Clock Domain generator for this Squishy platform
		* ``pll_config`` - The PLL configuration for the ``clock_domain_generator``

	Platforms are also still required to inherit from the appropriate :py:mod:`torii.vendor.platform`
	in order to properly be used.

	'''

	@property
	def usb_vid(self) -> int:
		''' The USB Vendor ID used for Squishy endpoints '''
		return USB_VID

	@property
	def usb_pid_app(self) -> int:
		''' The USB PID for the main Squishy gateware '''
		return USB_PID_APPLICATION

	@property
	def usb_pid_boot(self) -> int:
		''' The USB VID for the Squishy bootloader '''
		return USB_PID_BOOTLOADER

	@property
	def usb_mfr(self) -> str:
		''' The USB Manufacturer string '''
		return USB_MANUFACTURER

	@property
	def usb_prod(self) -> dict[int, str]:
		''' The USB VID to USB Product string mapping '''
		return USB_PRODUCT

	@property
	def scsi_vid(self) -> str:
		''' The SCSI Vendor ID '''
		return SCSI_VID

	@property
	@abstractmethod
	def revision(self) -> float:
		''' The hardware platform revision '''
		raise NotImplementedError('SquishyPlatform requires a revision to be set')

	@property
	@abstractmethod
	def clock_domain_generator(self) -> Elaboratable:
		''' The Torii Elaboratable that is the PLL/Clock Domain generator for this Squishy platform '''
		raise NotImplementedError('SquishyPlatform requires a clock domain generator to be set')

	@property
	@abstractmethod
	def pll_config(self) -> dict[str, int]:
		''' The PLL configuration for the given clock_domain_generator '''
		raise NotImplementedError('SquishyPlatform requires a pll config to be set')
