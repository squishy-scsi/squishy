# SPDX-License-Identifier: BSD-3-Clause
from ..utility             import *

ACTION_NAME = 'taperipper'
ACTION_DESC = 'project taperipper options'




def build_bootimage(args):
	inf('Running taperipper boot image generation')
	if not path.exists(args.efi_fw):
		err(f'UEFI firmware {args.efi_fw} does not exist')
		return 1

	return 0

def pack_flash(args):
	inf('Running taperipper flash packing')
	if not path.exists(args.boot_img):
		err(f'Boot image {args.boot_img} does not exist')
		return 1

	if not path.exists(args.bitstream):
		err(f'Bitstream {args.bitstream} does not exist')
		return 1

	return 0

def mkboot_tape(args):
	inf('Running taperipper make boot tape')
	from ..taperipper import tape_image_fmt

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

TAPERIPPER_ACTIONS = {
	'build-bootimage': build_bootimage,
	'pack-flash': pack_flash,
	'make-boot-tape': mkboot_tape
}

def parser_init(parser):
	actions = parser.add_subparsers(dest = 'taperipper_actions')

	bootimage_action = actions.add_parser(
		'build-bootimage',
		help = 'build UEFI boot image'
	)

	packflash_action = actions.add_parser(
		'pack-flash',
		help = 'pack squishy flash image'
	)

	mkboottap_action = actions.add_parser(
		'make-boot-tape',
		help = 'create the boot tape'
	)

	bootimage_action.add_argument(
		'--efi-fw', '-f',
		dest = 'efi_fw',
		type = str,
		required = True,
		help = 'UEFI firmware blob to pack'
	)

	packflash_action.add_argument(
		'--boot-img', '-i',
		dest = 'boot_img',
		type = str,
		required = True,
		help = 'Image generated with `squishy taperipper build-bootimage`'
	)

	packflash_action.add_argument(
		'--bitstream', '-B',
		dest = 'bitstream',
		type = str,
		required = True,
		help = 'Generated squishy bitstream'
	)


	mkboottap_action.add_argument(
		'--kernel-image', '-K',
		dest = 'kernel_image',
		type = str,
		required = True,
		help = 'Kernel Image to pack'
	)

	mkboottap_action.add_argument(
		'--initramfs-image', '-I',
		dest = 'initramfs_image',
		type = str,
		required = True,
		help = 'Kernel initramfs image to pack for loading'
	)

	mkboottap_action.add_argument(
		'--image-output', '-i',
		dest = 'image_file_name',
		type = str,
		default = 'squishy-tape.img',
		help = 'The output file name for the tape image'
	)

	mkboottap_action.add_argument(
		'--tape-size', '-T',
		dest = 'tape_size',
		type = int,
		default = 180e6,
		help = 'The size of the tape in bytes'
	)

	mkboottap_action.add_argument(
		'--tape-block-size', '-B',
		dest = 'tape_block_size',
		type = int,
		default = 256,
		help = 'The size of the native block on the tape'
	)


def action_main(args):
	return TAPERIPPER_ACTIONS.get(args.taperipper_actions, lambda _: 1)(args)