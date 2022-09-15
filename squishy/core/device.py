# SPDX-License-Identifier: BSD-3-Clause
import logging                      as log
from typing                         import (
	List, Tuple, Type, Union
)

import usb1

from usb_protocol.types             import (
	LanguageIDs
)
from usb_protocol.types.descriptors import (
	InterfaceClassCodes, ApplicationSubclassCodes
)


from ..config           import USB_VID, USB_PID_APPLICATION, USB_PID_BOOTLOADER

__all__ = (
	'SquishyHardwareDevice',
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
	_DFU_CLASS = (int(InterfaceClassCodes.APPLICATION), int(ApplicationSubclassCodes.DFU))


	def __init__(self, dev: usb1.USBDevice, serial: str, **kwargs) -> None:
		self._dev     = dev
		self.serial   = serial
		self.raw_ver  = dev.getbcdDevice()
		self.dec_ver  = self._decode_version(self.raw_ver)
		self.rev      = int(self.dec_ver)
		self.gate_ver = int((self.dec_ver - self.rev) * 100)

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

	def can_dfu(self) -> bool:
		''' Check to see if the Device can DFU '''
		return any(
			filter(
				lambda t: t == self._DFU_CLASS,
				map(
					lambda s: s.getClassTupple(),
					self._dev.iterSettings()
				)
			)
		)

	@classmethod
	def get_device(cls: Type['SquishyHardwareDevice'], serial: str = None) -> Union[None, 'SquishyHardwareDevice']:
		'''Get attached Squishy device.

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
	def enumerate(cls: Type['SquishyHardwareDevice']) -> List[Tuple[str, float, usb1.USBDevice]]:
		'''Enumerate attached devices

		Returns
		-------
		List[Tuple[str, float, usb1.USBDevice]]
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
						ver = cls._decode_version(dev.getbcdDevice())

						devices.append((sn, ver, dev))

						hndl.close()
					except usb1.USBError as e:
						log.error(f'Unable to open suspected squishy device: {e}')

		return devices


	def __repr__(self) -> str:
		return f'<SquishyHardwareDevice SN=\'{self.serial}\' REV=\'{self.rev}\' ADDR={self._dev.getDeviceAddress()}>'

	def __str__(self) -> str:
		return f'rev{self.rev} SN: {self.serial}'
