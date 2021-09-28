# SPDX-License-Identifier: BSD-3-Clause
from construct import *

from .common   import lun_res, opcode, ctl_byte

__all__ = (
	'rezero_unit',
	'format_unit',
	'defect_list',
)

# Group: 0 | Peripheral Device: Direct Access | Type: Optional
rezero_unit = 'Re-Zero Unit' / Struct(
	'OP Code'  / Const(b'\x01'),
	'LUN'      / lun_res,
	'Reserved' / Int8ul,
	'Reserved' / Int8ul,
	'Reserved' / Int8ul,
	'Control'  / ctl_byte,
)

# Group: 0 | Peripheral Device: Direct Access | Type: Mandatory
format_unit = 'Format Unit' / Struct(
	'OP Code'  / Const(b'\x04'),
	BitStruct(
		'LUN'             / BitsInteger(3),
		'Format Data'     / Flag,
		'Compare List'    / Flag,
		'Defect List Fmt' / BitsInteger(3),
	),
	'Vendor'     / Int8ul,
	'Interleave' / Int16ul,
	'Control'    / ctl_byte,
)

defect_list_blk = 'Defect List (blk)' / Struct(
	'Reserved'        / Int8ul,
	'Reserved'        / Int8ul,
	'Defect List Len' / Int16ul,
	'Defects'         / Array(this.Defect_List_Len, Int32ul),
)


defect_list = 'Defect List (bytes/sector)' / Struct(
	'Reserved'        / Int8ul,
	'Reserved'        / Int8ul,
	'Defect List Len' / Int16ul,
	'Defects'         / Array(this.Defect_List_Len, Struct(
		'Cylinder'         / Int24ul,
		'Head Number'      / Int8ul,
		'Bytes From Index' / Int32ul,
	)),
)

# Group: 0 | Peripheral Device: Direct Access, WORM | Type: Optional
reassign_blocks = 'Reassign Blocks' / Struct(
	'OP Code'  / Const(b'\x07'),
	'LUN'      / lun_res,
	'Reserved' / Int8ul,
	'Reserved' / Int8ul,
	'Control'  / ctl_byte,
)

# Group: 0 | Peripheral Device: Direct Access | Type: Mandatory
read = 'Read' / Struct(
	'OP Code'  / Const(b'\x08'),
	BitStruct(
		'LUN' / BitsInteger(3),
		'LBA' / BitsInteger(20),
	),
	'TX Len'   / Int8ul,
	'Control'  / ctl_byte,
)

# Group: 0 | Peripheral Device: Direct Access | Type: Mandatory
write = 'Write' / Struct(
	'OP Code'  / Const(b'\x0A'),
	BitStruct(
		'LUN' / BitsInteger(3),
		'LBA' / BitsInteger(20),
	),
	'TX Len'   / Int8ul,
	'Control'  / ctl_byte,
)

# Group: 0 | Peripheral Device: Direct Access, WORM, RO DA | Type: Optional
seek = 'Seek' / Struct(
	'OP Code'  / Const(b'\x0B'),
	BitStruct(
		'LUN' / BitsInteger(3),
		'LBA' / BitsInteger(20),
	),
	'Reserved' / Int8ul,
	'Control'  / ctl_byte,
)

# Group: 0 | Peripheral Device: Direct Access | Type: Optional
mode_select = 'Mode Select' / Struct(
	'OP Code'   / Const(b'\x15'),
	'LUN'       / lun_res,
	'Reserved'  / Int8ul,
	'Reserved'  / Int8ul,
	'Param Len' / Int8ul,
	'Control'   / ctl_byte,
)

medium_type = 'Medium Type' / Enum(Int8ul,
	Default         = 0x00,
	FlexibleDisk_SS = 0x01,
	FlexibleDisk_DS = 0x02,

)

density_code = 'Density Code' / Enum(Int8ul,
	Default         = 0x00,
	FlexibleDisk_SD = 0x01,
	FlexibleDisk_DD = 0x02,
	ReservedStart   = 0x03,
	ReservedEnd     = 0x7F,
	VendorStart     = 0x80,
	VendorEnd       = 0xFF,
)

mode_params = 'Mode Select Parameters' / Struct(
	'Reserved'              / Int8ul,
	'Medium Type'           / medium_type,
	'Reserved'              / Int8ul,
	'Block Descriptor Len'  / Int8ul,
	'Block Descriptors'     / Array(this.Block_Descriptor_Len // 8, Struct(
		'Density Code'      / density_code,
		'Number Of Blocks'  / Int24ul,
		'Reserved'          / Int8ul,
		'Block Length'      / Int24ul,
	))
)
