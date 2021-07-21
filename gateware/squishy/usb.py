# SPDX-License-Identifier: BSD-3-Clause
from nmigen              import *
from nmigen_soc.wishbone import Interface
from nmigen_soc.memory   import MemoryMap

from luna.usb2 import *

__all__ = ('USBInterface')

class USBInterface(Elaboratable):
	def __init__(self, *, config, wb_config):
		self.config = config
		self._wb_cfg = wb_config

		self.bus = Interface(
			addr_width  = 4,
			data_width  = self._wb_cfg['data'],
			granularity = self._wb_cfg['gran'],
			features    = self._wb_cfg['feat'],
			name        = 'usb_wb'
		)

		self.activity = Signal()

		self.usb_dev = None

	def init_descriptors(self):
		from usb_protocol.emitters import DeviceDescriptorCollection

		desc = DeviceDescriptorCollection()

		# Device Descriptor
		with desc.DeviceDescriptor() as dev:
			dev.idVendor  = self.config['vid']
			dev.idProduct = self.config['pid']

			dev.iManufacturer = self.config['mfr']
			dev.iProduct      = self.config['prd']
			dev.iSerialNumber = self.config['srn']

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

	def elaborate(self, platform):
		m = Module()

		ulpi_bus = platform.request('ulpi')

		m.submodules.usb = self.usb = USBDevice(bus = ulpi_bus)

		descriptors = self.init_descriptors()
		self.usb.add_standard_control_endpoint(descriptors)

		m.d.comb += [
			self.usb.connect.eq(1),

			self.activity.eq(self.usb.tx_activity_led | self.usb.rx_activity_led)
		]

		return m
