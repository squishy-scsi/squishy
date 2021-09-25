# SPDX-License-Identifier: BSD-3-Clause
from construct import *

__all__ = (
	'lun_res',
	'opcode',
	'ctl_byte',

	'test_unit_rdy',
	'request_sense',
	'sense_data',
	'sense_data_key',
	'sense_data_ex',
	'inquiry',
	'peripheral_type',
	'inquiry_data',
	'copy_func',
	'copy',
	'copy_descriptor_0',
	'copy_descriptor_1',
	'copy_descriptor_2',
	'copy_data',
	'recv_diagnostic_results',
	'send_diagnostic',
	'compare',
	'copy_and_verify',
)

lun_res = BitStruct(
	'LUN'      / BitsInteger(3),
	'Reserved' / BitsInteger(5),
)

opcode = 'OP Code' / BitStruct(
	'Group'   / BitsInteger(3),
	'Command' / BitsInteger(5),
)

ctl_byte = 'Control' / BitStruct(
	'Vendor'   / BitsInteger(2),
	'Reserved' / BitsInteger(4),
	'Flag'     / Flag,
	'Link'     / Flag,
)

# Generic SCSI Command Formats
cmd6 = '6-Byte Command' / Struct(
	'OP Code' / opcode,
	'LUN'     / lun_res,
	'LBA 2'   / Int8ul,
	'LBA 3'   / Int8ul,
	'TX Len'  / Int8ul,
	'Control' / ctl_byte,
)

cmd10 = '10 Byte Command' / Struct(
	'OP Code'   / opcode,
	BitStruct(
		'LUN'      / BitsInteger(3),
		'Reserved' / BitsInteger(4),
		'RelAdde'  / Flag,
	),
	'LBA 1'     / Int8ul,
	'LBA 2'     / Int8ul,
	'LBA 3'     / Int8ul,
	'LBA 4'     / Int8ul,
	'Reserved'  / Int8ul,
	'TX Len 1'  / Int8ul,
	'TX Len 2'  / Int8ul,
	'Control'   / ctl_byte,
)

cmd12 = '12 Byte Command' / Struct(
	'OP Code'   / opcode,
	BitStruct(
		'LUN'      / BitsInteger(3),
		'Reserved' / BitsInteger(4),
		'RelAdde'  / Flag,
	),
	'LBA 1'     / Int8ul,
	'LBA 2'     / Int8ul,
	'LBA 3'     / Int8ul,
	'LBA 4'     / Int8ul,
	'Reserved'  / Int8ul,
	'Reserved'  / Int8ul,
	'Reserved'  / Int8ul,
	'TX Len 1'  / Int8ul,
	'TX Len 2'  / Int8ul,
	'Control'   / ctl_byte,
)


# Group: 0 | Peripheral Device: All | Type: Optional
test_unit_rdy = 'Test Unit Ready' / Struct(
	'OP Code'  / Const(b'\x00'),
	'LUN'      / lun_res,
	'Reserved' / Int8ul,
	'Reserved' / Int8ul,
	'Reserved' / Int8ul,
	'Control'  / ctl_byte,
)

# Group: 0 | Peripheral Device: All | Type: Mandatory
request_sense = 'Request Sense' / Struct(
	'OP Code'   / Const(b'\x03'),
	'LUN'       / lun_res,
	'Reserved'  / Int8ul,
	'Reserved'  / Int8ul,
	'Alloc Len' / Int8ul,
	'Control'   / ctl_byte,
)

sense_data = 'Sense Data' / Struct(
	BitStruct(
		'AD Valid'  / Flag,
		'ERR Class' / BitsInteger(3),
		'Err Code'  / BitsInteger(4),
	),
	BitStruct(
		'Vendor Unique' / BitsInteger(3),
		'LBA 1'         / BitsInteger(5),
	),
	'LBA 2' / Int8ul,
	'LBA 3' / Int8ul,
)

sense_data_key = 'Sense Key' / Enum(BitsInteger(4),
	NO_SENSE      = 0b0000,
	RECOVERED_ERR = 0b0001,
	NOT_READY     = 0b0010,
	MEDIUM_ERROR  = 0b0011,
	HARDWARE_ERR  = 0b0100,
	ILLEGAL_REQ   = 0b0101,
	UNIT_ATN      = 0b0110,
	DATA_PROT     = 0b0111,
	BLANK_CHECK   = 0b1000,
	VENDOR        = 0b1001,
	COPY_ABORTED  = 0b1010,
	ABORT_CMD     = 0b1011,
	EQUAL         = 0b1100,
	VOL_OVERFLOW  = 0b1101,
	MISCOMPARE    = 0b1110,
	RESERVED      = 0b1111,
)

sense_data_ex = 'Extended Sense Data' / Struct(
	BitStruct(
		'AD Valid'  / Flag,
		'ERR Class' / BitsInteger(3),
		'Err Code'  / BitsInteger(4),
	),
	'Segment' / Int8ul,
	BitStruct(
		'File Mark' / Flag,
		'EOM'       / Flag,
		'ILI'       / Flag,
		'Reserved'  / Flag,
		'Sense Key' / sense_data_key,
	),
	'Info 1'          / Int8ul,
	'Info 2'          / Int8ul,
	'Info 3'          / Int8ul,
	'Info 4'          / Int8ul,
	'Additional'      / Int8ul,
	'Additional Data' / Bytes(this.Additional),
)


# Group: 0 | Peripheral Device: All | Type: Extended
inquiry = 'Inquiry' / Struct(
	'OP Code'   / Const(b'\x12'),
	'LUN'       / lun_res,
	'Reserved'  / Int8ul,
	'Reserved'  / Int8ul,
	'Alloc Len' / Int8ul,
	'Control'   / ctl_byte,
)

peripheral_type = 'Peripheral Type' / Enum(Int8ul,
	DirectAccess     = 0x00,
	SequentialAccess = 0x01,
	Printer          = 0x02,
	Processor        = 0x03,
	WORM             = 0x04,
	ReadOnly         = 0x05,
	ReservedStart    = 0x06,
	ReservedEnd      = 0x7E,
	LUNNotPresent    = 0x7F,
	VendorStart      = 0x80,
	VendorEnd        = 0xFF,
)


inquiry_data = 'Inquiry Data' / Struct(
	'Peripheral Type' / peripheral_type,
	BitStruct(
		'RMB'                   / Flag,
		'Device Type Qualifier' / BitsInteger(7),
	),
	BitStruct(
		'ISO Ver'  / BitsInteger(2),
		'ECMA Ver' / BitsInteger(3),
		'ANSI Ver' / BitsInteger(3),
	),
	'Reserved'      / Int8ul,
	'Additional'    / Int8ul,
	'Vendor Params' / Bytes(this.Additional),
)

# Group: 0 | Peripheral Device: All | Type: Optional

copy_func = 'Copy Function' / Enum(BitsInteger(5),
	DirectToSequential     = 0b00000,
	SequentialToDirect     = 0b00001,
	DirectToDirect         = 0b00010,
	SequentialToSequential = 0b00011,
	ReservedStart          = 0b00100,
	ReservedEnd            = 0b01111,
	VendorStart            = 0b10000,
	VendorEnd              = 0b11111,
)

copy = 'Copy' / Struct(
	'OP Code'   / Const(b'\x18'),
	'LUN'       / lun_res,
	'Param Len' / Int24ul,
	'Control'   / ctl_byte,
)

copy_descriptor_0 = 'Segment Descriptor' / Struct(
	BitStruct(
		'Source'   / BitsInteger(3),
		'Reserved' / BitsInteger(2),
		'Src LUN'  / BitsInteger(3),
	),
	BitStruct(
		'Destination' / BitsInteger(3),
		'Reserved'    / BitsInteger(2),
		'Dst LUN'     / BitsInteger(3),
	),
	'Sequential Blk Len' / Int16ul,
	'Direct Blk Count'   / Int32ul,
	'Direct LBA'         / Int32ul,
)

copy_descriptor_1 = 'Segment Descriptor' / Struct(
	BitStruct(
		'Source'   / BitsInteger(3),
		'Reserved' / BitsInteger(2),
		'Src LUN'  / BitsInteger(3),
	),
	BitStruct(
		'Destination' / BitsInteger(3),
		'Reserved'    / BitsInteger(2),
		'Dst LUN'     / BitsInteger(3),
	),
	'Reserved'      / Int8ul,
	'Reserved'      / Int8ul,
	'Src Blk Count' / Int32ul,
	'Src LUN'       / Int32ul,
	'Dst LBA'       / Int32ul,
)

copy_descriptor_2 = 'Segment Descriptor' / Struct(
	BitStruct(
		'Source'   / BitsInteger(3),
		'Reserved' / BitsInteger(2),
		'Src LUN'  / BitsInteger(3),
	),
	BitStruct(
		'Destination' / BitsInteger(3),
		'Reserved'    / BitsInteger(2),
		'Dst LUN'     / BitsInteger(3),
	),
	'Reserved'      / Int8ul,
	'Reserved'      / Int8ul,
	'Src Blk Len'   / Int16ul,
	'Dst Blk Len'   / Int16ul,
	'Src Blk Count' / Int32ul,
)

copy_data = 'Copy Data' / Struct(
	BitStruct(
		'Function' / copy_func,
		'Priority' / BitsInteger(3),
	),
	'Vendor Unique' / Int8ul,
	'Reserved'      / Int8ul,
	'Reserved'      / Int8ul,
)

# Group: 0 | Peripheral Device: All | Type: Optional
recv_diagnostic_results = 'Receive Diagnostic Results' / Struct(
	'OP Code'        / Const(b'\x1C'),
	'LUN'            / lun_res,
	'Reserved'       / Int8ul,
	'Allocation Len' / Int16ul,
	'Control'        / ctl_byte,
)

# Group: 0 | Peripheral Device: All | Type: Optional
send_diagnostic = 'Send Diagnostic' / Struct(
	'OP Code' / Const(b'\x1D'),
	BitStruct(
		'LUN'          / BitsInteger(3),
		'Reserved'     / BitsInteger(2),
		'Self Test'    / Flag,
		'Dev Offline'  / Flag,
		'Unit Offline' / Flag,
	),
	'Reserved'       / Int8ul,
	'Param List Len' / Int16ul,
	'Control'        / ctl_byte,
)

# Group: 1 | Peripheral Device: All | Type: Optional
compare = 'Compare' / Struct(
	'OP Code'        / Const(b'\x39'),
	'LUN'            / lun_res,
	'Reserved'       / Int8ul,
	'Param List Len' / Int24ul,
	'Reserved'       / Int8ul,
	'Reserved'       / Int8ul,
	'Reserved'       / Int8ul,
	'Control'        / ctl_byte,
)

# Group: 1 | Peripheral Device: All | Type: Optional
copy_and_verify = 'Copy and Verify' / Struct(
	'OP Code' / Const(b'\x3A'),
	BitStruct(
		'LUN'      / BitsInteger(3),
		'Reserved' / BitsInteger(3),
		'Byte Chk' / Flag,
		'Reserved' / Flag,
	),
	'Reserved'       / Int8ul,
	'Param List Len' / Int24ul,
	'Reserved'       / Int8ul,
	'Reserved'       / Int8ul,
	'Reserved'       / Int8ul,
	'Control'        / ctl_byte,
)
