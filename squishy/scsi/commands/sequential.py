# SPDX-License-Identifier: BSD-3-Clause

'''
This module defines the commands that are specific to sequential
access devices.
'''

from construct import BitsInteger, BitStruct, Flag, Int8ul, Int24ul

__all__ = (
	'rewind',
	'read_block_limits',
	'read',
	'write',
	'track_select',
	'read_reverse',
	'write_filemarks',
	'space',
	'verify',
	'recover_buffered_data',
	'mode_select',
	'reserve',
	'release',
	'erase',
	'mode_sense',
	'load_unload',
)

# Group: 0 | Peripheral Device: Sequential Access | Type: Mandatory
rewind = 'Rewind' / BitStruct(
	'LUN'       / BitsInteger(3),
	'Reserved'  / BitsInteger(4),
	'Immediate' / Flag,
	'Reserved'  / Int24ul,
)

# Group: 0 | Peripheral Device: Sequential Access | Type: Extended
read_block_limits = 'Read Block Limits' / BitStruct(
	'LUN'       / BitsInteger(3),
	'Reserved'  / BitsInteger(29),
)

# Group: 0 | Peripheral Device: Sequential Access | Type: Mandatory
read = 'Read (Sequential)' / BitStruct(
	'LUN'      / BitsInteger(3),
	'Reserved' / BitsInteger(4),
	'Fixed'    / Flag,
	'TXLen'    / Int24ul,
)

# Group: 0 | Peripheral Device: Sequential Access | Type: Mandatory
write = 'Write (Sequential)' / BitStruct(
	'LUN'      / BitsInteger(3),
	'Reserved' / BitsInteger(4),
	'Fixed'    / Flag,
	'TXLen'    / Int24ul,
)

# Group: 0 | Peripheral Device: Sequential Access | Type: Optional
track_select = 'Track Select' / BitStruct(
	'LUN'      / BitsInteger(3),
	'Reserved' / BitsInteger(21),
	'TrackVal' / Int8ul,
)

# Group: 0 | Peripheral Device: Sequential Access | Type: Optional
read_reverse = 'Read Reversed' / BitStruct(
	'LUN'      / BitsInteger(3),
	'Reserved' / BitsInteger(4),
	'Fixed'    / Flag,
	'TXLen'    / Int24ul,
)

# Group: 0 | Peripheral Device: Sequential Access | Type: Mandatory
write_filemarks = 'Write Filemarks' / BitStruct(
	'LUN'         / BitsInteger(3),
	'Reserved'    / BitsInteger(5),
	'FilemarkNum' / Int24ul,
)

# Group: 0 | Peripheral Device: Sequential Access | Type: Optional
space = 'Space' / BitStruct(
	'LUN'      / BitsInteger(3),
	'Reserved' / BitsInteger(3),
	'Code'     / BitsInteger(2),
	'Count'    / Int24ul,
)

# Group: 0 | Peripheral Device: Sequential Access | Type: Optional
verify = 'Verify (Sequential)' / BitStruct(
	'LUN'       / BitsInteger(3),
	'Reserved'  / BitsInteger(3),
	'ByteCmp'   / Flag,
	'Fixed'     / Flag,
	'VerifyLen' / Int24ul,
)

# Group: 0 | Peripheral Device: Sequential Access | Type: Optional
recover_buffered_data = 'Recover Buffered Date' / BitStruct(
	'LUN'      / BitsInteger(3),
	'Reserved' / BitsInteger(4),
	'Fixed'    / Flag,
	'TXLen'    / Int24ul,
)

# Group: 0 | Peripheral Device: Sequential Access | Type: Optional
mode_select = 'Mode Select (Sequential)' / BitStruct(
	'LUN'      / BitsInteger(3),
	'Reserved' / BitsInteger(21),
	'ParamLen' / Int8ul,
)

# Group: 0 | Peripheral Device: Sequential Access | Type: Optional
reserve = 'Reserve Unit (Sequential)' / BitStruct(
	'LUN'           / BitsInteger(3),
	'ThirdParty'    / Flag,
	'ThirdPartyDID' / BitsInteger(3),
	'Reserved'      / BitsInteger(25),
)

# Group: 0 | Peripheral Device: Sequential Access | Type: Optional
release = 'Release Unit (Sequential)' / BitStruct(
	'LUN'           / BitsInteger(3),
	'ThirdParty'    / Flag,
	'ThirdPartyDID' / BitsInteger(3),
	'Reserved'      / BitsInteger(25),
)

# Group: 0 | Peripheral Device: Sequential Access | Type: Optional
erase = 'Erase (Sequential)' / BitStruct(
	'LUN'      / BitsInteger(3),
	'Reserved' / BitsInteger(4),
	'Long'     / Flag,
	'Reserved' / Int24ul,
)

# Group: 0 | Peripheral Device: Sequential Access | Type: Optional
mode_sense = 'Mode Sense (Sequential)' / BitStruct(
	'LUN'      / BitsInteger(3),
	'Reserved' / BitsInteger(21),
	'AllocLen' / Int8ul,
)

# Group: 0 | Peripheral Device: Sequential Access | Type: Optional
load_unload = 'Load/Unload' / BitStruct(
	'LUN'       / BitsInteger(3),
	'Reserved'  / BitsInteger(4),
	'Immediate' / Flag,
	'Reserved'  / BitsInteger(22),
	'ReTension' / Flag,
	'Load'      / Flag,
)

# Group: 0 | Peripheral Device: Sequential Access | Type: Optional
prevent_allow_media_removal = 'Prevent/Allow Media Removal (Sequential)' / BitStruct(
	'LUN'      / BitsInteger(3),
	'Reserved' / BitsInteger(28),
	'Prevent'  / Flag,
)
