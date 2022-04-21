# SPDX-License-Identifier: BSD-3-Clause
from math                      import ceil, log2


from ...misc.utility           import ns_to_s

from amaranth                  import *
from amaranth_soc.wishbone     import Interface
from amaranth_soc.csr.bus      import Element, Multiplexer
from amaranth_soc.csr.wishbone import WishboneCSRBridge


__all__ = (
	'SCSIInterface',
)

# This is the SCSI 1,2,3 HVD,LVD,SE 50,68,80 PHY Block
class SCSIInterface(Elaboratable):
	def __init__(self, *, config, wb_config):
		self.config = config
		self._scsi_id = Signal(8)

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

		self.scsi_phy      = None

		self._scsi_in_fifo = None
		self._usb_out_fifo = None

		self._status_led = None

	def connect_fifo(self, *, scsi_in, usb_out):
		self._scsi_in_fifo = scsi_in
		self._usb_out_fifo = usb_out

	def _init_csrs(self):
		self._csr['regs'] = {
			'status': Element(8, 'r', name = 'scsi_status')
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

	def _elab_rev1(self, platform):
		self.scsi_phy     = platform.request('scsi_phy')
		self._status_led = platform.request('led', 1)

		self._interface_status = Signal(8)

		# SCSI Bus timings:
		# 	min arbitration delay  - 2.2us
		# 	min assertion period   - 90ns
		# 	min bus clear delay    - 800ns
		# 	max bus clear delay    - 1.2us
		# 	min bus free delay     - 800ns
		# 	max bus set delay      - 1.8us
		# 	min bus settle delay   - 400ns
		# 	max cable skew delay   - 10ns
		# 	max data release delay - 400ns
		# 	min deskew delay       - 45ns
		# 	min hold time          - 45ns
		# 	min negation period    - 90ns
		# 	min reset hold time    - 25us
		# 	max sel abort time     - 200us
		# 	min sel timeout delay  - 250ms (recommended)

		bus_settle_cnt = int(ceil(ns_to_s(400) * platform.pll_config['freq']) + 2)
		bus_settle_tmr = Signal(range(bus_settle_cnt))
		bus_settled    = Signal()

		hold_time_cnt = int(ceil(ns_to_s(45) * platform.pll_config['freq']) + 2)
		hold_time_tmr = Signal(range(hold_time_cnt))

		m = Module()
		m.submodules += self._csr_bridge
		m.submodules.csr_mux = self._csr['mux']

		self._csr_elab(m)

		m.d.comb += [
			self._interface_status[0:7].eq(Cat(
					self.scsi_phy.tp_en,
					self.scsi_phy.tx_en,
					self.scsi_phy.aa_en,
					self.scsi_phy.bsy_en,
					self.scsi_phy.sel_en,
					self.scsi_phy.mr_en,
					self.scsi_phy.diff_sense
			)),
			bus_settled.eq(0)
		]

		with m.If((~self.scsi_phy.sel.rx) & (~self.scsi_phy.bsy.rx)):
			with m.If(bus_settle_tmr == (bus_settle_cnt - 1)):
				m.d.comb += bus_settled.eq(1)
			with m.Else():
				m.d.sync += bus_settle_tmr.eq(bus_settle_tmr + 1)
		with m.Else():
			m.d.sync += bus_settle_tmr.eq(0)

		with m.FSM(reset = 'rst'):
			with m.State('rst'):
				m.d.sync += [
					self.scsi_phy.tp_en.eq(0),
					self.scsi_phy.tx_en.eq(0),
					self.scsi_phy.aa_en.eq(0),
					self.scsi_phy.bsy_en.eq(0),
					self.scsi_phy.sel_en.eq(0),
					self.scsi_phy.mr_en.eq(0),

					self.scsi_phy.d0.tx.eq(0),
					self.scsi_phy.dp0.tx.eq(0),
				]

				with m.If(bus_settled):
					m.next = 'bus_free'

			# bus_free - no scsi device is using the bus
			#
			with m.State('bus_free'):
				# All signals are left high-z due to no target/initiator
				m.d.sync += [
					self.scsi_phy.tp_en.eq(0),
					self.scsi_phy.tx_en.eq(0),
					self.scsi_phy.aa_en.eq(0),
					self.scsi_phy.bsy_en.eq(0),
					self.scsi_phy.sel_en.eq(0),
					self.scsi_phy.mr_en.eq(0),

					self.scsi_phy.d0.tx.eq(0),
					self.scsi_phy.dp0.tx.eq(0),
				]

				with m.If(self._scsi_in_fifo.r_rdy):
					m.next = 'selection'


				m.next = 'bus_free'

			with m.State('selection'):
				m.d.sync += [
					self.scsi_phy.mr_en.eq(1),
					self.scsi_phy.io.tx.eq(~self.scsi_phy.io.tx)
				]



				m.next = 'bus_free'

			with m.State('command'):


				m.next = 'bus_free'

			with m.State('data_in'):




				m.next = 'bus_free'

			with m.State('data_out'):



				m.next = 'bus_free'

			with m.State('message_in'):



				m.next = 'bus_free'

			with m.State('message_out'):



				m.next = 'bus_free'

			with m.State('status'):


				m.next = 'bus_free'

		return m

	def _elab_rev2(self, platform):
		m = Module()

		return m

	def elaborate(self, platform):
		if platform is None:
			m = Module()
			return m
		else:
			if platform.revision == 1:
				return self._elab_rev1(platform)
			elif platform.revision == 2:
				return self._elab_rev2(platform)
			else:
				raise ValueError(f'Unknown platform revision {platform.revision}')
