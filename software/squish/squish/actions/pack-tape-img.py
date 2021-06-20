# SPDX-License-Identifier: BSD-3-Clause
from os import path, stat
from ..utility import *

from construct import *

ACTION_NAME = 'pack-tape-img'
ACTION_DESC = 'Pack the bootable tape image to be written to the boot tape'

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

def parser_init(parser):
	pack_tape_img = parser.add_argument_group('Pack tape image')

	pack_tape_img.add_argument(
		'--kernel-image', '-K',
		dest = 'kernel_image',
		type = str,
		required = True,
		help = 'Kernel Image to pack'
	)

	pack_tape_img.add_argument(
		'--initramfs-image', '-I',
		dest = 'initramfs_image',
		type = str,
		required = True,
		help = 'Kernel initramfs image to pack for loading'
	)

	pack_tape_img.add_argument(
		'--image-output', '-i',
		dest = 'image_file_name',
		type = str,
		default = 'squishy-tape.img',
		help = 'The output file name for the tape image'
	)

	pack_tape_img.add_argument(
		'--tape-size', '-T',
		dest = 'tape_size',
		type = int,
		default = 180e6,
		help = 'The size of the tape in bytes'
	)

	pack_tape_img.add_argument(
		'--tape-block-size', '-B',
		dest = 'tape_block_size',
		type = int,
		default = 256,
		help = 'The size of the native block on the tape'
	)

def action_main(args):
	if not path.exists(args.kernel_image):
		err(f'Kernel image {args.kernel_image} does not exist')
		return 1

	if not path.exists(args.initramfs_image):
		err(f'Kernel initramfs image {args.initramfs_image} does not exist')
		return 1

	kernel_size = stat(args.kernel_image).st_size
	initramfs_size = stat(args.initramfs_image).st_size
	tape_img_size = (256 + kernel_size + initramfs_size)

	tape_img_file = path.join(args.build_dir, args.image_file_name)

	log(f'Kernel is {kernel_size} bytes long')
	log(f'initramfs is {initramfs_size} bytes long')

	if tape_img_size > args.tape_size:
		err(f'The total size of the tape image ({tape_img_size} bytes) exceeds that of the total size available on the tape ({args.tape_size} bytes)')

	log(f'Total tape image length will be {tape_img_size} bytes')
	log(f'Output file {tape_img_file}')

	with open(tape_img_file, 'wb') as tape_image:
		kimg_data = None
		iimg_data = None

		with open(args.kernel_image, 'rb') as kimg:
			kimg_data = kimg.read()

		with open(args.initramfs_image, 'rb') as iimg:
			iimg_data = iimg.read()

		tape_img = tape_image_fmt.build(dict(
			header = dict(
				tape_length    = tape_img_size,
				kernel_offset  = 256,
				kernel_length  = kernel_size,
				initram_offset = (256 + kernel_size),
				initram_length = initramfs_size,
			),
			kernel_img    = kimg_data,
			initramfs_img = iimg_data,
		))

		tape_image.write(tape_img)


	return 0
