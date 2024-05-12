# SPDX-License-Identifier: BSD-3-Clause
import logging                           as log

from typing                              import Iterable, Type
from time                                import sleep
from datetime                            import datetime

from usb1                                import USBContext, USBDevice, USBError, USBConfiguration
from usb1.libusb1                        import (
	LIBUSB_REQUEST_TYPE_CLASS, LIBUSB_RECIPIENT_INTERFACE, LIBUSB_ERROR_IO, LIBUSB_ERROR_NO_DEVICE
)

from usb_construct.types                 import LanguageIDs
from usb_construct.types.descriptors.dfu import FunctionalDescriptor

from rich.progress                       import Progress

from .dfu_types                          import DFU_CLASS, DFURequests, DFUState, DFUStatus
from ..config                            import USB_VID, USB_PID_APPLICATION, USB_PID_BOOTLOADER

__all__ = (
	'SquishyHardwareDevice',
)

# Due to how libusb1 works and how we're using it
# This needs to be global so it can live for the
# life of the runtime
_USB_CTX: USBContext | None = None

class SquishyHardwareDevice:
	'''
	Squishy Hardware Device

	This class represents and abstracted Squishy hardware device, exposing a common
	and stable API for applets to interact with the hardware on.

	Parameters
	----------
	dev : usb1.USBDevice
		The USB device handle for the hardware platform.

	serial : str
		The serial number of the device.

	Attributes
	----------
	serial : str
		The serial number of the device.

	rev : int
		The revision of the hardware of the device.

	'''

	def _get_dfu_interface(self, cfg: USBConfiguration | None) -> int | None:
		''' Get the interface ID that matches the ``_DFU_CLASS`` '''
		if self._dfu_iface is None and cfg is not None:
			for cfg in self._dev.iterConfigurations():
				for iface in cfg:
					for ifset in iface:
						if ifset.getClassTuple() == DFU_CLASS:
							self._dfu_cfg: int = cfg.getConfigurationValue()
							self._dfu_iface: int = ifset.getNumber()
							if self._usb_hndl.getConfiguration() != self._dfu_cfg:
								self._usb_hndl.setConfiguration(self._dfu_cfg)
							return self._dfu_iface

		return self._dfu_iface

	def _get_dfu_status(self) -> tuple[DFUStatus, DFUState]:
		''' Get DFU Status '''
		cfg = self._usb_hndl.getConfiguration()
		interface_id = self._get_dfu_interface(cfg)
		if interface_id is None:
			raise RuntimeError('Unable to get interface ID for DFU Device')

		self._ensure_iface_claimed(interface_id)

		data: bytearray | None = self._usb_hndl.controlRead(
			LIBUSB_REQUEST_TYPE_CLASS | LIBUSB_RECIPIENT_INTERFACE,
			DFURequests.GetStatus,
			0,
			interface_id,
			6,
			self._timeout
		)
		if data is None:
			raise RuntimeError(f'Unable to send control request DFU_GETSTATUS to interface {interface_id}')

		return (DFUStatus(data[0]), DFUState(data[4]))

	def _get_dfu_state(self) -> DFUState:
		''' Get the DFU State '''
		cfg = self._usb_hndl.getConfiguration()
		interface_id = self._get_dfu_interface(cfg)
		if interface_id is None:
			raise RuntimeError('Unable to get interface ID for DFU Device')

		self._ensure_iface_claimed(interface_id)

		data: bytearray | None = self._usb_hndl.controlRead(
			LIBUSB_REQUEST_TYPE_CLASS | LIBUSB_RECIPIENT_INTERFACE,
			DFURequests.GetState,
			0,
			interface_id,
			1,
			self._timeout
		)
		if data is None:
			raise RuntimeError(f'Unable to send control request DFU_GETSTATE to interface {interface_id}')

		return DFUState(data[0])

	def _send_dfu_detach(self) -> bool:
		''' Invoke a DFU Detach '''
		cfg = self._usb_hndl.getConfiguration()
		interface_id = self._get_dfu_interface(cfg)
		if interface_id is None:
			raise RuntimeError('Unable to get interface ID for DFU Device')

		self._ensure_iface_claimed(interface_id)

		try:
			sent: int = self._usb_hndl.controlWrite(
				LIBUSB_REQUEST_TYPE_CLASS | LIBUSB_RECIPIENT_INTERFACE,
				DFURequests.Detach,
				0,
				interface_id,
				bytearray(),
				self._timeout
			)
		except USBError as error:
			# If the error is one of the not-actually-an-error errors caused by the device rebooting, palm it off
			if error.value in (LIBUSB_ERROR_IO, LIBUSB_ERROR_NO_DEVICE):
				self._claimed_interfaces.remove(self._dfu_iface)
				sent = 0
			# Otherwise propagate the error properly
			else:
				raise BufferError(
					f'Unable to send control request for DFU_DETACH to interface {interface_id}'
				) from error

		self._ensure_iface_released(interface_id)
		return sent == 0

	def _get_dfu_altmodes(self) -> dict[int, str]:
		''' Get the DFU alt-modes '''
		log.debug('Getting DFU alt-modes')

		cfg = self._usb_hndl.getConfiguration()
		interface_id  = self._get_dfu_interface(cfg)
		if interface_id is None:
			raise RuntimeError('Unable to get interface ID for DFU Device')

		alt_modes: dict[int, str] = dict()

		for cfg in self._dev.iterConfigurations():
			for iface in cfg:
				for ifset in iface:
					if ifset.getNumber() == interface_id:
						alt_modes[
							ifset.getAlternateSetting()
						] = self._usb_hndl.getStringDescriptor(
							ifset.getDescriptor(),
							LanguageIDs.ENGLISH_US
						)

		log.debug(f'Found {len(alt_modes.keys())} alt-modes')

		return alt_modes

	def _get_dfu_tx_size(self) -> int | None:
		''' Get the DFU transaction size '''
		cfg = self._usb_hndl.getConfiguration()
		interface_id = self._get_dfu_interface(cfg)
		if interface_id is None:
			raise RuntimeError('Unable to get interface ID for DFU Device')

		for cfg in self._dev.iterConfigurations():
			for iface in cfg:
				for ifset in iface:
					if ifset.getNumber() == interface_id:
						ext = ifset.getExtra()
						assert len(ext) == 1, '*sadface*'
						func_desc = FunctionalDescriptor.parse(ext[0])
						return func_desc.wTransferSize

		return None

	def _enter_dfu_mode(self) -> bool:
		''' Enter the DFU bootloader '''
		if self._get_dfu_state() == DFUState.AppIdle:
			log.debug('Device is in Application mode, attempting to detach')
			self._send_dfu_detach()
			self._usb_hndl.close()
			self._dev.close()
			self._dfu_iface = None

			devices = list()

			log.info(f'Waiting for device \'{self.serial}\' to come back')
			sleep(self._timeout / 1000)
			while len(devices) == 0:
				devices = list(filter(
					lambda dev: dev[0] == self.serial,
					SquishyHardwareDevice.enumerate()
				))

			log.debug('Device came back, re-caching device handle')
			self._dev: USBDevice = devices[0][2]
			self._usb_hndl       = self._dev.open()

		state = self._get_dfu_state()

		log.debug('Checking DFU state')
		if state != DFUState.DFUIdle:
			log.error(f'Device was in improper DFU state: {state}')
			return False
		log.debug('Device is in DFUIdle, ready for operations')
		return True

	def _send_dfu_download(self, data: bytearray, chunk_num: int) -> bool:
		''' Send a DFU Download transaction '''

		cfg = self._usb_hndl.getConfiguration()
		interface_id = self._get_dfu_interface(cfg)
		if interface_id is None:
			raise RuntimeError('Unable to get interface ID for DFU Device')

		self._ensure_iface_claimed(interface_id)

		sent: int = self._usb_hndl.controlWrite(
			LIBUSB_REQUEST_TYPE_CLASS | LIBUSB_RECIPIENT_INTERFACE,
			DFURequests.Download,
			chunk_num,
			interface_id,
			data,
			self._timeout
		)


		return sent == len(data)

	def _ensure_iface_claimed(self, id: int) -> None:
		if id not in self._claimed_interfaces:
			self._usb_hndl.claimInterface(id)
			self._claimed_interfaces.append(id)

	def _ensure_iface_released(self, id: int) -> None:
		if id in self._claimed_interfaces:
			self._usb_hndl.releaseInterface(id)
			self._claimed_interfaces.remove(id)


	def can_dfu(self) -> bool:
		''' Check to see if the Device can DFU '''
		log.debug('Checking to see if device is DFU capable')
		return any(
			filter(
				lambda t: t == DFU_CLASS,
				map(
					lambda s: s.getClassTupple(),
					self._dev.iterSettings()
				)
			)
		)

	def __init__(self, dev: USBDevice, serial: str, timeout: int = 2500, **kwargs) -> None:
		self._dev      = dev
		self._usb_hndl = self._dev.open()
		if not self.can_dfu():
			raise RuntimeError(f'The device {dev.getVendorID():04x}:{dev.getProductID():04x} @ {dev.getBusNumber()} is not DFU capable.')
		self._timeout: int          = timeout
		self._dfu_cfg: int | None = None
		self._dfu_iface: int | None = None
		self.serial   = serial
		self.raw_ver  = dev.getbcdDevice()
		self.dec_ver  = self._decode_version(self.raw_ver)
		self.rev      = int(self.dec_ver)
		self.gate_ver = int((self.dec_ver - self.rev) * 100)
		self._claimed_interfaces = list()

	def __del__(self) -> None:
		self._usb_hndl.close()
		self._dev.close()

	@staticmethod
	def _decode_version(bcd: int) -> float:
		i = bcd >> 8
		i = ((i >> 4) * 10) + (i & 0xf)
		d = bcd & 0xff
		d = ((d >> 4) * 10) + (d & 0xf)
		return i + (d / 100)

	def _update_serial(self) -> None:
		''' Update the serial number from the attached device '''
		hndl = self._dev.open()

		self.serial = hndl.getStringDescriptor(
			self._dev.getSerialNumberDescriptor(),
			LanguageIDs.ENGLISH_US
		)

		hndl.close()

	@staticmethod
	def make_serial() -> str:
		'''
		Make a new serial number string.

		The default serial number is the current time and date
		in UTC in an ISO 8601-like format.

		Returns
		-------
		str
			The new serial number

		'''
		return datetime.utcnow().strftime(
			'%Y%m%dT%H%M%SZ'
		)

	@classmethod
	def get_device(cls: Type['SquishyHardwareDevice'], serial: str = None) -> Type['SquishyHardwareDevice'] | None:
		'''
		Get attached Squishy device.

		Get the attached and selected squishy device if possible, or if only
		one is attached to the system use that one.

		Parameters
		----------
		serial : str
			The serial number if any.

		Returns
		-------
		None
			If no device is selected

		squishy.core.device.SquishyHardwareDevice
			The selected hardware if available.

		'''
		def print_devtree() -> None:
			from rich.tree import Tree
			from rich      import print

			dev_tree = Tree(
				'[green]Attached Devices[/]',
				guide_style = 'blue'
			)
			for idx, tup in enumerate(devices):
				node = dev_tree.add(f'[magenta]{idx}[/]')
				node.add(f'SN:  [bright_green]{tup[0]}[/]')
				node.add(f'Rev: [bright_cyan]{int(tup[1])}[/]')
			print(dev_tree)

		devices   = SquishyHardwareDevice.enumerate()
		dev_count = len(devices)

		if dev_count > 1:
			if serial is None:
				log.error(f'No serial number specified, unable to pick from {dev_count} attached devices.')
				print_devtree()
				return None

			found = list(filter(lambda sn, _, __: sn == serial, devices))

			if len(found) > 1:
				log.error(f'Multiple devices matching serial number \'{serial}\'')
				return None
			elif len(found) == 0:
				log.error(f'No devices matching serial number \'{serial}\'')
				print_devtree()
			else:
				dev = SquishyHardwareDevice(found[2], found[0])
				log.info(f'Found Squishy rev{dev.rev} matching serial \'{dev.serial}\'')
				return dev
		elif dev_count == 1:
			found = devices[0]
			if serial is not None:
				if serial != found[0]:
					log.error(f'Connected Squishy has serial number \'{found[0]}\' but \'{serial}\' was specified')
					return None
			else:
				log.warn('No serial specified')
				log.info('Using only Squishy attached to system')

			dev = SquishyHardwareDevice(found[2], found[0])
			log.info(f'Found Squishy rev{dev.rev} matching serial \'{dev.serial}\'')
			return dev
		else:
			log.error('No Squishy devices found attached to system')
			return None


	@classmethod
	def enumerate(cls: Type['SquishyHardwareDevice']) -> list[tuple[str, float, USBDevice]]:
		'''
		Enumerate attached devices

		Returns
		-------
		List[Tuple[str, float, usb1.USBDevice]]
			The collection of :py:class:`SquishyDeviceContainer` objects that match the
			enumeration critera.

		'''
		global _USB_CTX

		devices = list()

		if _USB_CTX is None:
			_USB_CTX = USBContext()

		for dev in _USB_CTX.getDeviceIterator():
			vid = dev.getVendorID()
			pid = dev.getProductID()

			if vid == USB_VID and (pid == USB_PID_APPLICATION or pid == USB_PID_BOOTLOADER):
				try:
					hndl = dev.open()

					sn = hndl.getStringDescriptor(
						dev.getSerialNumberDescriptor(),
						LanguageIDs.ENGLISH_US
					)
					ver = cls._decode_version(dev.getbcdDevice())

					devices.append((sn, ver, dev))
					hndl.close()
				except USBError as e:
					log.error(f'Unable to open suspected squishy device: {e}')
					log.error('Maybe check your udev rules?')
		return devices

	def get_altmodes(self):
		return self._get_dfu_altmodes()

	def reset(self) -> bool:
		''' Reset the device '''
		return self._send_dfu_detach()

	def upload(self, data: bytearray, slot: int, progress: Progress | None = None) -> bool:
		''' Push Firmware/Gateware to device '''
		if not self._enter_dfu_mode():
			return False

		log.info(f'Starting DFU upload of {len(data)} bytes to slot {slot}')

		cfg = self._usb_hndl.getConfiguration()
		interface_id = self._get_dfu_interface(cfg)
		if interface_id is None:
			raise RuntimeError('Unable to get interface ID for DFU Device')

		self._ensure_iface_claimed(interface_id)

		log.debug(f'Setting interface {interface_id} alt to {slot}')
		self._usb_hndl.setInterfaceAltSetting(interface_id, slot)


		def chunker(size: int, data: Iterable):
			from itertools import zip_longest
			return zip_longest(*[iter(data)]*size)

		tx_size = self._get_dfu_tx_size()
		if tx_size is None:
			raise RuntimeError('Unable to get DFU transaction size for device')


		prog_task = progress.add_task('Programming', start = True, total = len(data))

		log.debug(f'DFU Transfer size is {tx_size}')

		for chunk_num, chunk in enumerate(chunker(tx_size, data)):
			chunk_data = bytearray(b for b in chunk if b is not None)
			if not self._send_dfu_download(chunk_data, chunk_num):
				log.error(f'DFU Transaction failed, did not sent all data for chunk {chunk_num}')
				return False
			progress.update(prog_task, advance = len(chunk_data))
			while self._get_dfu_state() != DFUState.DlSync:
				sleep(0.05)

			status, state = self._get_dfu_status()
			if state != DFUState.DlSync:
				log.error(f'DFU State is {state} not DlIdle, aborting')
				return False

		chunk_num += 1

		log.debug(f'Wrote {chunk_num} chunks to device')
		assert self._send_dfu_download(bytearray(), chunk_num), 'Uoh nowo'
		_, state = self._get_dfu_status()

		if state != DFUState.DFUIdle:
			log.error('Device did not go idle after upload')
			return False
		progress.update(prog_task, completed = True)
		return True


	def download(self, slot: int) -> bytearray | None:
		''' Pull Firmware/Gateware from device (if supported) '''
		return None

	def __repr__(self) -> str:
		return f'<SquishyHardwareDevice SN=\'{self.serial}\' REV=\'{self.rev}\' ADDR={self._dev.getDeviceAddress()}>'

	def __str__(self) -> str:
		return f'rev{self.rev} SN: {self.serial}'
