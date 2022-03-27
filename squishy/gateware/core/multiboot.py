# SPDX-License-Identifier: BSD-3-Clause
from amaranth  import *

__all__ = (
	'iCE40Warmboot',
)

class iCE40Warmboot(Elaboratable):
	def __init__(self):
		self.boot = Signal(1, reset = 0)
		self.s0   = Signal(1, reset = 0)
		self.s1   = Signal(1, reset = 0)

	def elaborate(self, _):
		m = Module()

		m.submodules.warmboot = Instance(
			'SB_WARMBOOT',
			i_BOOT = self.boot,
			i_S0   = self.s0,
			i_S1   = self.s1
		)

		return m

