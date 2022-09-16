# SPDX-License-Identifier: BSD-3-Clause
from amaranth         import Elaboratable, Module

__all__ = (
	'Device',
	'Initiator',
)

__doc__ = '''\

'''

class SCSI3(Elaboratable):
	'''SCSI 3 Elaboratable

	This elaboratable represents an interface for interacting with SCSI-3 compliant bus'.

	Parameters
	----------
	is_device : bool
		If this SCSI-1 Elaboratable is a Device or Initiator.

	'''

	def __init__(self, *, is_device: bool, config: dict) -> None:
		self.config = config

	def elaborate(self, platform) -> Module:
		m = Module()


		return m

def Device(*args, **kwargs) -> SCSI3:
	'''Create a SCSI-3 Device Elaboratable'''
	return SCSI3(*args, is_device = True, **kwargs)

def Initiator(*args, **kwargs) -> SCSI3:
	'''Create a SCSI-3 Initiator Elaboratable'''
	return SCSI3(*args, is_device = False, **kwargs)
