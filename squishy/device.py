# SPDX-License-Identifier: BSD-3-Clause

'''
This module contains the :py:class:`SquishyDevice` object. It is the primary method for interacting
with the physical Squishy hardware, as such, it abstracts away a large portion of the the common
tasks such as DFU uploads to load new applets onto the system.

However, it can only be so generic, more advanced applets will likely define custom USB endpoints and
functions, and may choose to ignore most if not all of the functionality of this module.

For example, an applet that implements a USB Attached SCSI (UAS) bridge device will likely only
ever use the :py:class:`SquishyDevice` to upload the gateware onto the device, after that the
host OS will treat Squishy like any other UAS device, assuming it has drivers for it.

'''

import logging                           as log
from collections.abc                     import Callable, Iterable
from contextlib                          import contextmanager
from datetime                            import datetime, timezone
from itertools                           import zip_longest
from time                                import sleep
from typing                              import TYPE_CHECKING, Self, TypeAlias, TypeVar

from rich.progress                       import Progress
from usb1                                import USBContext, USBDevice, USBError
from usb1.libusb1                        import (
	LIBUSB_ERROR_IO, LIBUSB_ERROR_NO_DEVICE, LIBUSB_RECIPIENT_INTERFACE, LIBUSB_REQUEST_TYPE_CLASS
)
from usb_construct.types                 import LanguageIDs
from usb_construct.types.descriptors.dfu import FunctionalDescriptor

from .core.config                        import USB_APP_PID, USB_DFU_PID, USB_VID
from .core.dfu                           import DFU_CLASS, DFURequests, DFUState, DFUStatus
from .gateware                           import AVAILABLE_PLATFORMS, SquishyPlatformType

__all__ = (
	'SquishyDevice',
)


# NOTE(aki): Due to how `libusb1` works and how we're using it, we need to
# hold a global reference to the context, I don't like it any more than the
# next girl, but here we are.
_LIBUSB_CTX: USBContext | None = None

# Type Alias to simplify life
DeviceContainer: TypeAlias = tuple[str, tuple[int, int], USBDevice]

T = TypeVar('T')

# This is here because `next(filter(...), None)` doesn't propagate types properly
# TODO(aki): Maybe move to a helpers/utility module?
def _find_if(collection: Iterable[T], predicate: Callable[[T], bool]) -> T | None:
	for item in collection:
		if predicate(item):
			return item
	return None

# TODO(aki): This kinda sucks, can we directly slice bytearrays?
def _chunker(size: int, data: Iterable[T]):
	return zip_longest(*[iter(data)] * size)

@contextmanager
def usb_device_handle(dev: USBDevice):
	''' Wrap the usb1 dev.open()/hndl.close() in a context manager '''
	handle = dev.open()
	try:
		yield handle
	finally:
		handle.close()


class SquishyDevice:
	'''
	Squishy Hardware Device

	This class represents a Squishy hardware device that is attached to the host, it exposes
	a common and stable API for interacting with Squishy devices.

	Parameters
	----------
	dev : usb1.USBDevice
		The USB Device handle for the attached Squishy hardware.

	serial : str
		The serial number of the device.

	timeout : int
		USB Transaction timeout in ms. (default: 2500)


	Attributes
	----------

	rev : tuple[int, int]
		The revision of the attached Squishy device in the form of (major, minor).

	serial : str
		The serial number of this Squishy device

	'''

	@staticmethod
	def _unpack_revision(bcd: int) -> tuple[int, int]:
		'''
		Un-pack the Squishy revision from the USB BCD Descriptor.

		Returns
		-------
		tuple[int, int]
			The revision of the Squishy hardware that was packed into the USB BCD in the form
			of (major, minor)
		'''

		major = bcd >> 8
		major = ((major >> 4) * 10) + (major & 0xF)

		minor = bcd & 0xFF
		minor = ((minor >> 4) * 10) + (minor & 0xF)

		return (major, minor)

	def _get_dfu_interface(self) -> int | None:
		'''
		Get the USB Interface number that matches ``DFU_CLASS``

		Returns
		-------
		int | None
			The DFU interface number, or None if not found
		'''
		if self._dfu_iface is None and self._dfu_cfg is None:
			# Iterate over device configurations
			for config in self._dev.iterConfigurations():
				# For each config, iterate over the interfaces
				for iface in config:
					# For each interface, iterate over the settings
					for setting in iface:
						# Check to see if it's `DFU_CLASS`
						if setting.getClassTupple() == DFU_CLASS:
							# If so, then we extract the configuration and interface IDs
							self._dfu_cfg: int    = config.getConfigurationValue()
							self._dfu_iface: int  = setting.getNumber()
							# Check if the current device configuration is the DFU config
							if self._usb_handle.getConfiguration() != self._dfu_cfg:
								# If not, we make it the current configuration
								self._usb_handle.setConfiguration(self._dfu_cfg)
							# And return the DFU interface number
							return self._dfu_iface

		return self._dfu_iface

	def _get_dfu_status(self) -> tuple[DFUStatus, DFUState]:
		'''
		Get the state and status for the DFU endpoint.

		Returns
		-------
		tuple[DFUStatus, DFUState]
			The status and state of the DFU endpoint.

		Raises
		------
		RuntimeError
			If the DFU interface is unknown, or the DFU get status request fails or times out.
		'''

		# Try to get the DFU interface
		interface_id = self._get_dfu_interface()
		if interface_id is None:
			raise RuntimeError(f'Unable to get DFU interface id for {self._usb_dev_str}')

		# Ensure we have our grubby little paws on it
		self._ensure_iface_claimed(interface_id)

		# Try to request the status
		data: bytearray | None = self._usb_handle.controlRead(
			LIBUSB_REQUEST_TYPE_CLASS | LIBUSB_RECIPIENT_INTERFACE,
			DFURequests.GetStatus,
			0,
			interface_id,
			6,
			self._timeout
		)

		# If we didn't get any data back (likely a timeout) then bail
		if data is None:
			raise RuntimeError(f'Unable to read DFU status from `{self._usb_dev_str}` on interface `{interface_id}`')

		# Otherwise, return the State and Status
		return (DFUStatus(data[0]), DFUState(data[4]))

	def _get_dfu_state(self) -> DFUState:
		'''
		Get the state for the DFU endpoint.

		Returns
		-------
		DFUState
			The state of the DFU endpoint.

		Raises
		------
		RuntimeError
			If the DFU interface is unknown, or the DFU get state request fails or times out.
		'''

		# Try to get the DFU interface
		interface_id = self._get_dfu_interface()
		if interface_id is None:
			raise RuntimeError(f'Unable to get DFU interface id for {self._usb_dev_str}')

		# Ensure we have our grubby little paws on it
		self._ensure_iface_claimed(interface_id)

		# Try to request the status
		data: bytearray | None = self._usb_handle.controlRead(
			LIBUSB_REQUEST_TYPE_CLASS | LIBUSB_RECIPIENT_INTERFACE,
			DFURequests.GetState,
			0,
			interface_id,
			1,
			self._timeout
		)

		# If we didn't get any data back (likely a timeout) then bail
		if data is None:
			raise RuntimeError(f'Unable to read DFU state from `{self._usb_dev_str}` on interface `{interface_id}`')

		# Otherwise, return the State and Status
		return DFUState(data[0])

	def _send_dfu_detach(self) -> bool:
		'''
		Invoke a DFU detach.

		Returns
		-------
		bool
			True if the detach was successful, otherwise False

		Raises
		------
		RuntimeError
			If the DFU interface is unknown, or the DFU control request times out.
		'''

		# Try to get the DFU interface
		interface_id = self._get_dfu_interface()
		if interface_id is None:
			raise RuntimeError(f'Unable to get DFU interface id for {self._usb_dev_str}')

		# Ensure we have the DFU interface, and clean it up after
		with self._ensure_iface(interface_id):
			# Try to poke the device to get it to reboot
			try:
				sent: int = self._usb_handle.controlWrite(
					LIBUSB_REQUEST_TYPE_CLASS | LIBUSB_RECIPIENT_INTERFACE,
					DFURequests.Detach,
					0,
					interface_id,
					bytearray(),
					self._timeout
				)
			except USBError as e:
				# If the error is one of the not-actually-an-error errors caused by the device rebooting, palm it off
				if e.value in (LIBUSB_ERROR_IO, LIBUSB_ERROR_NO_DEVICE):
					sent = 0
				# Otherwise bubble it up
				else:
					raise RuntimeError(
						f'Unable to send DFU detach to `{self._usb_dev_str}` on interface `{interface_id}`'
					)

		return sent == 0

	def _get_dfu_altmodes(self) -> dict[int, str]:
		'''
		Collect and return all of the DFU alt-modes and their name from the device.

		Returns
		-------
		dict[int, str]
			A mapping of the alt-mode endpoint and it's name.

		Raises
		------
		RuntimeError
			If the DFU interface is unknown, or the DFU control request times out.
		AssertionError
			If we lose the DFU configuration or interface somehow.
		'''

		# Try to get the DFU interface
		interface_id = self._get_dfu_interface()
		if interface_id is None:
			raise RuntimeError(f'Unable to get DFU interface id for {self._usb_dev_str}')

		cfg_id = self._dfu_cfg

		config = _find_if(self._dev.iterConfigurations(), lambda cfg: cfg.getConfigurationValue() == cfg_id)
		if config is None:
			raise AssertionError('Failed to re-locate USB DFU configuration')

		interface = _find_if(config.iterInterfaces(), lambda ifc: next(iter(ifc)).getNumber() == interface_id)
		if interface is None:
			raise AssertionError('Failed to re-locate USB DFU interface')

		alt_modes: dict[int, str] = {}
		# Iterate over all of the alt-modes
		for alt in interface:
			mode_id: int = alt.getAlternateSetting()
			# Try to get the alt-mode's string descriptor
			mode_name = self._usb_handle.getStringDescriptor(
				alt.getDescriptor(),
				LanguageIDs.ENGLISH_US
			)

			alt_modes[mode_id] = mode_name if mode_name is not None else f'mode {mode_id}'

		return alt_modes

	def _get_dfu_tx_size(self) -> int | None:
		'''
		Get the DFU transaction size in bytes.

		Returns
		-------
		int | None
			The DFU transaction size in bytes, or if unable to be found None

		Raises
		------
		RuntimeError
			If the DFU interface is unknown, or the DFU control request times out.
		AssertionError
			If we lose the DFU configuration or interface somehow.
		'''

		# Try to get the DFU interface
		interface_id = self._get_dfu_interface()
		if interface_id is None:
			raise RuntimeError(f'Unable to get DFU interface id for {self._usb_dev_str}')

		cfg_id = self._dfu_cfg

		config = _find_if(self._dev.iterConfigurations(), lambda cfg: cfg.getConfigurationValue() == cfg_id)
		if config is None:
			raise AssertionError('Failed to re-locate USB DFU configuration')

		interface = _find_if(config.iterInterfaces(), lambda ifc: next(iter(ifc)).getNumber() == interface_id)
		if interface is None:
			raise AssertionError('Failed to re-locate USB DFU interface')

		# Get the first alt-mode
		settings = next(iter(interface))
		extra    = settings.getExtra()

		# Check to ensure there is only one functional descriptor
		if len(extra) != 1:
			raise RuntimeError(f'Expected only one functional descriptor in alt-mode, found {len(extra)}')

		# Pull out the descriptor and get the transfer size
		func_desc = FunctionalDescriptor.parse(extra[0])
		if TYPE_CHECKING:
			assert isinstance(func_desc.wTransferSize, int)

		return func_desc.wTransferSize

	def _enter_dfu(self) -> bool:
		'''
		Instruct the device to enter DFU mode.

		Returns
		-------
		bool
			True if we managed to enter DFU mode, False otherwise.
		'''

		# Check to see if we're not already in DFU
		if self._get_dfu_state() == DFUState.AppIdle:
			# We're not, so poke at the device to get use there
			self._send_dfu_detach() # BUG(aki): We should do something about this return value, huh?
			# Flush the device and handles
			self._usb_handle.close()
			self._dev.close()
			self._dfu_iface = None
			self._dfu_cfg   = None

			device: DeviceContainer | None = None

			# Re-enumerate the devices after a short timeout
			log.debug(f'Waiting for `{self.serial}` to come back')
			sleep(self._timeout / 1000)
			# BUG(aki): This *might* spin forever in some cases
			while device is None:
				device = _find_if(self.enumerate(), lambda dev: dev[0] == self.serial)

			# We have the device back, re-attach
			log.debug('Device came back, re-attaching')
			(_, _, dev) = device

			self._dev = dev
			self._usb_handle = self._dev.open()

		# Now that we *should* be in DFU make sure we are actually there
		dfu_state = self._get_dfu_state()
		log.debug(f'DFU State: {dfu_state}')

		if dfu_state != DFUState.DFUIdle:
			log.error(f'Device came back in an improper DFU state: {dfu_state}')
			return False
		return True

	def _send_dfu_download(self, data: bytearray, chunk_num: int) -> bool:
		'''
		Push a chunk of data to the DFU endpoint. In DFU terminology this is a "Download"

		Returns
		-------
		bool
			True if the DFU transaction was successful, otherwise False.

		Raises
		------
		RuntimeError
			If the DFU interface is unknown, or the DFU control request times out.
		'''

		# Try to get the DFU interface
		interface_id = self._get_dfu_interface()
		if interface_id is None:
			raise RuntimeError(f'Unable to get DFU interface id for {self._usb_dev_str}')

		# Ensure we have our grubby little paws on it
		self._ensure_iface_claimed(interface_id)

		# Stuff the data in the endpoints face
		sent: int = self._usb_handle.controlWrite(
			LIBUSB_REQUEST_TYPE_CLASS | LIBUSB_RECIPIENT_INTERFACE,
			DFURequests.Download,
			chunk_num,
			interface_id,
			data,
			self._timeout
		)

		return sent == len(data)

	@contextmanager
	def _ensure_iface(self, iface_id: int):
		''' A context manager helper for wrapping USB interface handling '''
		self._ensure_iface_claimed(iface_id)
		try:
			yield
		finally:
			self._ensure_iface_released(iface_id)

	def _ensure_iface_claimed(self, iface_id: int) -> None:
		'''
		Ensures the given USB interface is claimed.

		Parameters
		----------
		iface_id : int
			The USB interface ID to ensure is claimed.
		'''

		if iface_id not in self._claimed_interfaces:
			self._usb_handle.claimInterface(iface_id)
			self._claimed_interfaces.append(iface_id)

	def _ensure_iface_released(self, iface_id: int) -> None:
		'''
		Ensures the given USB interface is released.

		Parameters
		----------
		iface_id : int
			The USB interface ID to ensure is released.
		'''

		if iface_id in self._claimed_interfaces:
			self._claimed_interfaces.remove(iface_id)
			try:
				self._usb_handle.releaseInterface(iface_id)
			except USBError as e:
				if e.value != LIBUSB_ERROR_NO_DEVICE:
					raise

	@property
	def _usb_dev_str(self) -> str:
		''' The formatted USB device string in the form of ``VID:PID @ BUSID``  '''
		return f'{self._dev.getVendorID():04x}:{self._dev.getProductID():04x} @ {self._dev.getBusNumber()}'

	def __init__(self, dev: USBDevice, serial: str, timeout: int = 2500) -> None:
		# USB Device and handle
		self._dev        = dev
		self._usb_handle = self._dev.open()
		if not self.can_dfu():
			raise RuntimeError(f'The device {self._usb_dev_str} is not DFU capable.')

		self._timeout               = timeout
		self._dfu_cfg: int | None   = None
		self._dfu_iface: int | None = None

		# Device Metadata
		self.serial             = serial
		self._raw_revision: int = self._dev.getbcdDevice()
		self.rev                = self._unpack_revision(self._raw_revision)

		# USB Interface accounting
		self._claimed_interfaces = list()

	def __del__(self) -> None:
		self._usb_handle.close()
		self._dev.close()

	def __repr__(self) -> str:
		return f'<SquishyDevice SN=\'{self.serial}\' REV=\'{self.rev}\' ADDR=\'{self._dev.getDeviceAddress()}\' >'

	def __str__(self) -> str:
		# TODO(aki): The rev bits should be made less, bad,
		return f'Squishy rev{self.rev[0]}.{self.rev[1]} SN: {self.serial}'

	@classmethod
	def get_device(cls: type[Self], *, serial: str | None = None, first: bool = True) -> Self | None:
		'''
		Returns an instance of the first :py:class:`SquishyDevice` attached to the system,
		or if ``serial`` is specified the device with that serial number, if possible.

		If there are no Squishy devices attached to the host system, or one with  ``serial`` is not found
		None is returned instead.

		Parameters
		----------
		serial : str  | None
			The serial number of the target device wanted.

		first : bool
			If there is more than one Squishy attached, and no serial number is specified,
			return the first that occurs in the list.

		Returns
		-------
		SquishyDevice | None
			The requested Squishy device if found, otherwise None

		'''

		# Get all attached Squishy devices
		attached = SquishyDevice.enumerate()
		count    = len(attached)

		# Bail early if we don't have any devices at all
		if count == 0:
			log.warning('No Squishy devices found attached to system')
			return None

		# There is only one device, or we're just yoinking the first one on the system
		if count == 1 or (serial is None and first):
			found_device = attached[0]
		# We're not yoinking the first, but we don't have a serial number
		elif serial is None and not first:
			log.error(
				f'No serial number specified and I\'m not allowed to pick the first of the {count} devices attached.'
			)
			log.error('Please specify a serial number')
			return None
		# There are more the once device, and we have a serial number to look for
		else:
			# Try to pull out devices that match our serial number (there should only be one)
			found = tuple(filter(lambda sn, _, __: sn == serial, attached))
			num_found = len(found)
			if num_found > 1:
				# ohno
				log.error(f'Found {len(found)} Squishy devices matching serial number `{serial}`')
				return None
			elif num_found == 0:
				log.error(f'No Squishy device with serial number `{serial}` found')
			else:
				found_device = found[0]

		# Now we have a device, time to construct a SquishyDevice around it for use
		(serial_number, _, dev) = found_device
		# We-forward propagate the serial number incase the input one is None
		return cls(dev, serial_number)

	@classmethod
	def enumerate(cls: type[Self]) -> list[DeviceContainer]:
		'''
		Collect all of the attached Squishy devices.

		Returns
		-------
		list[DeviceContainer]
			A collection of Squishy hardware devices attached to the system.
		'''

		# icky icky icky icky
		global _LIBUSB_CTX

		# If we don't have a libusb context, make one.
		if _LIBUSB_CTX is None:
			_LIBUSB_CTX = USBContext()

		devices: list[DeviceContainer] = []

		# Iterate over all attached USB devices and filter out anything we're interested in
		for dev in _LIBUSB_CTX.getDeviceIterator(skip_on_error = True):
			dev_vid = dev.getVendorID()
			dev_pid = dev.getProductID()

			# Make sure we only try to interact with Squishies
			if dev_vid == USB_VID and dev_pid in (USB_APP_PID, USB_DFU_PID):
				try:
					# Pull out the serial number
					with usb_device_handle(dev) as hndl:
						serial_number = hndl.getStringDescriptor(
							dev.getSerialNumberDescriptor(),
							LanguageIDs.ENGLISH_US
						)

					# Un-pack the version from the device BCD
					version = cls._unpack_revision(dev.getbcdDevice())

					# Stick it into the list of known devices
					devices.append((serial_number, version, dev))

				except USBError as e:
					log.error(f'Unable to open suspected Squishy device: {e}')
					log.error('Maybe check your udev rules?')

		return devices

	@staticmethod
	def generate_serial() -> str:
		'''
		Generate a new serial number string for a Squishy device.

		The current implementation uses the current datetime in an
		ISO 8601-like format.

		Returns
		-------
		str
			The new serial number.
		'''

		return datetime.now(timezone.utc).strftime(
			'%Y%m%dT%H%M%SZ'
		)

	def can_dfu(self) -> bool:
		'''
		Determine whether or not this device is DFU capable.

		Returns
		-------
		bool
			True if the given USB device is DFU capable, otherwise False
		'''

		log.debug(f'Checking if {self._usb_dev_str} is DFU capable')
		return any(filter(
			lambda cls: cls == DFU_CLASS,
			map(
				lambda setting: setting.getClassTupple(),
				self._dev.iterSettings()
			)
		))

	def get_altmodes(self) -> dict[int, str]:
		'''
		Collect and return all of the DFU alt-modes and their name from the device.

		Returns
		-------
		dict[int, str]
			A mapping of the alt-mode endpoint and it's name.

		Raises
		------
		RuntimeError
			If the DFU interface is unknown, or the DFU control request times out.
		AssertionError
			If we lose the DFU configuration or interface somehow.
		'''

		return self._get_dfu_altmodes()

	def reset(self) -> bool:
		'''
		Invoke a DFU detach.

		Returns
		-------
		bool
			True if the detach was successful, otherwise False

		Raises
		------
		RuntimeError
			If the DFU interface is unknown, or the DFU control request times out.
		'''

		return self._send_dfu_detach()

	def upload(self, data: bytes, altmode: int, progress: Progress | None = None) -> bool:
		'''
		Push firmware/gateware to device.

		Parameters
		----------
		data : bytes
			The data to upload to the device.

		altmode : int
			The alt-mode endpoint to upload to.

		progress : rich.progress.Progress | None
			Optional Rich progressbar instance.

		Returns
		-------
		bool
			Upload was successful, otherwise False

		Raises
		------
		RuntimeError
			If the DFU interface is unknown, the DFU control request times out, or we can't determine the transaction
			size.
		'''

		# First try to enter DFU mode
		if not self._enter_dfu():
			return False

		# Try to get the DFU interface
		interface_id = self._get_dfu_interface()
		if interface_id is None:
			raise RuntimeError(f'Unable to get DFU interface id for {self._usb_dev_str}')

		# Ensure we have our grubby little paws on it
		self._ensure_iface_claimed(interface_id)

		# Set (or at least try to) the alt-mode for the DFU interface
		self._usb_handle.setInterfaceAltSetting(interface_id, altmode)

		# Try and get the transaction size so we know how big to make our chunks
		trans_size = self._get_dfu_tx_size()
		if trans_size is None:
			raise RuntimeError(f'Unable to determine DFU transaction size for `{self._usb_dev_str}`')

		log.debug(f'DFU Transfer size: {trans_size}')

		# if there is a progress bar, add task to it
		if progress is not None:
			prog_task = progress.add_task('Programming', start = True, total = len(data))

		# Iterate over our chunks
		for (chunk_num, chunk) in enumerate(_chunker(trans_size, data)):
			# Fold the chunk back into a bytearray
			chunk_data = bytearray(b for b in chunk if b is not None)

			# Try to send the data
			if not self._send_dfu_download(chunk_data, chunk_num):
				log.error(f'DFU transaction failed, was unable to send any/all data for chunk {chunk_num}')
				return False
			# Update the upload task if we can
			if progress is not None:
				progress.update(prog_task, advance = len(chunk_data))

			# Let DFU chew on the chunk and settle a bit
			while self._get_dfu_state() != DFUState.DlSync:
				sleep(0.05)

			# Get the status of the chunk  upload
			_, state = self._get_dfu_status()

			if state != DFUState.DlSync:
				log.error(f'DFU State is {state} not DlSync, aborting')
				return False

		chunk_num += 1

		# Flush and make sure we go idle
		self._send_dfu_download(bytearray(), chunk_num)
		_, state = self._get_dfu_status()

		if state != DFUState.DFUIdle:
			log.error('Device did not go idle after upload')
			return False

		log.debug(f'Wrote {chunk_num} chunks to device')

		# Finally, clean up the progress bar if we were using it
		if progress is not None:
			progress.update(prog_task, completed = True)
			progress.remove_task(prog_task)

		return True

	# TODO(aki): Should this return type be an alias of a union of possible platform?
	def get_platform(self) -> type[SquishyPlatformType] | None:
		'''
		Get the type Torii platform definition for the currently attached device.

		Returns
		-------
		type[SquishyPlatformType] | None
			The type Torii platform definition for this device if found, otherwise None
		'''

		hwplat = f'rev{self.rev[0]}' # This is kinda lazy, but for now it works:tm:

		return AVAILABLE_PLATFORMS.get(hwplat, None)
