# SPDX-License-Identifier: BSD-3-Clause
from io        import SEEK_END, SEEK_SET, BytesIO

from arrow     import Arrow
from construct import (
	Aligned, BitsInteger, BitStruct, Bytes, Check, Computed,
	Const, CString, Default, Enum, GreedyRange, Hex, HexDump,
	If, Int8ul, Int16ul, Int32ul, Int64sl, Int64ul, PaddedString,
	Pass, Rebuild, RepeatUntil, Struct, Switch, len_, this
)

# We don't have a PEN, and don't want to get one
# so we're stealing SGIs
block_pen = 59

# We only have the user link types specified, we don't need the other as we
# are not interested in a full pcapng reader/writer
#
# The following are our mappings for 'Link Type'
#  * user_00 - SCSI-1
#  * user_01 - SCSI-2
#  * user_02 - SCSI-3
#
# Details on if it is single ended or differential, as well as if
# it is 50, 68, or 80 pin is to be stored at metadata
#
# eventually we need to submit these as proper libpcap `LINKTYPE_`'s
# but that can wait,

link_type = 'Link Type' / Enum(Int16ul,
	user_00 = 0x0093,
	user_01 = 0x0094,
	user_02 = 0x0095,
	user_03 = 0x0096,
	user_04 = 0x0097,
	user_05 = 0x0098,
	user_06 = 0x0099,
	user_07 = 0x009A,
	user_08 = 0x009B,
	user_09 = 0x009C,
	user_10 = 0x009D,
	user_11 = 0x009E,
	user_12 = 0x009F,
	user_13 = 0x00A0,
	user_14 = 0x00A1,
	user_15 = 0x00A2,
)

# Because of the limitations of some of the blocks
# in the pcapng format, as well as the strange decisions
# made with regards to custom blocks, we have a multi-function
# custom block which is set to be copyied, for more details
# see the `squishy_meta` block structure.
block_type = 'Block Type' / Enum(Int32ul,
	section_header  = 0x0A0D0D0A,
	interface       = 0x00000001,
	interface_stats = 0x00000005,
	enhanced_packet = 0x00000006,

	custom          = 0x00000BAD,
	custom_no_copy  = 0x40000BAD,
)

option_type = 'Option Type' / Enum(Int16ul,
	end     = 0x0000,
	comment = 0x0001,

	custom0 = 0x0BAC,
	custom1 = 0x0BAD,
	custom2 = 0x4BAC,
	custom3 = 0x4BAD,
)

epoch = Arrow(1970, 1, 1)

def timestamp_from_raw(this):
	timestamp = (this.Raw.High << 32) + this.Raw.Low
	return epoch.shift(seconds = timestamp * 1e-6)

def timestamp_to_raw(this):
	from datetime import timedelta
	timestamp = this.Value
	# For now, assume that if the object is not an Arrow datetime, it's a standard library one
	if not isinstance(timestamp, Arrow):
		timestamp = Arrow.fromdatetime(timestamp)
	value: timedelta = timestamp - epoch
	value = int(value.total_seconds() * 1e6)
	return {'Low': value & 0xffffffff, 'High': value >> 32}

timestamp = 'Timestamp' / Struct(
	'Raw' / Rebuild(Struct(
		'High' / Hex(Int32ul),
		'Low'  / Hex(Int32ul),
	), timestamp_from_raw),
	'Value' / Computed(timestamp_to_raw),
)

# This uses PaddedString because the strings encoded are not guaranteed to be NUL terminated
# which means, if one were to use CString, it would reading past the intended EOS and into the
# next control block structure. CString has no way to length limit the read.
option_value = Aligned(4, Switch(
	this.Code, {
		option_type.end: Pass,
		option_type.comment: PaddedString(this.Length, 'utf8'),

		0x0002: Switch(this._.Type, {
				block_type.section_header: PaddedString(this.Length, 'utf8'), # shb_hardware
				block_type.interface: PaddedString(this.Length, 'utf8'),      # if_name
				block_type.enhanced_packet: BitStruct(                        # epb_flags
					'direction'   / BitsInteger(2),
					'recept_type' / BitsInteger(3),
					'fcs_len'     / BitsInteger(4),
					'reserved'    / BitsInteger(7),
					'll_errors'   / BitsInteger(16),
				),
				block_type.interface_stats: timestamp,						  # isb_starttime
			},
			HexDump(Bytes(this.Length))
		),
		0x0003: Switch(this._.Type, {
				block_type.section_header: PaddedString(this.Length, 'utf8'), # shb_os
				block_type.interface: PaddedString(this.Length, 'utf8'),      # if_description
				block_type.enhanced_packet: Bytes(this.Length),               # epb_hash
				block_type.interface_stats: timestamp,                        # isb_endtime
			},
			HexDump(Bytes(this.Length))
		),
		0x0004: Switch(this._.Type, {
				block_type.section_header: PaddedString(this.Length, 'utf8'), # shb_userappl
				block_type.interface: Struct(                                 # if_IPv4addr
					'address' / Hex(Bytes(4)),
					'mask'    / Hex(Bytes(4)),
				),
				block_type.enhanced_packet: Int64ul,                          # epb_dropcount
				block_type.interface_stats: Hex(Int64ul),                     # isb_ifrecv
			},
			HexDump(Bytes(this.Length))
		),
		0x0005: Switch(this._.Type, {
				block_type.interface: Hex(Bytes(17)),                         # if_IPv6addr
				block_type.enhanced_packet: Hex(Int64ul),                     # epb_packetid
				block_type.interface_stats: Hex(Int64ul),                     # isb_ifdrop
			},
			HexDump(Bytes(this.Length))
		),
		0x0006: Switch(this._.Type, {
				block_type.interface: Hex(Bytes(6)),                          # if_MACaddr
				block_type.enhanced_packet: Hex(Int64ul),                     # epb_queue
				block_type.interface_stats: Hex(Int64ul),                     # isb_filteraccept

			},
			HexDump(Bytes(this.Length))
		),
		0x0007: Switch(this._.Type, {
				block_type.interface: Hex(Bytes(8)),                          # if_EUIaddr
				block_type.enhanced_packet: Bytes(this.Length),               # epb_verdict
				block_type.interface_stats: Hex(Int64ul),                     # isb_osdrop
			},
			HexDump(Bytes(this.Length))
		),
		0x0008: Switch(this._.Type, {
				block_type.interface: Hex(Int64ul),                           # if_speed
				block_type.interface_stats: Hex(Int64ul),                     # isb_usrdeliv
			},
			HexDump(Bytes(this.Length))
		),
		0x0009: Switch(this._.Type, {
				block_type.interface: Hex(Bytes(1)), # if_tsresol
			},
			HexDump(Bytes(this.Length))
		),
		0x000A: Switch(this._.Type, {
				block_type.interface: Hex(Int32ul), # if_tzone
			},
			HexDump(Bytes(this.Length))
		),
		0x000B: Switch(this._.Type, {
				block_type.interface: Hex(Bytes(this.Length)), # if_filter
			},
			HexDump(Bytes(this.Length))
		),
		0x000C: Switch(this._.Type, {
				block_type.interface: PaddedString(this.Length, 'utf8'), # if_os
			},
			HexDump(Bytes(this.Length))
		),
		0x000D: Switch(this._.Type, {
				block_type.interface: Hex(Bytes(1)), # if_fcslen
			},
			HexDump(Bytes(this.Length))
		),
		0x000E: Switch(this._.Type, {
				block_type.interface: Hex(Int64ul), # if_tsoffset
			},
			HexDump(Bytes(this.Length))
		),
		0x000F: Switch(this._.Type, {
				block_type.interface: PaddedString(this.Length, 'utf8'), # if_hardware
			},
			HexDump(Bytes(this.Length))
		),
		0x0010: Switch(this._.Type, {
				block_type.interface: Hex(Int64ul), # if_txspeed
			},
			HexDump(Bytes(this.Length))
		),
		0x0011: Switch(this._.Type, {
				block_type.interface: Hex(Int64ul), # if_rxspeed
			},
			HexDump(Bytes(this.Length))
		),

		option_type.custom0: PaddedString(this.Length, 'utf8'),
		option_type.custom1: HexDump(Bytes(this.Length)),
		option_type.custom2: PaddedString(this.Length, 'utf8'),
		option_type.custom3: HexDump(Bytes(this.Length)),
	},
	HexDump(Bytes(this.Length)),
))

def option_len(this) -> int:
	if isinstance(this.Value, str):
		value = CString('utf8').build(this.Value, **this)[:-1]
	else:
		value = option_value.build(this.Value, **this)
	return len(value)

option = 'Option' / Struct(
	'Code'   / Hex(option_type),
	'Length' / Rebuild(Int16ul, option_len),
	'Value'  / If(
		this.Length > 0,
		option_value
	)
)




section_header_block = 'Section Header' / Struct(
	'BOM'     / Hex(Const(b'\x4D\x3C\x2B\x1A')),
	'Version' / Struct(
		'Major' / Hex(Int16ul),
		'Minor' / Hex(Int16ul),
	),
	'Section Len' / Hex(Int64sl),
)

interface_block = 'Interface Header' / Struct(
	'LinkType' / Hex(link_type),
	'Reserved' / Hex(Int16ul),
	'SnapLen'  / Hex(Int32ul),
)

enhanced_packet_block = 'Enhanced Packet' / Struct(
	'InterfaceID' / Hex(Int32ul),
	'TimestampRaw' / Struct('High' / Hex(Int32ul), 'Low' / Hex(Int32ul)),
	# 'Timestamp'   / Timestamp(Computed((this.TimestampRaw.High << 32) + this.TimestampRaw.Low), 0.000001, 1970),
	'CapturedLen' / Hex(Int32ul),
	'ActualLen'   / Hex(Int32ul),
	'PacketData'  / HexDump(Aligned(4, Bytes(this.CapturedLen))),
)

interface_statistics_block = 'Interface Statistics' / Struct(
	'InterfaceID' / Hex(Int32ul),
	'TimestampRaw' / Struct('High' / Hex(Int32ul), 'Low' / Hex(Int32ul)),
)


squishy_bus_type = 'Bus Type' / Enum(BitsInteger(3),
	unknown = 0b000,
	hvd     = 0b001,
	lvd     = 0b010,
	se      = 0b011,
	res0    = 0b100,
	res1    = 0b101,
	res2    = 0b110,
	res3    = 0b111,
)

squishy_con_type = 'Connection Type' / Enum(BitsInteger(3),
	unknown = 0b000,
	fifty   = 0b001,
	sixty   = 0b010,
	eighty  = 0b011,
	res0    = 0b100,
	res1    = 0b101,
	res2    = 0b110,
	res3    = 0b111,
)

squishy_scsi_ver = 'SCSI Version' / Enum(BitsInteger(2),
	unknown = 0b00,
	scsi1   = 0b01,
	scsi2   = 0b10,
	scsi3   = 0b11,
)

squishy_mode = 'Squishy Mode' / Enum(Int8ul,
	unknown    = 0x00,
	tap        = 0x01,
	device     = 0x02,
	initiator  = 0x03,
)

# bus objects
# * Bus Initiators
# * Devices
# * Seen

squishy_meta = 'Squishy Meta' / Aligned(4, Struct(
	'StartTimestamp'  / timestamp,			# Capture start timestamp
	'SquishyMetadata' / Struct(
		'SerialNumber'  / Hex(Int64ul),		# Squishy Serial Number
		'GatewareHash'  / Hex(Bytes(20)),	# Git rev of the gateware
		'SCSIInterface' / Struct(
			'VID' / Hex(Int16ul),
			'DID' / Hex(Int16ul),
			'MODE' / squishy_mode,
		),
	),
	'PythonVersion'  / BitStruct(			# Python Version
		'Major' / BitsInteger(3), 			#  * Major: 0..7
		'Minor' / BitsInteger(5), 			#  * Minor: 0..31
	),
	'BusMetadata'    / Struct(				# Bus Metadata
		'BusInfo' / BitStruct(				#  * Attached SCSI Bus Info
			'BusType' / squishy_bus_type,
			'ConType' / squishy_con_type,
			'SCSIVer' / squishy_scsi_ver,
		),
	)
))

pcapng_block = 'Block' / Struct(
	'Type'    / Hex(block_type),
	'Length1' / Hex(Int32ul),
	'Data'    / Switch(
		this.Type, {
			block_type.section_header: section_header_block,
			block_type.interface: interface_block,
			block_type.enhanced_packet: enhanced_packet_block,
			block_type.interface_stats: interface_statistics_block,
		},
	),
	'Size' / Computed(lambda this: this._subcons.Data.sizeof(**this)),
	'Options' / If(
		(this.Length1 - 12) > 0,
		RepeatUntil(
			lambda x, _, __: x.Code == option_type.end,
			option
		)
	),
	'Length2' / Hex(Int32ul),
)

pcapng = 'Pcapng' / GreedyRange(pcapng_block)

class PcapngFile:
	def __init__(self, *, data_stream):
		if isinstance(data_stream, bytes):
			self._data = BytesIO(data_stream)
		else:
			self._data = data_stream

		self.offset = self._data.tell()
		self._data.seek(0, SEEK_END)
		self.end = self._data.tell()
		self.size = self.end - self.offset
		self._data.seek(self.offset, SEEK_SET)

		self._pcap_file = pcapng.parse_stream(self._data)

	def __str__(self) -> str:
		return str(self._pcap_file)

if __name__ == '__main__':
	def dump_img(file_name):
		with open(file_name, 'rb') as f:
			fs = PcapngFile(data_stream = f)
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
