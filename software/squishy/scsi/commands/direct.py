# SPDX-License-Identifier: BSD-3-Clause
from construct import *

__all__ = (
	'rezero_unit',
	'format_unit',
	'reassign_blocks',
	'read',
	'write',
	'seek',
	'mode_select',
	'reserve',
	'release',
	'mode_sense',
	'start_stop_unit',
	'prevent_allow_media_removal',
	'read_capacity',
	'read',
	'write',
	'seek',
	'write_and_verify',
	'verify',
	'search_data',
	'set_limits',
)


# Group: 0 | Peripheral Device: Direct Access | Type: Optional
rezero_unit = 'Re-Zero Unit' / BitStruct(
	'LUN'      / BitsInteger(3),
	'Reserved' / BitsInteger(29),
)

# Group: 0 | Peripheral Device: Direct Access | Type: Mandatory
format_unit = 'Format Unit' / BitStruct(
	'LUN'           / BitsInteger(3),
	'FormatData'    / Flag,
	'CompareList'   / Flag,
	'DefectListFmt' / BitsInteger(3),
	'Vendor'        / Int8ul,
	'Interleave'    / Int16ul,
)


# Group: 0 | Peripheral Device: Direct Access, WORM | Type: Optional
reassign_blocks = 'Reassign Blocks' / BitStruct(
	'LUN'      / BitsInteger(3),
	'Reserved' / BitsInteger(29),
)

# Group: 0 | Peripheral Device: Direct Access | Type: Mandatory
read = 'Read' / BitStruct(
	'LUN'   / BitsInteger(3),
	'LBA'   / BitsInteger(21),
	'TxLen' / Int8ul,
)

# Group: 0 | Peripheral Device: Direct Access | Type: Mandatory
write = 'Write' / BitStruct(
	'LUN'   / BitsInteger(3),
	'LBA'   / BitsInteger(21),
	'TxLen' / Int8ul,
)

# Group: 0 | Peripheral Device: Direct Access, WORM, RO DA | Type: Optional
seek = 'Seek' / BitStruct(
	'LUN'      / BitsInteger(3),
	'LBA'      / BitsInteger(21),
	'Reserved' / Int8ul,
)

# Group: 0 | Peripheral Device: Direct Access | Type: Optional
mode_select = 'Mode Select' / BitStruct(
	'LUN'      / BitsInteger(3),
	'Reserved' / BitsInteger(21),
	'ParamLen' / Int8ul,
)

# Group: 0 | Peripheral Device: Direct Access, WORM, RO DA | Type: Optional
reserve = 'Reserve' / BitStruct(
	'LUN'           / BitsInteger(3),
	'ThirdParty'    / Flag,
	'ThirdPartyDID' / BitsInteger(3),
	'Extent'        / Flag,
	'ReservationID' / Int8ul,
	'ExtentListLen' / Int16ul,
)

# Group: 0 | Peripheral Device: Direct Access, WORM, RO DA | Type: Optional
release = 'Release' / BitStruct(
	'LUN'           / BitsInteger(3),
	'ThirdParty'    / Flag,
	'ThirdPartyDID' / BitsInteger(3),
	'Extent'        / Flag,
	'ReservationID' / Int8ul,
	'Reserved'      / Int16ul,
)

# Group: 0 | Peripheral Device: Direct Access | Type: Optional
mode_sense = 'Mode Sense' / BitStruct(
	'LUN'      / BitsInteger(3),
	'Reserved' / BitsInteger(21),
	'AllocLen' / Int8ul,
)

# Group: 0 | Peripheral Device: Direct Access | Type: Optional
start_stop_unit = 'Start/Stop Unit' / BitStruct(
	'LUN'       / BitsInteger(3),
	'Reserved'  / BitsInteger(4),
	'Immediate' / Flag,
	'Reserved'  / BitsInteger(23),
	'Start'     / Flag,
)

# Group: 0 | Peripheral Device: Direct Access, WORM, RO DA | Type: Optional
prevent_allow_media_removal = 'Prevent/Allow Media Removal' / BitStruct(
	'LUN'      / BitsInteger(3),
	'Reserved' / BitsInteger(28),
	'Prevent'  / Flag,
)

# Group: 1 | Peripheral Device: Direct Access, WORM, RO DA | Type: Extended
read_capacity = 'Read Capacity' / BitStruct(
	'LUN'          / BitsInteger(3),
	'Reserved'     / BitsInteger(4),
	'RelativeAddr' / Flag,
	'LBA'          / Int32ul,
	'Reserved'     / Int16ul,
	'Vendor'       / BitsInteger(2),
	'Reserved'     / BitsInteger(5),
	'PMI'          / Flag,
)

# Group: 1 | Peripheral Device: Direct Access | Type: Extended
read = 'Read (Direct Access)' / BitStruct(
	'LUN'          / BitsInteger(3),
	'Reserved'     / BitsInteger(4),
	'RelativeAddr' / Flag,
	'LBA'          / Int32ul,
	'Reserved'     / Int8ul,
	'TXLen'        / Int16ul,
)

# Group: 1 | Peripheral Device: Direct Access | Type: Extended
write = 'Write (Direct Access)' / BitStruct(
	'LUN'          / BitsInteger(3),
	'Reserved'     / BitsInteger(4),
	'RelativeAddr' / Flag,
	'LBA'          / Int32ul,
	'Reserved'     / Int8ul,
	'TXLen'        / Int16ul,
)

# Group: 1 | Peripheral Device: Direct Access | Type: Extended
seek = 'Seek (Direct Access)' / BitStruct(
	'LUN'          / BitsInteger(3),
	'Reserved'     / BitsInteger(5),
	'LBA'          / Int32ul,
	'Reserved'     / Int24ul,
)

# Group: 1 | Peripheral Device: Direct Access | Type: Optional
write_and_verify = 'Write and Verify' / BitStruct(
	'LUN'          / BitsInteger(3),
	'Reserved'     / BitsInteger(3),
	'ByteCheck'    / Flag,
	'RelativeAddr' / Flag,
	'LBA'          / Int32ul,
	'Reserved'     / Int8ul,
	'TXLen'        / Int16ul,
)

# Group: 1 | Peripheral Device: Direct Access | Type: Optional
verify = 'Verify' / BitStruct(
	'LUN'          / BitsInteger(3),
	'Reserved'     / BitsInteger(3),
	'ByteCheck'    / Flag,
	'RelativeAddr' / Flag,
	'LBA'          / Int32ul,
	'Reserved'     / Int8ul,
	'VerifLen'     / Int16ul,
)

# Group: 1 | Peripheral Device: Direct Access | Type: Optional
search_data = 'Search Data' / BitStruct(
	'LUN'          / BitsInteger(3),
	'Invert'       / Flag,
	'Reserved'     / BitsInteger(2),
	'SpannedData'  / Flag,
	'RelativeAddr' / Flag,
	'LBA'          / Int32ul,
	'Reserved'     / Int8ul,
	'TXLen'        / Int16ul,
)

# Group: 1 | Peripheral Device: Direct Access | Type: Optional
set_limits = 'Set Limits' / BitStruct(
	'LUN'          / BitsInteger(3),
	'Reserved'     / BitsInteger(3),
	'ReadInhibit'  / Flag,
	'WriteInhibit' / Flag,
	'LBA'          / Int32ul,
	'Reserved'     / Int8ul,
	'BlkCount'     / Int16ul,
)
