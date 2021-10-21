# SPDX-License-Identifier: BSD-3-Clause
# The contents of this module are specific to the
# 'taperipper' project: https://lethalbit.net/projects/taperipper/

from construct import *

__all__ = ()


# TODO: header / data checksums?
tape_image_fmt = Padded(int(180e6), AlignedStruct(256,
	'header'        / Padded(256, Struct(
		'magic_number'   / Const(b'NYA~'),
		'tape_length'    / Int32ub,
		'kernel_offset'  / Int32ub,
		'kernel_length'  / Int32ub,
		'initram_offset' / Int32ub,
		'initram_length' / Int32ub,
	)),
	'kernel_img'    / Array(this.header.kernel_length, Byte),
	'initramfs_img' / Array(this.header.initram_length, Byte),
))
