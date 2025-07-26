# SPDX-License-Identifier: BSD-3-Clause

'''
This module contains the Squishy-specific implementation of the ``LINKTYPE_PARALLEL_SCSI`` framing
format for PCAPNG files, as described here: https://github.com/squishy-scsi/wireshark-scsi/blob/main/docs/LINKTYPE_PARALLEL_SCSI.md

It is part of the living/reference implementation, as it is the only emitter of the frame type as of writing
and as such is acting the driving force behind any changes or updates that need to be made to the
format as it evolves.


The framing itself is fairly simple, most of the magic involved is within the capture engine and the
wireshark dissector.
'''

from enum      import IntEnum
from typing    import Final

from construct import (
	Aligned, BitsInteger, BitStruct, Bytes, Const, Default, Enum, Flag, Hex, HexDump,
	Int8ul, Int16ul, Int32ul, Rebuild, Struct, len_, this,
)

__all__ = (
	'SCSIDataRate',
	'SCSISpeed',
	'SCSIWidth',
	'SCSIType',
	'SCSIFrameType',
)


SHRINE_PEN: Final = 0x0000F578

class SCSIDataRate(IntEnum):
	SDR = 0x00
	DDR = 0x01

class SCSISpeed(IntEnum):
	MHz_5   = 0x00
	MHz_10  = 0x01
	MHz_20  = 0x02
	MHz_40  = 0x03
	MHz_80  = 0x04
	MHz_160 = 0x05

class SCSIWidth(IntEnum):
	BITS_8  = 0x00
	BITS_16 = 0x01
	BITS_32 = 0x02

class SCSIType(IntEnum):
	HVD = 0x00
	SE  = 0x01
	LVD = 0x02
	MSE = LVD | SE

# LINKTYPE_PARALLEL_SCSI Interface Description SCSI Bus metadata Option
scsi_bus_opt = 'SCSI Bus Metadata' / Struct(
	'PEN'       / Const(SHRINE_PEN, Int32ul),
	'opt_type'  / Const(0x0000, Int16ul),
	'bus_flags' / BitStruct(
		'data_rate'    / Enum(Flag,        SCSIDataRate),
		'speed'        / Enum(BitsInteger(3), SCSISpeed),
		'width'        / Enum(BitsInteger(4), SCSIWidth),
		'type'         / Enum(BitsInteger(2),  SCSIType),
		'equalization' / Flag,
		'paced'        / Flag,
		'reserved'     / Const(0, BitsInteger(4)),
	),
	'reserved' / Const(b'\x00' * 8)
)

class SCSIFrameType(IntEnum):
	COMMAND          = 0x00
	DATA_IN          = 0x01
	DATA_OUT         = 0x02
	MESSAGE          = 0x03
	ARBITRATION      = 0x04
	SEL_RESEL        = 0x05
	INFORMATION_UNIT = 0x09
	BUS_CONDITION    = 0x0F

	INVALID = 0xFF

frame_type = 'SCSI Frame Type' / Enum(Int8ul, SCSIFrameType)

def _frame_len(this):
	return (
		Int32ul.sizeof()                      +
		this._subcons.type.sizeof(**this)     +
		(Int8ul.sizeof() * 2)                 +
		this._subcons.reserved.sizeof(**this) +
		Int32ul.sizeof()
	)

linktype_parallel_scsi = 'Parallel SCSI Frame' / Aligned(4, Struct(
	'len'      / Rebuild(Int32ul, _frame_len),
	'type'     / Hex(frame_type),
	'orig_id'  / Default(Int8ul, 0),
	'dest_id'  / Default(Int8ul, 0),
	'reserved' / Const(b'\x00' * 17),
	'data_len' / Rebuild(Int32ul, len_(this.data)),
	'data'     / HexDump(Bytes(this.data_len)),
))
