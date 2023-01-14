# SPDX-License-Identifier: BSD-3-Clause
import logging     as log
from argparse      import ArgumentParser, ArgumentDefaultsHelpFormatter, Namespace
from pathlib       import Path

from rich         import traceback
from rich.logging import RichHandler

from .             import actions, config
from .core.collect import collect_members, predicate_action
from .core.device  import SquishyHardwareDevice

__all__ = (
	'main',
)

def setup_logging(args: Namespace = None) -> None:
	'''
	Initialize logging subscriber

	Set up the built-in rich based logging subscriber, and force it
	to be the one at runtime in case there is already one set up.

	Parameters
	----------
	args : argparse.Namespace
		Any command line arguments passed.

	'''

	level = log.INFO
	if args is not None and args.verbose:
		level = log.DEBUG

	log.basicConfig(
		force    = True,
		format   = '%(message)s',
		datefmt  = '[%X]',
		level    = level,
		handlers = [
			RichHandler(rich_tracebacks = True, show_path = False)
		]
	)

def init_dirs() -> None:
	'''
	Initialize Squishy application directories.

	Creates all of the appropriate directories that Squishy
	expects, such as the config, and cache directories.

	This uses the XDG_* environment variables if they exist,
	otherwise they assume that all the needed dirs are in the
	running users home directory.

	'''

	dirs = (
		config.SQUISHY_CACHE,
		config.SQUISHY_DATA,
		config.SQUISHY_CONFIG,

		config.SQUISHY_APPLETS,
		config.SQUISHY_APPLET_CACHE,

		config.SQUISHY_BUILD_DIR,
	)

	for d in dirs:
		if not d.exists():
			d.mkdir(parents = True, exist_ok = True)


def main() -> int:
	'''
	Squishy CLI/REPL Runner

	This is the main invocation point for the Squishy CLI and REPL.

	Returns
	-------
	int
		0 if execution was successful, otherwise any other integer on error

	'''

	try:
		traceback.install()

		init_dirs()
		setup_logging()

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

		core_options = parser.add_argument_group('Core configuration options')

		core_options.add_argument(
			'--verbose', '-v',
			action = 'store_true',
			help   = 'Enable verbose output during synth and pnr'
		)

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
