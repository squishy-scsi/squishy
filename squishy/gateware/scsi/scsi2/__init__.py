# SPDX-License-Identifier: BSD-3-Clause
from torii import Elaboratable, Module

__all__ = (
	'SCSI2',

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
	config : dict
		The configuration for this Elaboratable, including SCSI VID and DID.

	'''

	def __init__(self, *, config: dict) -> None:
		self.config = config

	def elaborate(self, platform) -> Module:
		m = Module()


		return m

def Device(*, config: dict) -> SCSI2:
	''' Create a SCSI-2 Device Elaboratable '''
	return SCSI2({'is_device': True, **config})

def Initiator(*, config: dict) -> SCSI2:
	''' Create a SCSI-2 Initiator Elaboratable '''
	return SCSI2({'is_device': False, **config})
