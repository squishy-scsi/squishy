# SPDX-License-Identifier: BSD-3-Clause
try:
	try:
		from importlib import metadata as importlib_metadata # py3.8
	except ImportError:
		import importlib_metadata # py3.7
	__version__ = importlib_metadata.version(__package__)
except ImportError:
	__version__ = ':nya_confused:' # :nocov:

import logging as log
import sys

from rich.logging import RichHandler

from .i18n import init_i18n

__all__ = (
	'main',
	'main_gui',
)

def _set_logging(args):
	level = log.INFO
	if args.verbose:
		level = log.DEBUG

	log.basicConfig(
		format   = "%(message)s",
		datefmt  = "[%X]",
		level    = level,
		handlers = [
			RichHandler(rich_tracebacks = True)
		]
	)

def _init_dirs():
	from .  import config

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
			d.mkdir(exist_ok = True)

def _main_common():
	import json

	from rich    import traceback

	from .config import SQUISHY_SETTINGS_FILE, DEFAULT_SETTINGS

	traceback.install()

	_init_dirs()
	init_i18n()

	if not SQUISHY_SETTINGS_FILE.exists():
		with SQUISHY_SETTINGS_FILE.open('w') as cfg:
			json.dump(DEFAULT_SETTINGS, cfg)

def _common_options(parser):
	core_options = parser.add_argument_group('Core configuration options')

	core_options.add_argument(
		'--verbose',
		action = 'store_true',
		help   = 'Enable verbose output during synth and pnr'
	)

def main_gui():
	from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
	from pathlib  import Path
	try:
		from .actions.gui import GUI
	except ImportError:
		log.error('To use the Squishy GUI please install PySide2')
		return 1

	try:
		_main_common()

		parser = ArgumentParser(
			formatter_class = ArgumentDefaultsHelpFormatter,
			description     = 'Squishy SCSI Multitool GUI',
			prog            = 'squishy-gui'
		)

		_common_options(parser)

		gui = GUI()

		gui.register_args(parser)

		args = parser.parse_args()

		_set_logging(args)

		return gui.run(args)
	except KeyboardInterrupt:
		log.info('bye!')

def main():
	from argparse  import ArgumentParser, ArgumentDefaultsHelpFormatter
	from pathlib   import Path

	from .collect  import collect_members, predicate_action
	from .         import actions

	try:
		_main_common()

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

		_common_options(parser)

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

		_set_logging(args)

		act = list(filter(lambda a: a['name'] == args.action, ACTIONS))[0]
		return act['instance'].run(args)
	except KeyboardInterrupt:
		log.info('bye!')

if __name__ == '__main__':
	sys.exit(main())
