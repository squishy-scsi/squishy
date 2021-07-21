# SPDX-License-Identifier: BSD-3-Clause
from nmigen                  import *
from nmigen_soc.wishbone     import Interface
from nmigen_soc.csr.bus      import Element, Multiplexer
from nmigen_soc.csr.wishbone import WishboneCSRBridge

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

		self.ctl_bus = Interface(
			addr_width  = self._wb_cfg['addr'],
			data_width  = self._wb_cfg['data'],
			granularity = self._wb_cfg['gran'],
			features    = self._wb_cfg['feat']
		)

		self._csr = {
			'mux'     : None,
			'elements': {}
		}
		self._init_csrs()
		self._csr_bridge = WishboneCSRBridge(self._csr['mux'].bus)

		self.rx     = None
		self.tx     = None
		self.tx_ctl = None

		self._status_led = None

		self.activity = Signal()

	def _init_csrs(self):
		self._csr['regs'] = {
			'status': Element(8, 'r')
		}

		self._csr['mux'] = Multiplexer(
			addr_width = 1,
			data_width = self._wb_cfg['data']
		)

		self._csr['mux'].add(self._csr['regs']['status'], addr = 0)

	def _csr_elab(self, m):
		m.submodules += self._csr_bridge
		m.submodules.csr_mux = self._csr['mux']

	def elaborate(self, platform):
		self.rx     = platform.request('scsi_rx'),
		self.tx     = platform.request('scsi_tx'),
		self.tx_ctl = platform.request('scsi_tx_ctl')
		self._status_led = platform.request('led', 1)

		m = Module()
		self._csr_elab(m)



		return m

