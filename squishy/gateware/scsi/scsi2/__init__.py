# SPDX-License-Identifier: BSD-3-Clause
from math             import ceil, log2

from amaranth         import *

from ....misc.utility import us_to_s, ns_to_s

__all__ = (
	'Device',
	'Initiator',
)


class SCSI2(Elaboratable):
	'''SCSI 2 Elaboratable

	This elaboratable represents an interface for interacting with SCSI-2 compliant bus'.

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

def Device(*args, **kwargs) -> SCSI2:
	'''sCreate a SCSI-2 Device Elaboratable'''
	return SCSI2(*args, is_device = True, **kwargs)

def Initiator(*args, **kwargs) -> SCSI2:
	'''Create a SCSI-2 Initiator Elaboratable'''
	return SCSI2(*args, is_device = False, **kwargs)
