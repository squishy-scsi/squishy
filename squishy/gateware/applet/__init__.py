# SPDX-License-Identifier: BSD-3-Clause

'''

'''

from abc                                         import ABCMeta, abstractmethod
from typing                                      import Self

from torii.hdl                                   import Elaboratable, Module

# TODO(aki): USB3 bits for rev2+ (eventually)
from sol_usb.gateware.usb.usb2.request           import USBRequestHandler

from usb_construct.emitters.descriptors.standard import DeviceDescriptorCollection

from ..platform                                  import SquishyPlatformType

__all__ = (
	'AppletElaboratable',
)

class AppletElaboratable(Elaboratable, metaclass = ABCMeta):
	'''
	Squishy Applet gateware interface.

	This is the base class for the gateware for Squishy applets. It provides
	a common consumable API that allows the Squishy gateware superstructure to
	interface with the applet core.

	Attributes
	----------

	usb_request_handlers : list[USBRequestHandler] | None
		Any additional USB request handlers to register.

	'''

	def __init__(self) -> None:
		super().__init__()


	@property
	def usb_request_handlers(self) -> list[USBRequestHandler] | None:
		''' Returns a list of USB request handlers '''
		return None


	@classmethod
	def usb_init_descriptors(cls: Self, desc_collection: DeviceDescriptorCollection) -> int:
		''' Initialize USB descriptors'''
		return 0


	@abstractmethod
	def elaborate(self, platform: SquishyPlatformType) -> Module:
		''' Gateware elaboration '''
		raise NotImplementedError('Applet Elaboratables must implement this method')
