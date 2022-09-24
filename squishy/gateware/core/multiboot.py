# SPDX-License-Identifier: BSD-3-Clause
from amaranth                      import *
from amaranth.vendor.lattice_ice40 import LatticeICE40Platform

__all__ = (
	'iCE40Warmboot',
)

class iCE40Warmboot(Elaboratable):
	'''Wrapper for iCE40 Warmboot block

	This elaboratable instantiates an instance of the ``SB_WARMBOOT`` resource
	found on iCE40 FPGAs, allowing for alternate bitstrteam loading from gateware.

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

	def elaborate(self, platform) -> Module:
		if not isinstance(platform, LatticeICE40Platform):
			raise ValueError(f'The iCE40Warmboot is only available on LatticeICE40Platforms, not {platform!r}!')

		m = Module()

		m.submodules.warmboot = Instance(
			'SB_WARMBOOT',
			i_BOOT = self.boot,
			i_S0   = self.slot[0],
			i_S1   = self.slot[1]
		)

		return m
