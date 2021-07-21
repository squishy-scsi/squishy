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

	core_options = parser.add_argument_group('Core configuration options')
	verify_options = do_verify.add_argument_group('Verification options')


	core_options.add_argument(
		'--build-dir', '-b',
		type    = str,
		default = 'build',
		help    = 'The build directory for the Squishy gateware'
	)

	core_options.add_argument(
		'--vid', '-V',
		type    = int,
		default = 0xFEED,
		help    = 'The USB Vendor ID to use'
	)

	core_options.add_argument(
		'--pid', '-P',
		type    = int,
		default = 0xACA7,
		help    = 'The USB Product ID to use'
	)

	core_options.add_argument(
		'--enable-uart', '-U',
		default = False,
		action  = 'store_true',
		help    = 'Enable the debug UART',
	)

	core_options.add_argument(
		'--baud', '-B',
		type    = int,
		default = 9600,
		help    = 'The rate at which to run the debug UART'
	)

	args = parser.parse_args()

	plat = Rev1()

	gateware = Squishy(
		uart_baud   = args.baud,
		enable_uart = args.enable_uart,
		vid         = args.vid,
		pid         = args.pid
	)

	if args.action == 'verify':
		wrn('todo')
	else:
		plat.build(gateware, name = 'squishy', build_dir = args.build_dir, do_build = True)
	return 0
