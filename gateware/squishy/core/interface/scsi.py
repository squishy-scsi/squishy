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
		self.bus = self._csr_bridge.wb_bus

		self.rx     = None
		self.tx     = None
		self.tx_ctl = None

		self._scsi_in_fifo = None
		self._usb_out_fifo = None

		self._status_led = None

	def connect_fifo(self, *, scsi_in, usb_out):
		if not len(scsi_in) == 4 or not len(usb_out) == 4:
			raise ValueError(f'expected a tuple of four signals for scsi_in and usb_out, got {scsi_in}, {usb_out}')

		self._scsi_in_fifo = scsi_in
		self._usb_out_fifo = usb_out

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
		m.d.comb += [
			self._csr['regs']['status'].r_data.eq(self._interface_status)
		]

	def elaborate(self, platform):
		self.rx     = platform.request('scsi_rx'),
		self.tx     = platform.request('scsi_tx'),
		self.tx_ctl = platform.request('scsi_tx_ctl')
		self._status_led = platform.request('led', 1)

		self._interface_status = Signal(8)

		m = Module()
		m.submodules += self._csr_bridge
		m.submodules.csr_mux = self._csr['mux']




		self._csr_elab(m)



		return m

