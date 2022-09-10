# SPDX-License-Identifier: BSD-3-Clause
from construct import (
	Padded, Padding, Const,
	Struct, Array,
	Int16ul, Int32ul, Int32ub, Int64ul,
	Bytes,

)

__all__ = ()



guid = Struct(
	'raw' / Bytes(16)
)

# Legacy MBR for GPT, prefer protective_mbr over this
legacy_mbr = Padded(int(512), Struct(
	'boot_code'      / Bytes(424),      	# boot code for non-UEFI systems
	'disk_signature' / Int32ub,				# unique disk signature
	'reserved'       / Int16ul,				# Unknown reserved
	'partition_recs' / Array(4, Struct(		# Partition Records (*4)
		'boot_indicator' / Bytes(1), 		#	Boot indicator: 0x80 for bootable
		'starting_chs'   / Bytes(3),		#	Start of partition in CHS format
		'os_type'        / Bytes(1),		#	OS Type (0xEF or 0xEE)
		'ending_chs'     / Bytes(3),		# 	End of partition in CHS format
		'starting_lba'   / Int32ul,			# 	Starting LBA of the partition
		'size_in_lba'    / Int32ul,			#	Size of partition in LBA units
	)),
	'signature'      / Const(b'\x55\xAA'),	# MBR Signature
))

protective_mbr = Struct(
	'boot_code'      / Bytes(440),
	'disk_signature' / Padding(4),
	'reserved'       / Padding(2),
	'part_records'   / Array(4, Struct(
		'boot_indicator' / Const(b'\x00'),
		'starting_chs'   / Const(b'\x00\x02\x00'),
		'os_type'        / Const(b'\xEE'),
		'ending_chs'     / Bytes(3),
		'starting_lba'   / Const(b'\x01\x00\x00\x00'),
		'size_in_lba'    / Int32ul,
	)),
	'signature'      / Const(b'\x55\xAA'),
)

gpt_header = Padded(int(512), Struct(
	'signature'     / Const(b'\x54\x52\x41\x50\x20\x49\x46\x45'),
	'revision'      / Const(b'\x00\x01\x00\x00'),
	'header_size'   / Int32ul,
	'crc32'         / Int32ul,
	Padding(4),
	'my_lba'        / Int64ul,
	'alt_lba'       / Int64ul,
	'fusable_lba'   / Int64ul,
	'luseable_lba'  / Int64ul,
	'disk_guid'     / guid,
	'part_count'    / Int32ul,
	'part_ent_size' / Int32ul,
	'part_ents_crc' / Int32ul,
))
