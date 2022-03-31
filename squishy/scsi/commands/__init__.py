# SPDX-License-Identifier: BSD-3-Clause
from construct import *

from . import common
from . import direct
from . import sequential
from . import printer
from . import processor
from . import worm
from . import ro_direct

__all__ = (
	'group_code',
	'command',
)

group_code = 'Command Group Code' / Enum(BitsInteger(3),
	Group0 = 0b000, # Six-Byte Commands
	Group1 = 0b001, # Ten-Byte Commands
	Group2 = 0b010, # Reserved
	Group3 = 0b011, # Reserved
	Group4 = 0b100, # Reserved
	Group5 = 0b101, # Twelve-Byte Commands
	Group6 = 0b110, # Vendor
	Group7 = 0b111, # Vendor
)

command = 'SCSI Command' / Struct(
	'Opcode' / Union(0,
		'Raw'    / Int8ul,
		'Parsed' / BitStruct(
			'Group'   / group_code,
			'Command' / BitsInteger(5),
		),
	),
	'Data'  / Switch(
		this.Opcode.Parsed.Group, {
			# Opcodes 0b000XXXXX
			group_code.Group0: 'Six-byte Command'    / Switch(
				this.Opcode.Parsed.Command, {
					0b00000: common.test_unit_ready,
					0b00001: Union(None,
						direct.rezero_unit,
						sequential.rewind,
					),
					# ...
					0b00011: common.request_sense,
					0b00100: Union(None,
						direct.format_unit,
						printer.format_printer,
					),
					0b00101: sequential.read_block_limits,
					# ...
					0b00111: direct.reassign_blocks,
					0b01000: Union(None,
						direct.read,
						sequential.read,
					),
					# ...
					0b01010: Union(None,
						direct.write,
						sequential.write,
						printer.print_cmd,
					),
					0b01011: Union(None,
						direct.seek,
						sequential.track_select,
						printer.slew_and_print,
					),
					# ...
					0b01111: sequential.read_reverse,
					# ...
					0b10000: Union(None,
						sequential.write_filemarks,
						printer.flush_buffer,
					),
					0b10001: sequential.space,
					0b10010: common.inquiry,
					0b10011: sequential.verify,
					0b10100: Union(None,
						sequential.recover_buffered_data,
					),
					0b10101: Union(None,
						direct.mode_select,
						sequential.mode_select,
					),
					0b10110: Union(None,
						direct.reserve,
						sequential.reserve,
					),
					0b10111: Union(None,
						direct.release,
						sequential.release,
					),
					0b11000: common.copy,
					0b11001: sequential.erase,
					0b11010: Union(None,
						direct.mode_sense,
						sequential.mode_sense,
					),
					0b11011: Union(None,
						direct.start_stop_unit,
						sequential.load_unload,
					),
					0b11100: common.receive_diagnostic_results,
					0b11101: common.send_diagnostic,
					0b11110: Union(None,
						direct.prevent_allow_media_removal,
						sequential.prevent_allow_media_removal,
					),
					# ...
				},
				HexDump(Bytes(4)),
			),
			# Opcodes 0b001XXXXX
			group_code.Group1: 'Ten-byte Command'    / Switch(
				this.Opcode.Parsed.Command, {
					# ...
					0b00101: direct.read_capacity,
					# ...
					0b01000: direct.read,
					# ...
					0b01010: direct.write,
					0b01011: direct.seek,
					# ...
					0b01110: direct.write_and_verify,
					0b01111: direct.verify,
					0b10000: direct.search_data, # Search High
					0b10001: direct.search_data, # Search Equal
					0b10010: direct.search_data, # Search Low,
					0b10011: direct.set_limits,
					# ...
					0b11001: common.compare,
					0b11010: common.copy_and_verify,
					# ...
				},
				HexDump(Bytes(8)),
			),
			# Opcodes 0b010XXXXX
			group_code.Group2: 'Reserved'            / Pass,
			# Opcodes 0b011XXXXX
			group_code.Group3: 'Reserved'            / Pass,
			# Opcodes 0b100XXXXX
			group_code.Group4: 'Reserved'            / Pass,
			# Opcodes 0b101XXXXX
			group_code.Group2: 'Twelve-byte Command' / Switch(
				this.Opcode.Parsed.Command, {
					# ...
				},
				HexDump(Bytes(10)),
			),
			# Opcodes 0b110XXXXX
			group_code.Group2: 'Vendor'              / Pass,
			# Opcodes 0b111XXXXX
			group_code.Group2: 'Vendor'              / Pass,
		},
		Pass
	),
	'Control' / BitStruct(
		'Vendor'   / BitsInteger(2),
		'Reserved' / BitsInteger(4),
		'Flag'     / Flag,
		'Link'     / Flag,
	),
)

_cmds = 'SCSI Commands' / GreedyRange(command)

class SCSICmdStream:
	def __init__(self, *, data_stream):
		from io import BytesIO, SEEK_END, SEEK_SET

		if isinstance(data_stream, bytes):
			self._data = BytesIO(data_stream)
		else:
			self._data = data_stream

		self.offset = self._data.tell()
		self._data.seek(0, SEEK_END)
		self.end = self._data.tell()
		self.size = self.end - self.offset
		self._data.seek(self.offset, SEEK_SET)

		self._cmd_stream = _cmds.parse_stream(self._data)

	def __str__(self):
		return str(self._cmd_stream)

if __name__ == '__main__':
	def dump_img(file_name):
		with open(file_name, 'rb') as f:
			fs = SCSICmdStream(data_stream = f)
			print(fs)

	import sys
	from os import path
	from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

	parser = ArgumentParser(
		formatter_class = ArgumentDefaultsHelpFormatter,
	)

	global_options = parser.add_argument_group('Global Options')

	global_options.add_argument(
		'--file', '-f',
		type = str,
		required = True,
	)

	global_options.add_argument(
		'--dump', '-d',
		action = 'store_true',
		default = False,
	)

	args = parser.parse_args()

	if not path.exists(args.file):
		print(f'Unable to open file \'{args.file}\' does it exist?')
		sys.exit(1)

	if args.dump:
		sys.exit(dump_img(args.file))


	sys.exit(1)
