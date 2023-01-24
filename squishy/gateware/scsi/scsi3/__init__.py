# SPDX-License-Identifier: BSD-3-Clause
from torii import Elaboratable, Module

__all__ = (
	'SCSI3',

	'Device',
	'Initiator',
)

__doc__ = '''\

'''

class SCSI3(Elaboratable):
	'''
	SCSI 3 Elaboratable

	This elaboratable represents an interface for interacting with SCSI-3 compliant buses.

	Parameters
	----------
	config : dict
		The configuration for this Elaboratable, including SCSI VID and DID.

	'''

	def __init__(self, *, config: dict) -> None:
		self.config = config

	def elaborate(self, platform) -> Module:
		m = Module()


		return m

def Device(*, config: dict) -> SCSI3:
	''' Create a SCSI-3 Device Elaboratable '''
	return SCSI3({'is_device': True, **config})

def Initiator(*, config: dict) -> SCSI3:
	''' Create a SCSI-3 Initiator Elaboratable '''
	return SCSI3({'is_device': False, **config})
