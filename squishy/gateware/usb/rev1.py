# SPDX-License-Identifier: BSD-3-Clause
from typing                                        import (
	Dict, Any, Iterable, Optional, Callable,
	Union, List
)

from torii                                         import (
	Elaboratable, Module,
	ResetSignal, Cat
)
from torii.hdl.ast                                 import (
	Operator
)

from sol_usb.usb2                                  import (
	USBDevice
)


from sol_usb.gateware.usb.usb2.request              import (
	StallOnlyRequestHandler, USBRequestHandler,
	SetupPacket
)

from usb_construct.types                            import (
	LanguageIDs, USBRequestType
)

from usb_construct.types.descriptors.dfu             import (
	DFUWillDetach, DFUManifestationTolerant,
	DFUCanUpload, DFUCanDownload
)
from usb_construct.contextmgrs.descriptors.dfu       import (
	FunctionalDescriptor
)

from usb_construct.emitters.descriptors.standard     import (
	DeviceDescriptorCollection, DeviceClassCodes, InterfaceClassCodes,
	ApplicationSubclassCodes, DFUProtocolCodes
)

from usb_construct.emitters.descriptors.microsoft    import (
	PlatformDescriptorCollection
)
from usb_construct.contextmgrs.descriptors.microsoft import (
	PlatformDescriptor
)

from .dfu                                            import (
	DFURequestHandler
)
from ..quirks.usb.windows                            import (
	WindowsRequestHandler
)

__doc__ = '''\

'''

__all__ = (
	'Rev1USB',
)


class Rev1USB(Elaboratable):
	'''
	SOL based USB ULPI Interface

	Warning
	-------
	Currently this is a USB 2.0 only interface, and is not able to interact with
	the hardware on Squishy rev2, this is to be fixed in the future.


	'''

	def __init__(self, *,
		config: Dict[str, Any],
		applet_desc_builder: Callable[..., None]
	) -> None:
		self.config = config
		self.applet_desc_builder = applet_desc_builder
		self.request_handlers: List[USBRequestHandler] = list()
		self.endpoints        = list()

		self.dev: Optional[USBDevice]          = None


	def init_descriptors(self) -> DeviceDescriptorCollection:
		descriptors = DeviceDescriptorCollection()

		with descriptors.DeviceDescriptor() as dev_desc:
			dev_desc.bcdDevice          = 1.01
			dev_desc.bcdUSB             = 2.01
			dev_desc.bDeviceClass       = DeviceClassCodes.INTERFACE
			dev_desc.bDeviceSubclass    = 0x00
			dev_desc.bDeviceProtocol    = 0x00
			dev_desc.idVendor           = self.config['vid']
			dev_desc.idProduct          = self.config['pid']
			dev_desc.iManufacturer      = self.config['manufacturer']
			dev_desc.iProduct           = self.config['product']
			dev_desc.iSerialNumber      = self.config['serial_number']
			dev_desc.bNumConfigurations = self.applet_desc_builder(descriptors) + 1

		with descriptors.ConfigurationDescriptor() as cfg_desc:
			cfg_desc.bConfigurationValue = 1
			cfg_desc.iConfiguration      = 'Squishy'
			cfg_desc.bmAttributes        = 0x80
			cfg_desc.bMaxPower           = 250

			with cfg_desc.InterfaceDescriptor() as iface_desc:
				iface_desc.bInterfaceNumber   = 0
				iface_desc.bAlternateSetting  = 0
				iface_desc.bInterfaceClass    = InterfaceClassCodes.APPLICATION
				iface_desc.bInterfaceSubclass = ApplicationSubclassCodes.DFU
				iface_desc.bInterfaceProtocol = DFUProtocolCodes.APPLICATION
				iface_desc.iInterface         = 'Squishy DFU'

				with FunctionalDescriptor(iface_desc) as func_desc:
					func_desc.bmAttributes = (
						DFUWillDetach.YES | DFUManifestationTolerant.NO |
						DFUCanUpload.NO   | DFUCanDownload.YES
					)
					func_desc.wDetachTimeOut = 1000
					func_desc.wTransferSize  = 4096

		# Thanks Microsoft:tm: /s
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

		return descriptors, platform_desc

	def add_request_handlers(self, request_handlers: Union[USBRequestHandler, Iterable[USBRequestHandler]]) -> None:
		if isinstance(request_handlers, USBRequestHandler):
			self.request_handlers.append(request_handlers)
		else:
			self.request_handlers.extend(request_handlers)

	def elaborate(self, platform) -> Module:
		m = Module()

		ulpi = platform.request('ulpi', 0)

		m.submodules.dev = self.dev = USBDevice(bus = ulpi, handle_clocking = True)

		descriptors, platform_desc = self.init_descriptors()

		ep0 = self.dev.add_standard_control_endpoint(
			descriptors
		)

		dfu_handler = DFURequestHandler(configuration_num = 1, interface_num = 0)
		win_handler = WindowsRequestHandler(platform_desc)

		self.add_request_handlers((dfu_handler, win_handler))

		def stall_condition(setup: SetupPacket) -> Operator:
			return ~(
				(setup.type == USBRequestType.STANDARD) |
				Cat(
					handler.handler_condition(setup) for handler in self.request_handlers
				).any()
			)


		for hndlr in self.request_handlers:
			ep0.add_request_handler(hndlr)

		ep0.add_request_handler(
			StallOnlyRequestHandler(stall_condition = stall_condition)
		)

		m.d.comb += [
			self.dev.connect.eq(1),
			self.dev.low_speed_only.eq(0),
			self.dev.full_speed_only.eq(0),
			ResetSignal('usb').eq(0),
		]

		return m
