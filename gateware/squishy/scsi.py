# SPDX-License-Identifier: BSD-3-Clause
from nmigen import Elaboratable, Module, Signal

class SCSIInterface(Elaboratable):
	def __init__(self):
		self.activity_tx = Signal()
		self.activity_rx = Signal()

	def elaborate(self, platform):
		m = Module()

		scsi_raw = platform.request('scsi')

		return m

