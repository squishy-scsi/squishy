# SPDX-License-Identifier: BSD-3-Clause
import logging as log
from pathlib  import Path

import usb1

from usb_protocol.types             import LanguageIDs
from usb_protocol.types.descriptors import InterfaceClassCodes, ApplicationSubclassCodes


__all__ = (
	'DFUDevice',
)

DFU_CLASS = (int(InterfaceClassCodes.APPLICATION), int(ApplicationSubclassCodes.DFU))

class DFUDevice:

	@classmethod
	def enumerate(cls, *, vid = None, pid = None, serial = None, boot_vid = None, boot_pid = None):
		with usb1.USBContext() as usb_ctx:
			devs = usb_ctx.getDeviceIterator()
			# Apply the filters to select DFU devices
			if vid is not None:

				devs = filter(
					lambda d: d.getVendorID() == vid,
					devs
				)
			if pid is not None:
				devs = filter(
					lambda d: d.getProductID() == pid,
					devs
				)

			if serial is not None:
				def match_sn(d):
					try:
						hndl = d.open()

						sn = hndl.getStringDescriptor(
							d.getSerialNumberDescriptor(),
							LanguageIDs.ENGLISH_US
						)

						hndl.close()

						return sn == serial
					except:
						log.error(f'Unable to open device')
						return False

				devs = filter(match_sn, devs)

			# Filter out devices that don't support DFU
			def can_dfu(d):
				return any(
					filter(
						lambda t: t == DFU_CLASS,
						map(
							lambda s: s.getClassTupple(),
							d.iterSettings()
						)
					)
				)

			return list(
				map(
					lambda d: DFUDevice(d, vid, pid, serial, boot_vid, boot_pid),
					filter(can_dfu, devs)
				)
			)

	def _update_serial(self):
		hndl = self._dev.open()

		self.serial = hndl.getStringDescriptor(
			self._dev.getSerialNumberDescriptor(),
			LanguageIDs.ENGLISH_US
		)

		hndl.close()

	def __init__(self, dev, vid = None, pid = None, serial = None, boot_vid = None, boot_pid = None):
		self._dev   = dev
		self.vid    = vid if vid is not None else dev.getVendorID()
		self.pid    = pid if pid is not None else dev.getProductID()
		self.serial = serial
		self.boot_vid = boot_vid
		self.boot_pid = boot_pid

		if serial is None:
			self._update_serial()



	def __repr__(self):
		return f'<DFUDevice VID={self.vid:04x} PID={self.pid:04x} SN=\'{self.serial}\'>'

	def __str__(self):
		return f'{self!r}'

	def __del__(self):
		self._dev.close()
