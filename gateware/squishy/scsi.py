# SPDX-License-Identifier: BSD-3-Clause
from nmigen              import *
from nmigen_soc.wishbone import Interface
from nmigen_soc.memory   import MemoryMap

__all__ = ('SCSIInterface')

class SCSIInterface(Elaboratable):
	def __init__(self, *, config, wb_config):
		self.config = config
		self._wb_cfg = wb_config

		self.bus = Interface(
			addr_width  = 4,
			data_width  = self._wb_cfg['data'],
			granularity = self._wb_cfg['gran'],
			features    = self._wb_cfg['feat'],
			name        = 'scsi_wb'
		)

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

