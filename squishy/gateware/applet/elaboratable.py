# SPDX-License-Identifier: BSD-3-Clause
from abc                                         import ABCMeta, abstractmethod
from typing                                      import Any, Type

from torii                                       import Elaboratable, Module

from sol_usb.gateware.usb.usb2.request           import USBRequestHandler

from usb_construct.emitters.descriptors.standard import DeviceDescriptorCollection

from ..platform.platform                         import SquishyPlatform

__all__ = (
	'AppletElaboratable',
)

__doc__ = '''\

'''

class AppletElaboratable(Elaboratable, metaclass = ABCMeta):
	'''  '''

	def __init__(self) -> None:
		super().__init__()

	@property
	def scsi_request_handlers(self) -> list[Any] | None:
		''' Returns a list of SCSI request handlers '''
		return None

	@property
	def usb_request_handlers(self) -> list[USBRequestHandler] | None:
		''' Returns a list of USB request handlers '''
		return None

	@property
	def scsi_version(self) -> int:
		''' Returns the SCSI Version'''
		return 1

	@classmethod
	def usb_init_descriptors(cls: Type['AppletElaboratable'], dev_desc: DeviceDescriptorCollection) -> int:
		''' Initialize USB descriptors'''
		return 0


	@abstractmethod
	def elaborate(self, platform: SquishyPlatform) -> Module:
		'''  '''
		raise NotImplementedError('Applet Elaboratables must implement this method')
