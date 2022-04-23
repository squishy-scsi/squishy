# SPDX-License-Identifier: BSD-3-Clause
from math             import ceil, log2

from amaranth         import *

from ....misc.utility import us_to_s, ns_to_s

__all__ = (
	'Device',
	'Initiator',
)


class SCSI3(Elaboratable):
	'''SCSI 3 Elaboratable

	This elaboratable represents an interface for interacting with SCSI-3 compliant bus'.

	Parameters
	----------
	is_device : bool
		If this SCSI-1 Elaboratable is a Device or Initiator.

	'''

	def __init__(self, *, is_device, config):
		self.config = config

	def elaborate(self, platform):
		m = Module()


		return m

def Device(*args, **kwargs) -> SCSI3:
	'''Create a SCSI-3 Device Elaboratable'''
	return SCSI3(*args, is_device = True, **kwargs)

def Initiator(*args, **kwargs) -> SCSI3:
	'''Create a SCSI-3 Initiator Elaboratable'''
	return SCSI3(*args, is_device = False, **kwargs)
