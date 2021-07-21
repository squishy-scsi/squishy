# SPDX-License-Identifier: BSD-3-Clause
from nmigen import *

__all__ = ('SCSIInterface')

class SCSIInterface(Elaboratable):
	def __init__(self, *, config):

		self.config = config

		self.rx     = None
		self.tx     = None
		self.tx_ctl = None

		self.activity = Signal()

	def elaborate(self, platform):
		self.rx     = platform.request('scsi_rx'),
		self.tx     = platform.request('scsi_tx'),
		self.tx_ctl = platform.request('scsi_tx_ctl')

		m = Module()


		return m

