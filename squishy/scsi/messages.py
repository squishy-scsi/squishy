# SPDX-License-Identifier: BSD-3-Clause
from enum import IntEnum, unique

__all__ = (
	'MessageCodes',
	'ExtendedMessageCodes',
)

@unique
class MessageCodes(IntEnum):
	'''SCSI Message Codes

	SCSI Messages are to facilitate physical path management between
	a target and initiator.

	The only mandatory command is :py:const:`COMMAND_COMPLETE` and as such
	any functional SCSI device only needs to support that message.

	There are two directions a message may be sent in, ``in`` and ``out``. With
	messages that are ``in`` the flow is from the target to the initiator. With
	``out`` messages the flow is from the initiator to the target.

	'''

	COMMAND_COMPLETE   = 0x00
	'''Command Complete (Mandatory, In).

	This message is sent to the Initiator to indicate that the execution of a command
	or series of linked commands has been terminated and that a valid status has
	been sent to the initiator.

	After this message is sent the Initiator should go into the BUS FREE phase.

	.. note:: The command may have been successfully or unsuccessfully completed

	'''

	EXTENDED_MESSAGE  = 0x01
	''' Extended Message (Optional, In/Out).

	This message indicates that the following data is an extended message.
	See :py:class:`ExtendedMessageCodes` for more details on extended messages.

	'''

	SAVE_DATA_PTR   = 0x02
	''' Save Data Pointer (Optional, In).

	This message directs the Initiator to save a copy of the current active data
	pointer for the currently attached LUN.

	'''

	RESTORE_PTR    = 0x03
	'''Restore Pointers (Optional, In).

	This message directs the Initiator to restore the recently saved pointers
	to the active state.

	Pointers to the command, data, and status locations for the LUN shall be restored
	to the active pointers.

	Commands and status pointers shall be restored to the beginning of the current
	command and status areas.

	The data pointer shall be restored to the value at the beginning of the data
	area in the absence of a :py:const:`SAVE_DATA_PTR` message, or to the value of the pointer
	from the last :py:const:`SAVE_DATA_PTR` message that was issued to the LUN.

	'''

	DISCONNECT     = 0x04
	'''Disconnect (Optional, In/Out).

	When sent from a Target, this message informs the Initiator that the present
	physical path will invalidated, and that a later reconnection will be needed
	in order to finish the current operation.

	If BUS FREE is detected by the Initiator in any case other than a RESET condition
	and it did not receive a disconnect or command complete, it is considered a
	fatal error condition.

	If the target caused the error intentionally, it will clear the current command.

	This message shall not cause the initiator to save the data pointer.

	.. note::

		If one or more :py:const:`DISCONNECT` messages are used to segment a long data transfer
		into two or more smaller transfers, then a :py:const:`SAVE_DATA_PTR` must be issued
		before each :py:const:`DISCONNECT` message.

	'''

	INT_DETECT_ERR = 0x05
	'''Initiator Detected Error (Optional, Out).

	This message is sent from the Initiator to indicate to the target that
	an error has occurred that not prevent the target from re-attempting
	the operation.

	.. warning::

		Integrity of the pointers are not assured. However a :py:const:`RESTORE_PTR`
		message or a disconnect followed by a reconnect, shall cause the pointers
		to be restored to their defined prior state.

	'''

	ABORT          = 0x06
	'''Abort (Optional, Out).

	This message is sent from the Initiator to clear the current operation. If
	a LUN has been identified, then all pending data and status for the initiator
	issuing the message from the effected LUN shall be cleared. The target will then
	go into BUS FREE.

	Pending data and status for any other Initiators on the bus shall not be cleared.

	If a LUN has not been identified, then the target will go into the BUS FREE phase.

	No status or ending message shall be sent for the operation.

	.. note::

		It is not an error for this message to be sent to a LUN that
		is not currently performing an operation for the sending Initiator.

	'''

	MESSAGE_REJECT = 0x07
	'''Message Reject (Optional, In/Out).

	This message is sent from either the Target or Initiator to indicate
	that the previous message was invalid or not implemented.

	When an Initiator sends this message, it asserts the ATN signal prior to
	releasing ACK for the REQ/ACK handshake of the message that is being rejected.

	In the case of a Target, it moves to the MESSAGE IN phase and sends this message
	prior to requesting any additional message bytes from the Initiator. This ensures
	that the Initiator can check to see if the message is rejected or not before sending
	the remaining bytes of the message.

	.. note::

		This message must be implemented if any other optional messages
		are implemented.

	'''

	NOP            = 0x08
	'''No-Operation (Optional, Out).

	This message is sent to a Target in response to a request of the
	Initiator when there is no other messages to be sent.

	'''

	MSG_PARITY_ERR = 0x09
	'''Message Parity Error (Optional, Out).

	This message is sent from an Initiator to the Target where
	one or more bytes of the last message had a parity error.

	To send this message, the Initiator must indicate its intentions to do so.
	It does this by the same method as the :py:const:`MESSAGE_REJECT` message.

	'''

	LINK_CMD_COM   = 0x0A
	'''Linked Command Complete (Optional, In).

	.. note::

		This command is almost entirely identical to :py:const:`LINK_CMD_COM_F` with
		the only difference being that the flag bit of the command is not set.

	This message is sent to an Initiator to indicate that the execution of a linked
	command has completed and the status for it has been sent. The Initiator will
	then set the pointers to the initial state for the next linked command.

	'''

	LINK_CMD_COM_F = 0x0B
	'''Linked Command Completed With Flag (Optional, In).

	.. note::

		This command is almost entirely identical to :py:const:`LINK_CMD_COM` with
		the only difference being that the flag bit of the command is set.

	This message is sent to an Initiator to indicate that the execution of a linked
	command with the flag bit set has completed and the status for it has been sent. The Initiator will
	then set the pointers to the initial state for the next linked command.

	This message is typically used to cause an interrupt in the Initiator between two
	linked commands.

	'''

	BUS_DEV_RESET  = 0x0C
	'''Bus Device Reset (Optional, Out).

	This message is sent to a Target to tell it to clear all current commands on
	that SCSI device. It forces the SCSI device to an initial clean state with no
	pending operations for any Initiator on the bus.

	When the Target receives this message, it must go to the BUS FREE phase.

	'''

	RESERVED_START = 0x0D
	'''Start of Reserved Range.

	The message codes between :py:const:`RESERVED_START` and :py:const`RESERVED_END`
	are all reserved for future possible standards.

	'''

	RESERVED_END   = 0x7F
	'''End of Reserved Range.

	The message codes between :py:const:`RESERVED_START` and :py:const`RESERVED_END`
	are all reserved for future possible standards.

	'''

	IDENTIFY_START = 0x80
	'''Start of Identify Range (Optional, In/Out).

	The message codes between :py:const:`IDENTIFY_START` and :py:const`IDENTIFY_END`
	are sent by either the Target or the Initiator to establish a physical path between
	a Target and Initiator for a particular LUN.

	These messages have a special format that sets them apart from all other messages as
	illustrated below.

	+-------+-------+-------+-------+-------+-------+-------+-------+
	|   7   |   6   |   5   |   4   |   3   |   2   |   1   |   0   |
	+=======+=======+=======+=======+=======+=======+=======+=======+
	| ``1`` | ``I`` |.. centered:: Reserved | .. centered:: LUN     |
	+-------+-------+-------+-------+-------+-------+-------+-------+

	Bit ``7`` Is always set to a ``1`` to indicate that this is an IDENTIFY message.

	Bit ``6`` Is only set to one if the message is coming from an Initiator, this is to
	indicate that it supports disconnection and reconnection.

	Bits ``5`` thru ``3`` are reserved for future use.

	Bits ``2`` thru ``0`` are the LUN number.

	.. warning::

		Only one LUN can be identified for any one selection sequence. The bus must
		be released before a new IDENTIFY message with a new LUN can be issued.

	.. note::

		When sent to an Initiator from a Target during a reconnection, there is an implied
		:py:const:`RESTORE_PTR` message which should be completed by the Initiator before
		the completion of this message.

	'''

	IDENTIFY_END   = 0xFF
	'''End of Identify Range (Optional, In/Out).

	The message codes between :py:const:`IDENTIFY_START` and :py:const`IDENTIFY_END`
	are sent by either the Target or the Initiator to establish a physical path between
	a Target and Initiator for a particular LUN.

	'''

@unique
class ExtendedMessageCodes(IntEnum):
	'''Message Codes for Extended SCSI Messages


	Extended SCSI Messages roughly follow this format:

	+---------+----------+---------------------+
	|   Byte  |  Value   | Description         |
	+=========+==========+=====================+
	|  ``0``  | ``0x01`` | Extended Message ID |
	+---------+----------+---------------------+
	|  ``1``  | ``l``    | Message Length      |
	+---------+----------+---------------------+
	|  ``2``  | ``c``    | Message Code        |
	+---------+----------+---------------------+
	|  ``3``  | ``-``    | Message Args Start  |
	+---------+----------+---------------------+
	| ``l+1`` | ``-``    | Message Args End    |
	+---------+----------+---------------------+

	.. note:: The message length field is the number of bytes **after** and including that field.

	'''

	MODIFY_DATA_PTR = 0x00,
	'''Modify Data Pointer (Optional).

	This extended message is sent to the initiator from the target. It
	asks the initiator to add the signed 4 byte integer argument to the
	current data pointer.

	+---------+----------+---------------------+
	|   Byte  |  Value   | Description         |
	+=========+==========+=====================+
	|  ``0``  | ``0x01`` | Extended Message ID |
	+---------+----------+---------------------+
	|  ``1``  | ``0x05`` | Message Length      |
	+---------+----------+---------------------+
	|  ``2``  | ``0x00`` | Message Code        |
	+---------+----------+---------------------+
	|  ``3``  | ``o``    | Offset (MSB)        |
	+---------+----------+---------------------+
	|  ``4``  | ``o``    | Offset              |
	+---------+----------+---------------------+
	|  ``5``  | ``o``    | Offset              |
	+---------+----------+---------------------+
	|  ``6``  | ``o``    | Offset (LSB)        |
	+---------+----------+---------------------+

	'''

	SYNC_DATA_XFR_REQ = 0x01,
	'''Synchronous Data Transfer Request (Optional).

	.. todo:: Document better

	+---------+----------+---------------------+
	|   Byte  |  Value   | Description         |
	+=========+==========+=====================+
	|  ``0``  | ``0x01`` | Extended Message ID |
	+---------+----------+---------------------+
	|  ``1``  | ``0x03`` | Message Length      |
	+---------+----------+---------------------+
	|  ``2``  | ``0x01`` | Message Code        |
	+---------+----------+---------------------+
	|  ``3``  | ``t``    | Transfer Period     |
	+---------+----------+---------------------+
	|  ``4``  | ``x``    | REQ/ACK Offset      |
	+---------+----------+---------------------+

	.. note:: The transfer period is in 4ns increments.


	'''

	EXTENDED_IDENT = 0x02,
	'''Extended Identify Command (Optional).

	This extended message may be sent by a target or initiator, and
	may be used in conjunction with the normal ``IDENTIFY`` message
	to allow for an extended range for LUN addressing.

	Using the Sub-LUN byte to add 256 sub units to the target
	LUN allows for targets to have up to 2048 addressable units.

	+---------+----------+---------------------+
	|   Byte  |  Value   | Description         |
	+=========+==========+=====================+
	|  ``0``  | ``0x01`` | Extended Message ID |
	+---------+----------+---------------------+
	|  ``1``  | ``0x02`` | Message Length      |
	+---------+----------+---------------------+
	|  ``2``  | ``0x02`` | Message Code        |
	+---------+----------+---------------------+
	|  ``3``  | ``n``    | Sub-LUN Number      |
	+---------+----------+---------------------+


	'''

	RESERVED_START = 0x03
	'''Start of Reserved Range.

	The message codes between :py:const:`RESERVED_START` and :py:const`RESERVED_END`
	are all reserved for future possible standards.

	'''

	RESERVED_END   = 0x7F
	'''End of Reserved Range.

	The message codes between :py:const:`RESERVED_START` and :py:const`RESERVED_END`
	are all reserved for future possible standards.

	'''

	VENDOR_START = 0x80
	'''Start of Vendor Reserved Range.

	The message codes between :py:const:`VENDOR_START` and :py:const`VENDOR_END`
	are all for vendor-specific extended messages.

	'''

	VENDOR_END   = 0xFF
	'''End of Vendor Reserved Range.

	The message codes between :py:const:`VENDOR_START` and :py:const`VENDOR_END`
	are all for vendor-specific extended messages.

	'''
