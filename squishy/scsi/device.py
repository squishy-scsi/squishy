# SPDX-License-Identifier: BSD-3-Clause

from enum import IntEnum, unique

__doc__ = '''\

'''

__all__ = (
	'PeripheralDeviceType',
)

@unique
class PeripheralDeviceType(IntEnum):
	''' The type of device a peripheral iss '''

	DirectAccess          = 0x00
	''' Direct-access devices *(e.g. Magnetic Disk)* '''

	SequentialAccess      = 0x01
	''' Sequential-access devices *(e.g. Magnetic Tape)* '''

	Printer               = 0x02
	''' Printer-like devices '''

	Processor             = 0x03
	''' Processors '''

	WORM                  = 0x04
	''' Write-Once-Read-Many devices '''

	ReadOnlyDirectAccess  = 0x05
	''' Read-only Direct-access devices '''

	ReservedStart         = 0x06
	''' Start of the Reserved section '''

	ReservedEnd           = 0x7E
	''' End of the Reserved section '''

	LogicalUnitNotPresent = 0x7F
	''' Logical unit is not present '''

	VendorUniqueStart     = 0x80
	''' Start of the Vendor Unique section '''

	VendorUniqueEnd       = 0xFF
	''' End of the Vendor Unique section '''
