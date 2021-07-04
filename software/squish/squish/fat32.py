# SPDX-License-Identifier: BSD-3-Clause
"""
	This file is used for reading, writing, and modifying FAT32 FS images
"""
from construct import *

boot_sector = Struct(
	'jmp'      / Const(b'\xEB\x00\x90'),
	'oem_name' / Bytes(8),
	'params'   / Struct(
		'bpb'             / Struct(
			'sub_bpb'        / Struct(
				'log_sec_bytes'   / Int16ul,
				'log_sec_clust'   / Bytes(1),
				'res_log_sec'     / Int16ul,
				'fat_count'       / Bytes(1),
				'max_roots'       / Int16ul,
				'total_log_sec'   / Int16ul,
				'media_desc'      / Bytes(1),
				'log_sec_per_fat' / Int16ul,
			),
			'phys_sec'       / Int16ul,
			'disk_heads'     / Int16ul,
			'hidden_sect'    / Int32ul,
			'total_log_sect' / Int32ul,
		),
		'logical_sectors' / Int32ul,
		'drive_desc'      / Bytes(2),
		'version'         / Bytes(2),
		'root_cluster_id' / Int32ul,
		'fs_logical_sec'  / Int16ul,
		'first_log_sec'   / Int16ul,
		'reserved'        / Padding(12, pattern=b'\xF6'),
		'drive_num'       / Bytes(1),
		'dunno_lol'       / Bytes(1),
		'ext_boot_sig'    / Bytes(1),
		'vol_id'          / Bytes(4),
		'vol_label'       / Bytes(11),
		'fs_type'         / Bytes(8),
	),
	'phys_drive_num' / Bytes(1),
	'boot_sig'       / Const(b'\x55\xAA')
)
