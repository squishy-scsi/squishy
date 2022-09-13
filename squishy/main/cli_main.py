# SPDX-License-Identifier: BSD-3-Clause
import logging      as log
from argparse       import ArgumentParser, ArgumentDefaultsHelpFormatter
from pathlib        import Path

from ..             import actions
from .common        import (
	main_common, common_options, setup_logging
)
from ..core.collect import collect_members, predicate_action
from ..core.device  import SquishyHardwareDevice

def main() -> int:
	'''Squishy CLI/REPL Runner

	This is the main invocation point for the Squishy CLI and REPL.

	Returns
	-------
	int
		0 if execution was successfull, otherwise any other integer on error

	'''

	try:
		main_common()

		ACTIONS = collect_members(
			Path(actions.__path__[0]),
			predicate_action,
			f'{actions.__name__}.'
		)

		parser = ArgumentParser(
			formatter_class = ArgumentDefaultsHelpFormatter,
			description     = 'Squishy SCSI Multitool',
			prog            = 'squishy'
		)

		parser.add_argument(
			'--device', '-d',
			type = str,
			help = 'The serial number of the squishy to use if more than one is attached'
		)

		common_options(parser)

		action_parser = parser.add_subparsers(
			dest = 'action',
			required = True
		)

		if len(ACTIONS) > 0:
			for act in ACTIONS:
				action = act['instance']
				p = action_parser.add_parser(
						act['name'],
						help = action.short_help,
					)
				action.register_args(p)

		args = parser.parse_args()

		setup_logging(args)

		act = list(filter(lambda a: a['name'] == args.action, ACTIONS))[0]

		if act['instance'].requires_dev:
			dev = SquishyHardwareDevice.get_device(serial = args.device)
			if dev is not None:
				return act['instance'].run(args, dev)
			else:
				log.error('No device selected, unable to continue.')
		else:
			return act['instance'].run(args)
	except KeyboardInterrupt:
		log.info('bye!')
