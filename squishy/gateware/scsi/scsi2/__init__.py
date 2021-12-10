# SPDX-License-Identifier: BSD-3-Clause
from math         import ceil, log2

from amaranth       import *

from .....utility import us_to_s, ns_to_s

__all__ = (
	'Device',
	'Initiator',
	'SCSI2',
)


class SCSI2(Elaboratable):
	def __init__(self, *, is_device, config):
		self.config = config

	def elaborate(self, platform):
		m = Module()


		return m

def Device(*args, **kwargs):
	return SCSI1(*args, is_device = True, **kwargs)

def Initiator(*args, **kwargs):
	return SCSI1(*args, is_device = False, **kwargs)
