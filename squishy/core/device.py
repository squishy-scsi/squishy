# SPDX-License-Identifier: BSD-3-Clause
import logging          as log
from typing             import Iterable, Type, Union

import usb1

from usb_protocol.types import LanguageIDs

from ..config           import USB_VID, USB_PID_APPLICATION, USB_PID_BOOTLOADER

__all__ = (
	'SquishyHardwareDevice',
	'SquishyDeviceContainer',
)

class SquishyHardwareDevice:
	'''Squishy Hardware Device

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

	def __init__(self, dev: usb1.USBDevice, serial: str, **kwargs) -> None:
		self._dev   = dev
		self.serial = serial
		self.rev    = int(dev.getbcdDevice())


	def __repr__(self) -> str:
		return f'<SquishyHardwareDevice SN=\'{self.serial}\' REV=\'{self.rev}\' ADDR={self._dev.getDeviceAddress()}>'

	def __str__(self) -> str:
		return f'rev{self.rev} SN: {self.serial}'

class SquishyDeviceContainer:
	'''Squishy Device Container

	This class is a wrapper around the libusb1 USB device.

	Attributes
	----------
	serial : str
		The serial number of the device.

	rev : int
		The revision of the device.

	'''
	def __init__(self, dev: usb1.USBDevice, serial: str, **kwargs) -> None:
		self._dev = dev
		self.serial = serial
		self.rev = int(dev.getbcdDevice())

	def __del__(self):
		self._dev.close()

	@classmethod
	def enumerate(cls: Type['SquishyDeviceContainer']) -> Iterable['SquishyDeviceContainer']:
		'''Enumerate attached devices

		Returns
		-------
		Iterable[SquishyDeviceContainer]
			The collection of :py:class:`SquishyDeviceContainer` objects that match the
			enumeration critera.

		'''


		devices = list()

		with usb1.USBContext() as usb_ctx:
			for dev in usb_ctx.getDeviceIterator():
				vid = dev.getVendorID()
				pid = dev.getProductID()

				if vid == USB_VID and (pid == USB_PID_APPLICATION or pid == USB_PID_BOOTLOADER):
					try:
						hndl = dev.open()

						sn = hndl.getStringDescriptor(
							dev.getSerialNumberDescriptor(),
							LanguageIDs.ENGLISH_US
						)

						devices.append({
							'dev': dev,
							'sn': sn
						})

						hndl.close()
					except usb1.USBError as e:
						log.error(f'Unable to open suspected squishy device: {e}')

		return map(lambda d: SquishyDeviceContainer(d['dev'], d['sn']), devices)

	def to_device(self) -> SquishyHardwareDevice:
		'''Wrapper to device

		Returns
		-------
		SquishyHardwareDevice
			The hardware device that is represented by this USB device wrapper.

		'''
		return SquishyHardwareDevice(self._dev, self.serial)

	def __repr__(self) -> str:
		return f'<SquishyDeviceContainer SN=\'{self.serial}\' REV=\'{self.rev}\'>'

	def __str__(self) -> str:
		return self.__repr__()


def _get_device(args) -> Union[None, SquishyHardwareDevice]:
	'''Get attached Squishy device.

	Get the attached and selected squishy device if possible, or if only
	one is attached to the system use that one.

	Parameters
	----------
	args : argsparse.Namespace
		Any command line arguments passed.

	Returns
	-------
	None
		If no device is selected

	squishy.core.device.SquishyHardwareDevice
		The selected hardware if available.

	'''

	devices = list(SquishyDeviceContainer.enumerate())
	dev_count = len(devices)
	if dev_count > 1:
		if args.device is None:
			log.error(f'No device serial number specified, unable to pick from the {dev_count} devices.')
			log.info('Connected devices are:')
			for d in devices:
				log.info(f'\t{d.serial}')
			return None

		devs = list(filter(lambda d: d.serial == args.device, devices))

		if len(devs) == 0:
			log.error(f'No device with serial number \'{args.device}\'')
			log.info('Connected devices are:')
			for d in devices:
				log.info(f'\t{d.serial}')
			return None
		elif len(devs) > 1:
			log.error('Multiple Squishy devices with the same serial number found.')
			return None
		else:
			log.info(f'Found Squishy rev{devs[0].rev} \'{devs[0].serial}\'')
			return devs[0].to_device()
	elif dev_count == 1:
		if args.device is not None:
			if args.device != devices[0].serial:
				log.error(f'Connected Squishy has serial of \'{devices[0].serial}\', but device serial \'{args.device}\' was specified.')
				return None
		else:
			log.warning('No serial number specified.')
			log.warning('Using only Squishy attached to system.')
		log.info(f'Found Squishy rev{devices[0].rev} \'{devices[0].serial}\'')
		return devices[0].to_device()
	else:
		log.error('No Squishy devices attached to system.')
		return None
