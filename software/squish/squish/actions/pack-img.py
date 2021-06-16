# SPDX-License-Identifier: BSD-3-Clause
from os import path
from ..utility import *

ACTION_NAME = 'pack-image'
ACTION_DESC = 'Pack gateware and boot image together'


def parser_init(parser):
	pack_image = parser.add_argument_group('Pack final flash image')

	pack_image.add_argument(
		'--boot-img', '-b',
		dest = 'boot_img',
		type = str,
		required = True,
		help = 'Image generated with `squish gen-boot-img`'
	)

	pack_image.add_argument(
		'--bitstream', '-B',
		dest = 'bitstream',
		type = str,
		required = True,
		help = 'Generated squishy bitstream'
	)

def action_main(args):
	if not path.exists(args.boot_img):
		err(f'Boot image {args.boot_img} does not exist')
		return 1

	if not path.exists(args.bitstream):
		err(f'Bitstream {args.bitstream} does not exist')
		return 1


	return 0
