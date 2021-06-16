# SPDX-License-Identifier: BSD-3-Clause
from nmigen import Elaboratable, Module, Signal

class SCSIInterface(Elaboratable):
	def __init__(self):
		self.activity_tx = Signal()
		self.activity_rx = Signal()

	def elaborate(self, platform):
		m = Module()

		scsi_tx = platform.request('scsi_tx')
		scsi_tx_ctl = platform.request('scsi_tx_ctl')
		scsi_rx = platform.request('scsi_rx')


		return m

