# SPDX-License-Identifier: BSD-3-Clause
from amaranth                  import *
from amaranth_soc.wishbone     import Interface
from amaranth_soc.csr.bus      import Element, Multiplexer
from amaranth_soc.csr.wishbone import WishboneCSRBridge

from luna.usb2                 import *

from usb_protocol.types        import USBTransferType, USBUsageType

from usb_protocol.emitters.descriptors.standard import (
	DeviceDescriptorCollection, DeviceClassCodes, InterfaceClassCodes,
	MassStorageSubclassCodes, MassStorageProtocolCodes,
)

__all__ = (
	'USBInterface',
)

class USBInterface(Elaboratable):
	'''Luna based USB ULPI Interface

	Warning
	-------
	Currently this is a USB 2.0 only interface, and is not able to interact with
	the hardware on Squishy rev2, this is to be fixed in the future.

	'''
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
		desc = DeviceDescriptorCollection()

		# Device Descriptor
		with desc.DeviceDescriptor() as dev:
			dev.idVendor        = platform.usb_vid
			dev.idProduct       = platform.usb_pid_app

			dev.iManufacturer   = platform.usb_mfr
			dev.iProduct        = platform.usb_prod[dev.idProduct]
			dev.iSerialNumber   = platform.usb_snum

			dev.bcdDevice       = 0.01
			dev.bcdUSB          = 2.10

			dev.bDeviceClass    = DeviceClassCodes.INTERFACE
			dev.bDeviceSubclass = 0x00
			dev.bDeviceProtocol = 0x00

			dev.bNumConfigurations = 1

		# Configuration Descriptor
		with desc.ConfigurationDescriptor() as cfg:
			cfg.iConfiguration      = 'SCSI Multitool'
			cfg.bConfigurationValue = 1
			cfg.bmAttributes        = 0x80
			cfg.bMaxPower           = 250

			# Mass-Storage Interface
			with cfg.InterfaceDescriptor() as i0:
				i0.bInterfaceNumber   = 0
				i0.bInterfaceClass    = InterfaceClassCodes.MASS_STORAGE
				i0.bInterfaceSubclass = MassStorageSubclassCodes.NON_SPECIFIC
				i0.bInterfaceProtocol = MassStorageProtocolCodes.CBI_INTERRUPT
				i0.iInterface         = 'Storage Interface'

				with i0.EndpointDescriptor() as e0_out:
					e0_out.bmAttributes     = USBTransferType.BULK
					e0_out.bEndpointAddress = 0x01
					e0_out.wMaxPacketSize   = 0x0200

				with i0.EndpointDescriptor() as e0_in:
					e0_in.bmAttributes     = USBTransferType.INTERRUPT | USBUsageType.FEEDBACK
					e0_in.bInterval        = 0x0A
					e0_in.bEndpointAddress = 0x81
					e0_in.wMaxPacketSize   = 0x0400

			# SCSI Interface
			with cfg.InterfaceDescriptor() as i1:
				i1.bInterfaceNumber   = 1
				i1.bInterfaceClass    = InterfaceClassCodes.MASS_STORAGE
				i1.bInterfaceSubclass = MassStorageSubclassCodes.TRANSPARENT
				# Might want to make this CBI_NO_INTERRUPT,,,
				i1.bInterfaceProtocol = MassStorageProtocolCodes.VENDOR
				i1.iInterface         = 'SCSI Command Interface'

				with i1.EndpointDescriptor() as e1_out:
					e1_out.bmAttributes     = USBTransferType.BULK
					e1_out.bEndpointAddress = 0x02
					e1_out.wMaxPacketSize   = 0x0200

				with i1.EndpointDescriptor() as e1_in:
					e1_in.bmAttributes     = USBTransferType.INTERRUPT | USBUsageType.FEEDBACK
					e1_in.bInterval        = 0x0A
					e1_in.bEndpointAddress = 0x82
					e1_in.wMaxPacketSize   = 0x0400

		if self.config['webusb']['enabled']:
			from usb_protocol.emitters.descriptors.standard import BinaryObjectStoreDescriptorEmitter
			from usb_protocol.emitters.descriptors.webusb   import PlatformDescriptorEmitter

			bos = BinaryObjectStoreDescriptorEmitter()
			webusb_plat = PlatformDescriptorEmitter(desc)

			webusb_plat.iLandingPage = self.config['webusb']['url']

			bos.add_subordinate_descriptor(webusb_plat)
			desc.add_descriptor(bos)

		return desc

	def _init_csrs(self):
		self._csr['regs'] = {
			'status': Element(8, 'r', name = 'usb_status')
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
