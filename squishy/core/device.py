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
	def __init__(self, dev, serial, **kwargs):
		self._dev = dev
		self.serial = serial
		self.rev = int(dev.getbcdDevice())

	def __del__(self):
		self._dev.close()

	@classmethod
	def enumerate(cls):
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
		return SquishyHardwareDevice(self._dev, self.serial)

	def __repr__(self):
		return f'<SquishyDeviceContainer SN=\'{self.serial}\' REV=\'{self.rev}\'>'

	def __str__(self):
		return self.__repr__()

class SquishyHardwareDevice:
	def __init__(self, dev, serial, **kwargs):
		self._dev   = dev
		self.serial = serial
		self.rev    = int(dev.getbcdDevice())


	def __repr__(self):
		return f'<SquishyHardwareDevice SN=\'{self.serial}\' REV=\'{self.rev}\' ADDR={self._dev.getDeviceAddress()}>'

	def __str__(self):
		return f'rev{self.rev} SN: {self.serial}'
