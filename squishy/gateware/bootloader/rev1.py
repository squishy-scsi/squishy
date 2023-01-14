# SPDX-License-Identifier: BSD-3-Clause

from torii                                           import (
	Elaboratable, Module, ClockDomain,
	ResetSignal, Instance, Signal
)
from torii.hdl.ast                                   import (
	Operator
)

from sol_usb.usb2                                    import (
	USBDevice
)
from sol_usb.gateware.usb.request                    import (
	SetupPacket
)
from sol_usb.gateware.usb.usb2.request               import (
	StallOnlyRequestHandler
)

from usb_construct.types                             import (
	USBRequestType
)
from usb_construct.emitters.descriptors.standard     import (
	DeviceDescriptorCollection, LanguageIDs, DeviceClassCodes,
	InterfaceClassCodes, ApplicationSubclassCodes, DFUProtocolCodes
)
from usb_construct.types.descriptors.dfu             import *
from usb_construct.contextmgrs.descriptors.dfu       import *
from usb_construct.types.descriptors.microsoft       import *
from usb_construct.contextmgrs.descriptors.microsoft import *

from .dfu                 import DFURequestHandler
from ..quirks.usb.windows import WindowsRequestHandler


__doc__ = '''\

POR ->  Slot1 (Squishy Applet)
		Slot0 (DFU Bootloader)

Applet DFU Stub (reboot into Slot 0, w/ warmboot)
DFU Bootloader (DFU Alt-mods are slots)

dfu-util -a 0 <bootloader>
dfu-util -a 1 <applet>

'''

__all__ = (
	'rev1Bootloader',
)


class Bootloader(Elaboratable):
	'''  '''
	def __init__(self, *, serial_number: str) -> None:
		self._serial_number = serial_number

	def elaborate(self, platform) -> Module:
		m = Module()

		trigger_reboot = Signal()
		slot_select    = Signal(2)

		m.domains.usb = ClockDomain()
		ulpi = platform.request('ulpi', 0)
		m.submodules.dev = dev = USBDevice(bus = ulpi, handle_clocking = True)
		m.submodules += Instance(
			'SB_WARMBOOT',
			i_BOOT  = trigger_reboot,
			i_S0    = slot_select[0],
			i_S1    = slot_select[1],
		)

		descriptors = DeviceDescriptorCollection()
		with descriptors.DeviceDescriptor() as dev_desc:
			dev_desc.bcdUSB             = 2.01
			dev_desc.bDeviceClass       = DeviceClassCodes.INTERFACE
			dev_desc.bDeviceSubclass    = 0
			dev_desc.bDeviceProtocol    = 0
			dev_desc.idVendor           = platform.usb_vid
			dev_desc.idProduct          = platform.usb_pid_boot
			dev_desc.bcdDevice          = (0.00 + platform.revision)
			dev_desc.iManufacturer      = platform.usb_mfr
			dev_desc.iProduct           = platform.usb_prod[platform.usb_pid_boot]
			dev_desc.iSerialNumber      = self._serial_number
			dev_desc.bNumConfigurations = 1

		with descriptors.ConfigurationDescriptor() as cfg_desc:
			cfg_desc.bConfigurationValue = 1
			cfg_desc.iConfiguration      = 'Squishy Bootloader'
			cfg_desc.bmAttributes        = 0x80
			cfg_desc.bMaxPower           = 250

			for slot in platform.flash['geometry'].partitions:
				with cfg_desc.InterfaceDescriptor() as int_desc:
					int_desc.bInterfaceNumber   = 0
					int_desc.bAlternateSetting  = slot
					int_desc.bInterfaceClass    = InterfaceClassCodes.APPLICATION
					int_desc.bInterfaceSubclass = ApplicationSubclassCodes.DFU
					int_desc.bInterfaceProtocol = DFUProtocolCodes.DFU
					int_desc.iInterface         = f'Slot {slot}'

					with FunctionalDescriptor(int_desc) as func_desc:
						func_desc.bmAttributes   = (
							DFUWillDetach.YES | DFUManifestationTollerant.NO | DFUCanUpload.NO | DFUCanDownload.YES
						)
						func_desc.wDetachTimeOut = 1000
						func_desc.wTransferSize  = platform.flash['geometry'].erase_size

		platform_desc = PlatformDescriptorCollection()
		with descriptors.BOSDescriptor() as bos_desc:
			with PlatformDescriptor(bos_desc, platform_collection = platform_desc) as plat_desc:
				with plat_desc.DescriptorSetInformation() as desc_set_info:
					desc_set_info.bMS_VendorCode = 1

					with desc_set_info.SetHeaderDescriptor() as set_header:
						with set_header.SubsetHeaderConfiguration() as subset_cfg:
							subset_cfg.bConfigurationValue = 1

							with subset_cfg.SubsetHeaderFunction() as subset_func:
								subset_func.bFirstInterface = 0

								with subset_func.FeatureCompatibleID() as compat_id:
									compat_id.CompatibleID    = 'WINUSB'
									compat_id.SubCompatibleID = ''

		descriptors.add_language_descriptor((LanguageIDs.ENGLISH_US, ))
		ep0 = dev.add_standard_control_endpoint(descriptors)
		dfu_handler = DFURequestHandler(configuration = 1, interface = 0, resource_name = ('spi_flash_1x', 0))
		win_handler = WindowsRequestHandler(platform_desc)

		def stall_condition(setup: SetupPacket) -> Operator:
			return ~(
				(setup.type == USBRequestType.STANDARD) |
				dfu_handler.handler_condition(setup)     |
				win_handler.handler_condition(setup)
			)

		ep0.add_request_handler(dfu_handler)
		ep0.add_request_handler(win_handler)
		ep0.add_request_handler(StallOnlyRequestHandler(stall_condition = stall_condition))

		m.d.comb += [
			dev.connect.eq(1),
			dev.low_speed_only.eq(0),
			dev.full_speed_only.eq(0),
			ResetSignal('usb').eq(0),
			trigger_reboot.eq(dfu_handler.triggerReboot),
			slot_select.eq(0b01)
		]


		return m
