# SPDX-License-Identifier: BSD-3-Clause
from nmigen                  import *
from nmigen_soc.wishbone     import Interface
from nmigen_soc.csr.bus      import Element, Multiplexer
from nmigen_soc.csr.wishbone import WishboneCSRBridge


from luna.usb2 import *

__all__ = (
	'USBInterface',
)

class USBInterface(Elaboratable):
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

		self._usb_in_fifo   = None
		self._scsi_out_fifo = None

		self._status_led = None

		self.usb_dev = None

	def connect_fifo(self, *, usb_in, scsi_out):
		self._usb_in_fifo   = usb_in
		self._scsi_out_fifo = scsi_out

	def init_descriptors(self, platform):
		from usb_protocol.emitters import DeviceDescriptorCollection

		desc = DeviceDescriptorCollection()

		# Device Descriptor
		with desc.DeviceDescriptor() as dev:
			dev.idVendor  = platform.usb_vid
			dev.idProduct = platform.usb_pid_app

			dev.iManufacturer = platform.usb_mfr
			dev.iProduct      = platform.usb_prod[dev.idProduct]
			dev.iSerialNumber = platform.usb_snum

			dev.bNumConfigurations = 1

		# Configuration Descriptor
		with desc.ConfigurationDescriptor() as cfg:
			# Mass-Storage Interface
			with cfg.InterfaceDescriptor() as i0:
				i0.bInterfaceNumber = 0

				with i0.EndpointDescriptor() as e0_out:
					e0_out.bEndpointAddress = 0x01
					e0_out.wMaxPacketSize   = 64

				with i0.EndpointDescriptor() as e0_in:
					e0_in.bEndpointAddress = 0x81
					e0_in.wMaxPacketSize   = 64

			# SCSI Interface
			with cfg.InterfaceDescriptor() as i1:
				i1.bInterfaceNumber = 1

				with i1.EndpointDescriptor() as e1_out:
					e1_out.bEndpointAddress = 0x02
					e1_out.wMaxPacketSize   = 64

				with i1.EndpointDescriptor() as e1_in:
					e1_in.bEndpointAddress = 0x82
					e1_in.wMaxPacketSize   = 64

		return desc

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
		self._status_led = platform.request('led', 2)
		self._ulpi_bus = platform.request('ulpi')

		self._interface_status = Signal(8)

		m = Module()
		m.submodules += self._csr_bridge
		m.submodules.csr_mux = self._csr['mux']


		m.submodules.usb = self.usb = USBDevice(bus = self._ulpi_bus)

		descriptors = self.init_descriptors(platform)
		self.usb.add_standard_control_endpoint(descriptors)

		m.d.comb += [
			self.usb.connect.eq(1),
			self._status_led.eq(self.usb.tx_activity_led | self.usb.rx_activity_led)
		]


		m.d.comb += [
			self._interface_status[0].eq(self.usb.tx_activity_led),
			self._interface_status[1].eq(self.usb.rx_activity_led),
		]

		self._csr_elab(m)

		return m
