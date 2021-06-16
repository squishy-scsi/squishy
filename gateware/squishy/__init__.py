# SPDX-License-Identifier: BSD-3-Clause
from .utility import *

from .board import Rev0, Rev1

from .main import SquishyTop

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
		'--build-dir',
		type = str,
		default = 'build',
		help = 'The build directory for the Squishy gateware'
	)


	args = parser.parse_args()

	plat = Rev0()

	if args.action == 'verify':
		wrn('todo')
	else:
		plat.build(SquishyTop(), name = 'squishy', build_dir = args.build_dir, do_build = True)
	return 0
