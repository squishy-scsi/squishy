# SPDX-License-Identifier: BSD-3-Clause
from construct import *

__doc__ = """
This module contains common commands, that other device classes
can support.
"""

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

test_unit_ready = 'Test Unit Ready' / BitStruct(
	'LUN'      / BitsInteger(3),
	'Reserved' / BitsInteger(29),
)
""" Test Unit Ready - Group: 0 | Peripheral Device: All | Type: Optional """

request_sense = 'Request Sense' / BitStruct(
	'LUN'       / BitsInteger(3),
	'Reserved'  / BitsInteger(21),
	'AllocLen'  / Int8ul,
)
""" Request Sense - Group: 0 | Peripheral Device: All | Type: Mandatory """

inquiry = 'Inquiry' / BitStruct(
	'LUN'      / BitsInteger(3),
	'Reserved' / BitsInteger(21),
	'AllocLen' / Int8ul,
)
""" Inquiry - Group: 0 | Peripheral Device: All | Type: Extended """

copy = 'Copy' / BitStruct(
	'LUN'      / BitsInteger(3),
	'Reserved' / BitsInteger(5),
	'ParamLen' / Int24ul,
)
""" Copy - Group: 0 | Peripheral Device: All | Type: Optional """

receive_diagnostic_results = 'Receive Diagnostic Results' / BitStruct(
	'LUN'      / BitsInteger(3),
	'Reserved' / BitsInteger(21),
	'AllocLen' / Int16ul,
)
""" Receive Diagnostic Results - Group: 0 | Peripheral Device: All | Type: Optional """

send_diagnostic = 'Send Diagnostic' / BitStruct(
	'LUN'      / BitsInteger(3),
	'Reserved' / BitsInteger(2),
	'SelfTest' / Flag,
	'DevOL'    / Flag,
	'UnitOL'   / Flag,
	'Reserved' / Int8ul,
	'ParamLen' / Int16ul,
)
""" Send Diagnostic - Group: 0 | Peripheral Device: All | Type: Optional """

compare = 'Compare' / BitStruct(
	'LUN'      / BitsInteger(3),
	'Reserved' / BitsInteger(13),
	'ParamLen' / Int24ul,
	'Reserved' / Int24ul,
)
""" Compare - Group: 1 | Peripheral Device: All | Type: Optional  """

copy_and_verify = 'Copy and Verify' / BitStruct(
	'LUN'       / BitsInteger(3),
	'Reserved'  / BitsInteger(3),
	'ByteCheck' / Flag,
	'Reserved'  / Flag,
	'ParamLen'  / Int24ul,
	'Reserved'  / Int24ul,
)
""" Copy and Verify - Group: 1 | Peripheral Device: All | Type: Optional """
