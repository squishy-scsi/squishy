# SPDX-License-Identifier: BSD-3-Clause

'''

'''

from enum import IntEnum, auto, unique

__all__ = (
	'SCSIInterface',
	'SCSIElectrical',
	'SCSIClockMode',
	'SCSI_BUSSES',
)

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

# TODO(aki): This should be cleaned up into more sane types/objects

SCSIBusSpeed      = tuple[float, SCSIClockMode]
''' The tuple of speed in MHz and clock mode (SDR vs DDR) '''
SCSIBusElectrical = tuple[SCSIElectrical, ...]
''' The rough electrical characteristics of the SCSI Bus '''
SCSIBusDefinition = dict[str, SCSIBusElectrical | int | SCSIBusSpeed]
''' A definition of the type of bus the given SCSI version supports '''

SCSI_BUSSES: dict[SCSIInterface, SCSIBusDefinition] = {
	SCSIInterface.SCSI1: {
		'electrical': (SCSIElectrical.SE, SCSIElectrical.HVD),
		'width': 8,
		'speed': (5e6, SCSIClockMode.SDR)
	},
	SCSIInterface.FastSCSI: {
		'electrical': (SCSIElectrical.SE, SCSIElectrical.HVD),
		'width': 8,
		'speed': (10e6, SCSIClockMode.SDR)
	},
	SCSIInterface.FastWideSCSI: {
		'electrical': (SCSIElectrical.SE, SCSIElectrical.HVD),
		'width': 16,
		'speed': (10e6, SCSIClockMode.SDR)
	},
	SCSIInterface.UltraSCSI: {
		'electrical': (SCSIElectrical.SE, SCSIElectrical.HVD),
		'width': 8,
		'speed': (20e6, SCSIClockMode.SDR)
	},
	SCSIInterface.UltraWideSCSI: {
		'electrical': (SCSIElectrical.SE, SCSIElectrical.HVD),
		'width': 16,
		'speed': (20e6, SCSIClockMode.SDR)
	},
	SCSIInterface.Ultra2SCSI: {
		'electrical': (SCSIElectrical.HVD, SCSIElectrical.LVD),
		'width': 8,
		'speed': (40e6, SCSIClockMode.SDR)
	},
	SCSIInterface.Ultra2WideSCSI: {
		'electrical': (SCSIElectrical.HVD, SCSIElectrical.LVD),
		'width': 16,
		'speed': (40e6, SCSIClockMode.SDR)
	},
	SCSIInterface.Ultra3SCSI: {
		'electrical': (SCSIElectrical.LVD, ),
		'width': 16,
		'speed': (40e6, SCSIClockMode.DDR)
	},
	SCSIInterface.Ultra320SCSI: {
		'electrical': (SCSIElectrical.LVD, ),
		'width': 16,
		'speed': (80e6, SCSIClockMode.DDR)
	},
	SCSIInterface.Ultra640SCSI: {
		'electrical': (SCSIElectrical.LVD, ),
		'width': 16,
		'speed': (160e6, SCSIClockMode.DDR)
	}
}
