# SPDX-License-Identifier: BSD-3-Clause
import logging as log
from pathlib  import Path

import usb1

from usb_protocol.types import LanguageIDs

from ..config  import USB_VID, USB_PID_APPLICATION, USB_PID_BOOTLOADER

__all__ = (
	'SquishyHardwareDevice',
	'SquishyDeviceContainer',
)

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
	def __init__(self, dev, serial, **kwargs):
		self._dev = dev
		self.serial = serial
		self.rev = int(dev.getbcdDevice())

	def __del__(self):
		self._dev.close()

	@classmethod
	def enumerate(cls):
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
					except usb1.USBError:
						log.error('Unable to open suspected squishy device')

		return map(lambda d: SquishyDeviceContainer(d['dev'], d['sn']), devices)

	def to_device(self):
		'''Wrapper to device

		Returns
		-------
		SquishyHardwareDevice
			The hardware device that is represented by this USB device wrapper.

		'''
		return SquishyHardwareDevice(self._dev, self.serial)

	def __repr__(self):
		return f'<SquishyDeviceContainer SN=\'{self.serial}\' REV=\'{self.rev}\'>'

	def __str__(self):
		return self.__repr__()

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

	def __init__(self, dev, serial, **kwargs):
		self._dev   = dev
		self.serial = serial
		self.rev    = int(dev.getbcdDevice())


	def __repr__(self):
		return f'<SquishyHardwareDevice SN=\'{self.serial}\' REV=\'{self.rev}\' ADDR={self._dev.getDeviceAddress()}>'

	def __str__(self):
		return f'rev{self.rev} SN: {self.serial}'
