# SPDX-License-Identifier: BSD-3-Clause
from construct import *

__all__ = (
	'format_printer',
	'print_cmd',
	'slew_and_print',
	'flush_buffer',
	'recover_buffered_data',
)

# Group: 0 | Peripheral Device: Printer | Type: Optional
format_printer = 'Format (Printer)' / BitStruct(
	'LUN'      / BitsInteger(3),
	'Reserved' / BitsInteger(3),
	'Type'     / BitsInteger(2),
	'TxLen'    / Int24ul,
)

# Group: 0 | Peripheral Device: Printer | Type: Mandatory
print_cmd = 'Print' / BitStruct(
	'LUN'      / BitsInteger(3),
	'Reserved' / BitsInteger(5),
	'TxLen'    / Int24ul,
)

# Group: 0 | Peripheral Device: Printer | Type: Optional
slew_and_print = 'Slew and Print' / BitStruct(
	'LUN'      / BitsInteger(3),
	'Reserved' / BitsInteger(4),
	'Channel'  / BitsInteger(1),
)

# Group: 0 | Peripheral Device: Printer | Type: Optional
flush_buffer = 'Flush Buffer' / BitStruct(
	'LUN'      / BitsInteger(3),
	'Reserved' / BitsInteger(28),
)

# Group: 0 | Peripheral Device: Printer | Type: Optional
