# SPDX-License-Identifier: BSD-3-Clause
from torii import Elaboratable, Module

__all__ = (
	'Device',
	'Initiator',
)

__doc__ = '''\

'''

class SCSI2(Elaboratable):
	'''
	SCSI 2 Elaboratable

	This elaboratable represents an interface for interacting with SCSI-2 compliant buses.

	Parameters
	----------
	is_device : bool
		If this SCSI-2 Elaboratable is a Device or Initiator.

	'''

	def __init__(self, *, is_device: bool, config: dict) -> None:
		self.config = config

	def elaborate(self, platform) -> Module:
		m = Module()


		return m

def Device(*args, **kwargs) -> SCSI2:
	''' Create a SCSI-2 Device Elaboratable '''
	return SCSI2(*args, is_device = True, **kwargs)

def Initiator(*args, **kwargs) -> SCSI2:
	''' Create a SCSI-2 Initiator Elaboratable '''
	return SCSI2(*args, is_device = False, **kwargs)
