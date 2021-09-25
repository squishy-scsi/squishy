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
