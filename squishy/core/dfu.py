# SPDX-License-Identifier: BSD-3-Clause

'''


'''

from enum                            import IntEnum, unique

from usb_construct.types.descriptors import InterfaceClassCodes, ApplicationSubclassCodes

__all__ = (
	'DFUState',
	'DFUStatus',
	'DFURequests',
	'DFU_CLASS',
)

@unique
class DFUState(IntEnum):
	AppIdle     = 0
	AppDetach   = 1
	DFUIdle     = 2
	DlSync      = 3
	DlBusy      = 4
	DlIdle      = 5
	DFUMFSync   = 6
	DFUManifest = 7
	DFUMFWait   = 8
	UpIdle      = 9
	Error       = 10

	def __str__(self) -> str:
		return {
			DFUState.AppIdle    : 'Device is running normal application',
			DFUState.AppDetach  : 'Device is running normal application, waiting to reset',
			DFUState.DFUIdle    : 'Device is in DFU mode',
			DFUState.DlSync     : 'Device has received a block',
			DFUState.DlBusy     : 'Device is programming a block',
			DFUState.DlIdle     : 'Device is processing a download',
			DFUState.DFUMFSync  : 'Device has received the final block',
			DFUState.DFUManifest: 'Device is manifesting',
			DFUState.DFUMFWait  : 'Device had programmed its memory',
			DFUState.UpIdle     : 'Device is processing an upload',
			DFUState.Error      : 'Device failed the vibe check',
		}.get(self, f'Unknown DFU State: {int(self)}')

	def __int__(self) -> int:
		return int(self)

@unique
class DFUStatus(IntEnum):
	Okay               = 0x00
	TargetError        = 0x01
	FileError          = 0x02
	WriteError         = 0x03
	EraseError         = 0x04
	CheckErasedError   = 0x05
	ProgramError       = 0x06
	VerifyError        = 0x07
	AddressError       = 0x08
	NotDoneError       = 0x09
	FirmwareError      = 0x0A
	VendorError        = 0x0B
	USBResetError      = 0x0C
	PowerOnResetError  = 0x0D
	UnknownError       = 0x0E
	StalledPacketError = 0x0F

	def __str__(self) -> str:
		return {
			DFUStatus.Okay              : 'No error condition is present',
			DFUStatus.TargetError       : 'File is not targeted for this device',
			DFUStatus.FileError         : 'File is for device but fails vendor vibe check',
			DFUStatus.WriteError        : 'Device is unable to write memory',
			DFUStatus.EraseError        : 'Memory erase function failed',
			DFUStatus.CheckErasedError  : 'Memory erase check failed',
			DFUStatus.ProgramError      : 'Program memory function failed',
			DFUStatus.VerifyError       : 'Programmed memory failed verification',
			DFUStatus.AddressError      : 'Cannot program memory, address out of range',
			DFUStatus.NotDoneError      : 'Received DFU_DNLOAD with length 0 but device does not think it\'s done',
			DFUStatus.FirmwareError     : 'Unknown error occurred',
			DFUStatus.StalledPacketError: 'Device stalled an unexpected request'
		}.get(self, f'Unknown DFU Status: {int(self)}')

	def __int__(self) -> int:
		return int(self)

@unique
class DFURequests(IntEnum):
	Detach    = 0
	Download  = 1
	Upload    = 2
	GetStatus = 3
	ClrStatus = 4
	GetState  = 5
	Abort     = 6

	def __int__(self) -> int:
		return int(self)


DFU_CLASS: tuple[int, int] = (
	int(InterfaceClassCodes.APPLICATION), int(ApplicationSubclassCodes.DFU)
)
