# SPDX-License-Identifier: BSD-3-Clause

'''
This module defines the commands that are specific to printers
'''

from construct import BitsInteger, BitStruct, Int24ul

__all__ = (
	'format_printer',
	'print_cmd',
	'slew_and_print',
	'flush_buffer',
	'recover_buffered_data',
)

format_printer = 'Format (Printer)' / BitStruct(
	'LUN'      / BitsInteger(3),
	'Reserved' / BitsInteger(3),
	'Type'     / BitsInteger(2),
	'TxLen'    / Int24ul,
)
''' Format - Group: 0 | Peripheral Device: Printer | Type: Optional '''

print_cmd = 'Print' / BitStruct(
	'LUN'      / BitsInteger(3),
	'Reserved' / BitsInteger(5),
	'TxLen'    / Int24ul,
)
''' Print - Group: 0 | Peripheral Device: Printer | Type: Mandatory '''

slew_and_print = 'Slew and Print' / BitStruct(
	'LUN'      / BitsInteger(3),
	'Reserved' / BitsInteger(4),
	'Channel'  / BitsInteger(1),
)
''' Slew and Print - Group: 0 | Peripheral Device: Printer | Type: Optional '''

flush_buffer = 'Flush Buffer' / BitStruct(
	'LUN'      / BitsInteger(3),
	'Reserved' / BitsInteger(28),
)
''' Flush Buffer - Group: 0 | Peripheral Device: Printer | Type: Optional '''
