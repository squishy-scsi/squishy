# SPDX-License-Identifier: BSD-3-Clause

from enum import (
	auto, unique, IntEnum
)

from typing import (
	Tuple, Union, Dict
)

__all__ = (
	'SCSIInterface',
	'SCSIElectrical',
	'SCSIClockMode',
	'SCSI_BUSSES',
)

__doc__ = '''\
'''


@unique
class SCSIStandard(IntEnum):
	''' The SCSI Standard '''

	SCSI1 = auto()
	''' SCSI 1 '''
	SCSI2 = auto()
	''' SCSI 2 '''
	SCSI3 = auto()
	''' SCSI 3 / SPI 2,3,4,5 '''

@unique
class SCSIInterface(IntEnum):
	''' The SCSI interface name '''

	SCSI1          = auto()
	''' SCSI 1 (1986) '''
	FastSCSI       = auto()
	'''Fast SCSI/SCSI 2 (1994) '''
	FastWideSCSI   = auto()
	''' Fast Wide SCSI/SCSI 2 (also SCSI-3/SPI-5) '''
	UltraSCSI      = auto()
	'''  '''
	UltraWideSCSI  = auto()
	''' '''
	Ultra2SCSI     = auto()
	''' '''
	Ultra2WideSCSI = auto()
	''' '''
	Ultra3SCSI     = auto()
	''' '''
	Ultra320SCSI   = auto()
	''' '''
	Ultra640SCSI   = auto()
	''' '''

@unique
class SCSIElectrical(IntEnum):
	''' Indicates the electrical mode of the SCSI Bus'''

	SE  = auto()
	''' Single Ended ~= 5v0'''
	HVD = auto()
	''' High Voltage Differential >=5v0 '''
	LVD = auto()
	''' Low Voltage Differential ~= 1v2 '''

@unique
class SCSIClockMode(IntEnum):
	''' Indicates the SCSI bus clock mode '''

	SDR = auto()
	''' Single Data Rate clock '''
	DDR = auto()
	''' Double Data Rate clock '''

SCSI_BUSSES : Dict[SCSIInterface, Dict[str, Union[Tuple[SCSIElectrical], int, Tuple[int, SCSIClockMode]]]] = {
	SCSIInterface.SCSI1: {
		'electrical': (SCSIElectrical.SE, SCSIElectrical.HVD),
		'width': 8,
		'speed': (5, SCSIClockMode.SDR)
	},
	SCSIInterface.FastSCSI: {
		'electrical': (SCSIElectrical.SE, SCSIElectrical.HVD),
		'width': 8,
		'speed': (10, SCSIClockMode.SDR)
	},
	SCSIInterface.FastWideSCSI: {
		'electrical': (SCSIElectrical.SE, SCSIElectrical.HVD),
		'width': 16,
		'speed': (10, SCSIClockMode.SDR)
	},
	SCSIInterface.UltraSCSI: {
		'electrical': (SCSIElectrical.SE, SCSIElectrical.HVD),
		'width': 8,
		'speed': (20, SCSIClockMode.SDR)
	},
	SCSIInterface.UltraWideSCSI: {
		'electrical': (SCSIElectrical.SE, SCSIElectrical.HVD),
		'width': 16,
		'speed': (20, SCSIClockMode.SDR)
	},
	SCSIInterface.Ultra2SCSI: {
		'electrical': (SCSIElectrical.HVD, SCSIElectrical.LVD),
		'width': 8,
		'speed': (40, SCSIClockMode.SDR)
	},
	SCSIInterface.Ultra2WideSCSI: {
		'electrical': (SCSIElectrical.HVD, SCSIElectrical.LVD),
		'width': 16,
		'speed': (40, SCSIClockMode.SDR)
	},
	SCSIInterface.Ultra3SCSI: {
		'electrical': (SCSIElectrical.LVD, ),
		'width': 16,
		'speed': (40, SCSIClockMode.DDR)
	},
	SCSIInterface.Ultra320SCSI: {
		'electrical': (SCSIElectrical.LVD, ),
		'width': 16,
		'speed': (80, SCSIClockMode.DDR)
	},
	SCSIInterface.Ultra640SCSI: {
		'electrical': (SCSIElectrical.LVD, ),
		'width': 16,
		'speed': (160, SCSIClockMode.DDR)
	}
}
