# SPDX-License-Identifier: BSD-3-Clause
from construct import *

__all__ = (
	'test_unit_ready',
	'request_sense',
	'inquiry',
	'copy',
	'receive_diagnostic_results',
	'send_diagnostic',
	'compare',
	'copy_and_verify',
)


# Group: 0 | Peripheral Device: All | Type: Optional
test_unit_ready = 'Test Unit Ready' / BitStruct(
	'LUN'      / BitsInteger(3),
	'Reserved' / BitsInteger(29),
)

# Group: 0 | Peripheral Device: All | Type: Mandatory
request_sense = 'Request Sense' / BitStruct(
	'LUN'       / BitsInteger(3),
	'Reserved'  / BitsInteger(21),
	'AllocLen'  / Int8ul,
)

# Group: 0 | Peripheral Device: All | Type: Extended
inquiry = 'Inquiry' / BitStruct(
	'LUN'      / BitsInteger(3),
	'Reserved' / BitsInteger(21),
	'AllocLen' / Int8ul,
)


# Group: 0 | Peripheral Device: All | Type: Optional
copy = 'Copy' / BitStruct(
	'LUN'      / BitsInteger(3),
	'Reserved' / BitsInteger(5),
	'ParamLen' / Int24ul,
)

# Group: 0 | Peripheral Device: All | Type: Optional
receive_diagnostic_results = 'Receive Diagnostic Results' / BitStruct(
	'LUN'      / BitsInteger(3),
	'Reserved' / BitsInteger(21),
	'AllocLen' / Int16ul,
)

# Group: 0 | Peripheral Device: All | Type: Optional
send_diagnostic = 'Send Diagnostic' / BitStruct(
	'LUN'      / BitsInteger(3),
	'Reserved' / BitsInteger(2),
	'SelfTest' / Flag,
	'DevOL'    / Flag,
	'UnitOL'   / Flag,
	'Reserved' / Int8ul,
	'ParamLen' / Int16ul,
)

# Group: 1 | Peripheral Device: All | Type: Optional
compare = 'Compare' / BitStruct(
	'LUN'      / BitsInteger(3),
	'Reserved' / BitsInteger(13),
	'ParamLen' / Int24ul,
	'Reserved' / Int24ul,
)

# Group: 1 | Peripheral Device: All | Type: Optional
copy_and_verify = 'Copy and Verify' / BitStruct(
	'LUN'       / BitsInteger(3),
	'Reserved'  / BitsInteger(3),
	'ByteCheck' / Flag,
	'Reserved'  / Flag,
	'ParamLen'  / Int24ul,
	'Reserved'  / Int24ul,
)
