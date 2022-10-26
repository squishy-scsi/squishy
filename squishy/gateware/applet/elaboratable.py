# SPDX-License-Identifier: BSD-3-Clause
from abc                            import (
	ABCMeta, abstractmethod
)
from typing                         import (
	Optional, List, Any, Type
)
from amaranth                       import (
	Elaboratable, Module
)
from luna.gateware.usb.usb2.request import (
	USBRequestHandler
)


__all__ = (
	'AppletElaboratable',
)

__doc__ = '''\

'''

class AppletElaboratable(Elaboratable, metaclass = ABCMeta):
	''''''

	def __init__(self) -> None:
		super().__init__()

	@property
	def scsi_request_handlers(self) -> Optional[List[Any]]:
		''' Returns a list of SCSI request handlers '''
		return None

	@property
	def usb_request_handlers(self) -> Optional[List[USBRequestHandler]]:
		''' Returns a list of USB request handlers '''
		return None

	@property
	def scsi_version(self) -> int:
		''' Returns the SCSI Version'''
		return 1

	@classmethod
	def usb_init_descriptors(cls: Type['AppletElaboratable'], dev_desc) -> int:
		''' Initialize USB descriptors'''
		return 0


	@abstractmethod
	def elaborate(self, platform) -> Module:
		''' '''
		raise NotImplementedError('Applet Elaboratables must implement this method')
