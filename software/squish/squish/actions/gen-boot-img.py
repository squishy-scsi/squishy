# SPDX-License-Identifier: BSD-3-Clause
from os import path
from ..utility import *

ACTION_NAME = 'gen-boot-img'
ACTION_DESC = 'Generate the UEFI boot image'


def parser_init(parser):
	gen_boot_img = parser.add_argument_group('Generate boot image')

	gen_boot_img.add_argument(
		'--efi-fw', '-f',
		dest = 'efi_fw',
		type = str,
		required = True,
		help = 'UEFI firmware blob to pack'
	)

def action_main(args):
	if not path.exists(args.efi_fw):
		err(f'UEFI firmware {args.efi_fw} does not exist')
		return 1

	return 0
