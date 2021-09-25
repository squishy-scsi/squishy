# SPDX-License-Identifier: BSD-3-Clause
from enum import IntEnum, unique

__all__ = (
	'MessageCodes',
)

@unique
class MessageCodes(IntEnum):
	CMD_COMPLETE   = 0x00 # Type: Mandatory Dir: In
	EXTND_MESSAGE  = 0x01 # Type: Optional  Dir: In/Out
	SAV_DATA_PTR   = 0x02 # Type: Optional  Dir: In
	RESTORE_PTR    = 0x03 # Type: Optional  Dir: In
	DISCONNECT     = 0x04 # Type: Optional  Dir: In/Out
	INT_DETECT_ERR = 0x05 # Type: Optional  Dir:    Out
	ABORT          = 0x06 # Type: Optional  Dir:    Out
	MESSAGE_REJECT = 0x07 # Type: Optional  Dir: In/Out
	NOP            = 0x08 # Type: Optional  Dir:    Out
	MSG_PARITY_ERR = 0x09 # Type: Optional  Dir:    Out
	LINK_CMD_COM   = 0x0A # Type: Optional  Dir: In
	LINK_CMD_COM_F = 0x0B # Type: Optional  Dir: In
	BUS_DEV_RESET  = 0x0C # Type: Optional  Dir:    Out
	RESERVED_START = 0x0D # Type: Reserved  Dir: ¯\_(ツ)_/¯
	RESERVED_END   = 0x7F # Type: Reserved  Dir: ¯\_(ツ)_/¯
	IDENTIFY_START = 0x80 # Type: Optional  Dir: In/Out
	IDENTIFY_END   = 0xFF # Type: Optional  Dir: In/Out
