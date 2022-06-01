# SPDX-License-Identifier: BSD-3-Clause
from enum import IntEnum, unique

__doc__ = '''\

This module contains the needed constants and machinery
for dealing with SCSI messages.

'''

__all__ = (
	'MessageCodes',
)

@unique
class MessageCodes(IntEnum):
	'''SCSI Message Codes

	SCSI Messages are to facilitate physical path management between
	a target and initiator.

	The only mandatory command is ``COMMAND_COMPLETE`` and as such
	any functional SCSI device only needs to support that message.

	'''

	COMMAND_COMPLETE   = 0x00
	'''Command Complete. Type: Mandatory, Dir: In.

	'''

	EXTENDED_MESSAGE  = 0x01
	''' Extended Message. Type: Optional, Dir: In/Out.

	'''

	SAV_DATA_PTR   = 0x02
	''' Save Data Pointer. Type: Optional, Dir: In.

	'''

	RESTORE_PTR    = 0x03
	'''Restore Pointers Type: Optional, Dir: In.

	'''

	DISCONNECT     = 0x04
	'''Disconnect. Type: Optional, Dir: In/Out.

	'''

	INT_DETECT_ERR = 0x05
	'''Initiator Detected Error. Type: Optional, Dir: Out.

	'''

	ABORT          = 0x06
	'''Abort. Type: Optional, Dir: Out.

	'''

	MESSAGE_REJECT = 0x07
	'''Message Reject. Type: Optional, Dir: In/Out.

	'''

	NOP            = 0x08
	'''No-Operation. Type: Optional, Dir: Out.

	'''

	MSG_PARITY_ERR = 0x09
	'''Message Parity Error. Type: Optional, Dir: Out.

	'''

	LINK_CMD_COM   = 0x0A
	'''Linked Command Complete. Type: Optional, Dir: In.

	'''

	LINK_CMD_COM_F = 0x0B
	'''Linked Command Completed (With Flag). Type: Optional, Dir: In.

	'''

	BUS_DEV_RESET  = 0x0C
	'''Bus Device Reset. Type: Optional, Dir: Out.

	'''

	RESERVED_START = 0x0D
	'''Start of Reserved Range. Type: Reserved, Dir: Unspecified.

	'''

	RESERVED_END   = 0x7F
	'''End of Reserved Range. Type: Reserved, Dir: Unspecified.

	'''

	IDENTIFY_START = 0x80
	'''Start of Identify Range. Type: Optional, Dir: In/Out.

	'''

	IDENTIFY_END   = 0xFF
	'''End of Identify Range. Type: Optional, Dir: In/Out.

	'''
