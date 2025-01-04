# SPDX-License-Identifier: BSD-3-Clause

'''

'''

from torii                                           import (
	Elaboratable, Module, ResetSignal, Signal, Cat
)
from torii.lib.fifo                                  import AsyncFIFO

from sol_usb.usb2                                    import USBDevice

from usb_construct.emitters.descriptors.standard     import (
	DeviceDescriptorCollection, LanguageIDs, DeviceClassCodes,
	InterfaceClassCodes, ApplicationSubclassCodes, DFUProtocolCodes
)
from usb_construct.types.descriptors.dfu             import *
from usb_construct.contextmgrs.descriptors.dfu       import *
from usb_construct.types.descriptors.microsoft       import *
from usb_construct.contextmgrs.descriptors.microsoft import *

from .rev1                                           import Rev1
from .rev2                                           import Rev2
from ..platform                                      import SquishyPlatformType
from ..usb.dfu                                       import DFURequestHandler
from ..usb.quirks.windows                            import WindowsRequestHandler
from ...core.config                                  import USB_DFU_CONFIG


__all__ = (
	'SquishyBootloader',
)

class SquishyBootloader(Elaboratable):
	'''
	Squishy DFU Bootloader

	This is the "top" module representing a Squishy DFU capable bootloader.

	It provides DFU alt-modes for each flash slot, including the bootloader, as well
	as dispatch to the appropriate programming interface for the given platform.


	For :py:class:`SquishyRev1` platforms, the method of programming is direct SPI flash, followed
	by an `SB_WARMBOOT` trigger.

	For :py:class:`SquishyRev2` this is more complicated, as we have the supervisor MCU in the mix.
	First the image is written to the SPI PSRAM, a signal is then sent to the supervisor to reboot
	us and re-program us with the new bitstream.


	Note
	----
	There needs to be some consideration for hardware platforms that support ephemeral programming,
	any transfers to that slot must be distinguished from a normal slot transfer, for Rev1 platforms
	this is not an issue, as there is no way of doing an ephemeral applet, however for Rev2, in order
	to try to tide wearing out flash with write cycles (even though they're good for like, 100k cycles)
	we have an (optional?) onboard PSRAM that acts as both a cache for doing flash updates as well as
	doing hot-loading without actually touching flash.

	This can be done mostly opaquely from the root of the bootloader module itself, other than having
	to properly name the ephemeral DFU slot, as all the machinery for updating the platform is within
	the target module for that anyway.

	Warning
	-------
	Currently there is no flash protection for the bootloader slot (slot 0), it is exposed by default,
	and treated like any other applet slot.

	We also don't have any checksums, which might be a bit problematic, but due to some platform limitations
	specifically due to Rev1 where we write directly into flash and don't have a buffer that can be used
	and discarded, we write-over the slot as we update. This is particularly dangerous for the bootloader.

	Parameters
	----------
	serial_number : str
		The device serial number to use.

	revision: tuple[int, int]
		The device revision.

	Attributes
	----------
	serial_number : str
		The device serial number assigned.

	'''

	def __init__(self, *, serial_number: str, revision: tuple[int, int]) -> None:
		self.serial_number = serial_number
		self._rev_raw      = revision
		# This is so stupid but it works for now:tm:
		self._rev_bcd      = (self._rev_raw[0] + 0.00) + round(self._rev_raw[1] * 0.1, 3)

	def elaborate(self, platform: SquishyPlatformType | None) -> Module:
		m = Module()

		# Set up our PLL and clock domains
		m.submodules.pll = pll = platform.clk_domain_generator()

		# Set up the USB2 ULPI-based device
		ulpi_bus = platform.request('ulpi', 0)
		m.submodules.usb_dev = dev = USBDevice(bus = ulpi_bus)

		# Set up USB Descriptors
		descriptors = DeviceDescriptorCollection()

		# Setup the Device
		with descriptors.DeviceDescriptor() as dev_desc:
			dev_desc.bcdUSB             = 2.01
			dev_desc.bDeviceClass       = DeviceClassCodes.INTERFACE
			# NOTE(aki): When the class is INTERFACE and `bDeviceSubclass` and `bDeviceProtocol` are both `0`
			#            then the host is to use the class information from the interface descriptors instead.
			dev_desc.bDeviceSubclass    = 0
			dev_desc.bDeviceProtocol    = 0
			dev_desc.idVendor           = USB_DFU_CONFIG.vid
			dev_desc.idProduct          = USB_DFU_CONFIG.pid
			dev_desc.bcdDevice          = self._rev_bcd
			dev_desc.iManufacturer      = USB_DFU_CONFIG.manufacturer
			dev_desc.iProduct           = USB_DFU_CONFIG.product
			dev_desc.iSerialNumber      = self.serial_number
			dev_desc.bNumConfigurations = 1 # Just the DFU configuration

		# Now set up our 1 configuration
		with descriptors.ConfigurationDescriptor() as cfg_desc:
			cfg_desc.bConfigurationValue = 1
			cfg_desc.iConfiguration      = 'Squishy DFU'
			cfg_desc.bmAttributes        = 0x80 # Default: 0b100'000
			cfg_desc.bMaxPower           = 250  # 2mA * 250

			# Populate our valid DFU slots
			for slot, _ in platform.flash.geometry.partitions.items():
				with cfg_desc.InterfaceDescriptor() as int_desc:
					int_desc.bInterfaceNumber   = 0
					int_desc.bAlternateSetting  = slot
					int_desc.bInterfaceClass    = InterfaceClassCodes.APPLICATION
					int_desc.bInterfaceSubclass = ApplicationSubclassCodes.DFU
					int_desc.bInterfaceProtocol = DFUProtocolCodes.DFU
					# TODO(aki): We should have a way have the bootloader slot be hidden but to
					#            allow for it to be "unlocked" for updating.
					#
					#            On rev2 hardware we can just have the user hold down the DFU button
					#            for 5sec or so then the supervisor MCU can bap us to have the slot.
					#            However, on rev1 we have no way to do anything like that, maybe if we
					#            have a special USB endpoint that you need to send the unlock code to?
					if slot == 0:
						int_desc.iInterface     = r'Bootloader ( /!\ Danger /!\ )'
					elif platform.ephemeral_slot is not None and slot == platform.ephemeral_slot:
						int_desc.iInterface     = 'Ephemeral Slot'
					else:
						int_desc.iInterface     = f'Applet Slot {slot}'

					with FunctionalDescriptor(int_desc) as func_desc:
						func_desc.bmAttributes   = (
							DFUWillDetach.YES | DFUManifestationTolerant.NO | DFUCanUpload.NO | DFUCanDownload.YES
						)
						func_desc.wDetachTimeOut = 1000
						func_desc.wTransferSize  = platform.flash.geometry.erase_size

		# Windows needs this extra stuff for it to not be stupid
		plat_descs = PlatformDescriptorCollection()
		with descriptors.BOSDescriptor() as bos_desc:
			with PlatformDescriptor(bos_desc, platform_collection = plat_descs) as plat_desc:
				with plat_desc.DescriptorSetInformation() as dset_info:
					dset_info.bMS_VendorCode = 1
					with dset_info.SetHeaderDescriptor() as set_header:
						with set_header.SubsetHeaderConfiguration() as sset_cfg:
							sset_cfg.bConfigurationValue = 1
							with sset_cfg.SubsetHeaderFunction() as sset_func:
								sset_func.bFirstInterface = 0
								with sset_func.FeatureCompatibleID() as compat_id:
									compat_id.CompatibleID    = 'WINUSB'
									compat_id.SubCompatibleID = ''

		# Setup the language for the descriptor strings
		descriptors.add_language_descriptor((LanguageIDs.ENGLISH_US, ))

		# Bundle our mess of descriptors into a control endpoint
		ep0 = dev.add_standard_control_endpoint(descriptors)

		# NOTE(aki): We might need to domain rename the SPI stuff into USB or have a SPI domain
		# Set up the bitstream/firmware FIFO
		m.submodules.bit_fifo = bit_fifo = AsyncFIFO(
			width = 8, depth = platform.flash.geometry.erase_size, r_domain = 'sync', w_domain = 'usb'
		)

		# Set up the DFU and the special Windows compat request handlers
		dfu_handler = DFURequestHandler(configuration = 1, interface = 0, boot_stub = False, fifo = bit_fifo)
		win_handler = WindowsRequestHandler(plat_descs)

		# Add our handlers to the endpoint
		ep0.add_request_handler(dfu_handler)
		ep0.add_request_handler(win_handler)

		# Instantiate the correct platform interface
		match self._rev_raw[0]:
			case 1:
				platform_interface = Rev1(bit_fifo)
			case 2:
				platform_interface = Rev2(bit_fifo)

		m.submodules.platform_interface = platform_interface

		# NOTE(aki): 5 is kinda a magic number, but it's how many stripes are in the trans flag
		#            and due to the LED colors for all platforms being that, we are pretty safe
		#            in assuming that there will be 5 LEDs
		leds = [ led.o for led in [ platform.request('led', r) for r in range(5) ] ]

		m.d.comb += [
			# ensure we connect the USB device
			dev.connect.eq(1),
			# Make sure we can do all the speeds
			dev.low_speed_only.eq(0),
			dev.full_speed_only.eq(0),
			# TODO(aki): Should this be tied to the PLL lock like we do with 'sync'?
			# Release the reset on the USB clock domain
			ResetSignal('usb').eq(~pll.pll_locked),
			# Hook together the platform interface and the DFU handler
			# TODO(aki): These really *really* should be pulled into an interface
			platform_interface.trigger_reboot.eq(dfu_handler.trigger_reboot),
			platform_interface.slot_selection.eq(dfu_handler.slot_selection),
			platform_interface.slot_changed.eq(dfu_handler.slot_changed),
			platform_interface.dl_start.eq(dfu_handler.dl_start),
			platform_interface.dl_finish.eq(dfu_handler.dl_finish),
			platform_interface.dl_completed.eq(dfu_handler.dl_completed),
			platform_interface.dl_size.eq(dfu_handler.dl_size),
			dfu_handler.slot_ack.eq(platform_interface.slot_ack),
			dfu_handler.dl_ready.eq(platform_interface.dl_ready),
			dfu_handler.dl_done.eq(platform_interface.dl_done),
		]

		# TODO(aki): pull out from sync domain
		timer = Signal(range(int(170e6 // 10)), reset = int(170e6 // 10) - 1)
		flops = Signal(len(leds), reset = 1)

		m.d.comb += [ Cat(leds).eq(flops), ]
		with m.If(timer == 0):
			m.d.sync += [
				timer.eq(timer.reset),
				flops.eq(flops.rotate_left(1)),
			]
		with m.Else():
			m.d.sync += [ timer.eq(timer - 1), ]

		return m
