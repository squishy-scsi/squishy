# SPDX-License-Identifier: BSD-3-Clause
from .utility    import *
from .platform   import Rev1
from .core       import Squishy
from .simulation import *

__all__ = (
	'cli',
)


def cli():
	import sys
	from os import path, mkdir
	from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

	parser = ArgumentParser(formatter_class = ArgumentDefaultsHelpFormatter, description = 'Squishy gateware generation')
	actions = parser.add_subparsers(dest = 'action')

	do_verify = actions.add_parser('verify', help = 'Run formal verification')
	verify_options = do_verify.add_argument_group('Verification options')

	do_simulation  = actions.add_parser('simulate', help = 'Run simulation test cases')
	sim_options    = do_simulation.add_argument_group('Simulation Options')

	do_build       = actions.add_parser('build', help = 'Build the gateware')

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

	if args.action == 'verify':
		wrn('todo')
	elif args.action == 'simulate':
		run_sims(args)
	elif args.action == 'build':
		gateware = Squishy(
			uart_config = {
				'enabled'  : args.enable_uart,
				'baud'     : args.baud,
				'parity'   : args.parity,
				'data_bits': args.data_bits,
			},

			usb_config = {
				'vid': args.vid,
				'pid': args.pid,

				'mfr': args.manufacturer,
				'prd': args.product,
				'srn': args.serial_number,
			},

			scsi_config = {}
		)

		plat.build(gateware, name = 'squishy', build_dir = args.build_dir, do_build = True)
	else:
		inf('ニャー')
	return 0
