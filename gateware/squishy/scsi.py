# SPDX-License-Identifier: BSD-3-Clause
from nmigen import Elaboratable, Module, Signal

class SCSIInterface(Elaboratable):
	def __init__(self, *, rx, tx, tx_ctl):
		self.rx       = rx
		self.tx       = tx
		self.tx_ctl   = tx_ctl

		self.activity = Signal()

	def elaborate(self, platform):
		m = Module()


		return m

