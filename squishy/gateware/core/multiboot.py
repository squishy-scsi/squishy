# SPDX-License-Identifier: BSD-3-Clause
from amaranth  import *

__all__ = (
	'iCE40Warmboot',
)

class iCE40Warmboot(Elaboratable):
	'''Wrapper for iCE40 Warmboot block

	Parameters
	----------
	boot : Signal
		The signal to initiate a warmboot.

	slot : Signal
		The 2-bit address for the slot to warmboot into.

	'''
	def __init__(self):
		self.boot = Signal(1, reset = 0)
		self.slot = Signal(2, reset = 0)

	def elaborate(self, _):
		m = Module()

		m.submodules.warmboot = Instance(
			'SB_WARMBOOT',
			i_BOOT = self.boot,
			i_S0   = self.slot[0],
			i_S1   = self.slot[1]
		)

		return m
