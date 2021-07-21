# SPDX-License-Identifier: BSD-3-Clause
from .utility import *

from .board import Rev1

from .main import Squishy

__all__ = [ 'cli' ]


def cli():
	import sys
	from os import path, mkdir
	from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
	from nmigen import cli as nmigen_cli

	parser = ArgumentParser(formatter_class = ArgumentDefaultsHelpFormatter, description = 'Squishy gateware generation')
	nmigen_cli.main_parser(parser)
	actions = parser._subparsers._group_actions[0]

	do_verify = actions.add_parser('verify', help = 'Run formal verification')
	verify_options = do_verify.add_argument_group('Verification options')

	core_options   = parser.add_argument_group('Core configuration options')
	usb_options    = parser.add_argument_group('USB PHY Options')
	uart_options   = parser.add_argument_group('Debug UART Options')
	scsi_options   = parser.add_argument_group('SCSI Options')



	core_options.add_argument(
		'--build-dir', '-b',
		type    = str,
		default = 'build',
		help    = 'The build directory for the Squishy gateware'
	)

	usb_options.add_argument(
		'--vid', '-V',
		type    = int,
		default = 0xFEED,
		help    = 'The USB Vendor ID to use'
	)

	usb_options.add_argument(
		'--pid', '-P',
		type    = int,
		default = 0xACA7,
		help    = 'The USB Product ID to use'
	)

	usb_options.add_argument(
		'--manufacturer', '-m',
		type    = str,
		default = 'aki-nyan',
		help    = 'The USB Device Manufacturer'
	)

	usb_options.add_argument(
		'--product', '-p',
		type    = str,
		default = 'squishy',
		help    = 'The USB Device Product'
	)

	usb_options.add_argument(
		'--serial_number', '-s',
		type    = str,
		default = 'ニャ〜',
		help    = 'The USB Device Serial Number'
	)


	uart_options.add_argument(
		'--enable-uart', '-U',
		default = False,
		action  = 'store_true',
		help    = 'Enable the debug UART',
	)

	uart_options.add_argument(
		'--baud', '-B',
		type    = int,
		default = 9600,
		help    = 'The rate at which to run the debug UART'
	)

	uart_options.add_argument(
		'--data-bits', '-D',
		type    = int,
		default = 8,
		help    = 'The data bits to use for the UART'
	)

	uart_options.add_argument(
		'--parity', '-c',
		type    = str,
		choices = [
			'none', 'mark', 'space'
			'even', 'odd'
		],
		default = 'none',
		help    = 'The parity mode for the debug UART'
	)

	args = parser.parse_args()

	plat = Rev1()

	gateware = Squishy(
		enable_uart = args.enable_uart,
		uart_baud   = args.baud,
		uart_parity = args.parity,
		uart_data   = args.data_bits,

		vid = args.vid,
		pid = args.pid,

		manufacturer  = args.manufacturer,
		product       = args.product,
		serial_number = args.serial_number
	)

	if args.action == 'verify':
		wrn('todo')
	else:
		plat.build(gateware, name = 'squishy', build_dir = args.build_dir, do_build = True)
	return 0
