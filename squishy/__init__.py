# SPDX-License-Identifier: BSD-3-Clause
try:
	try:
		from importlib import metadata as importlib_metadata # py3.8
	except ImportError:
		import importlib_metadata # py3.7
	__version__ = importlib_metadata.version(__package__)
except ImportError:
	__version__ = ':nya_confused:' # :nocov:

import logging    as log

from rich.logging import RichHandler

from .core.device import SquishyDeviceContainer

__all__ = (
	'main',
	'main_gui',
)

def _set_logging(args = None) -> None:
	'''Initialize logging subscriber

	Set up the built-in rich based logging subscriber, and force it
	to be the one at runtime in case there is already one set up.

	Parameters
	----------
	args : argsparse.Namespace
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
			RichHandler(rich_tracebacks = True)
		]
	)

def _init_dirs() -> None:
	'''Initialize Squishy application directories.

	Creates all of the appropriate directories that Squishy
	expects, such as the config, and cache directories.

	This uses the XDG_* environment variables if they exist,
	otherwise they assume that all the needed dirs are in the
	running users home directory.

	'''

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

def _main_common() -> None:
	'''Squishy common initialization.

	This method initializes things like the application
	directories if they don't exist, as well as installing
	the rich based log handler.

	It also creates the settings JSON file if it doesn't exist.

	'''

	import json

	from rich    import traceback

	from .config import SQUISHY_SETTINGS_FILE, DEFAULT_SETTINGS

	traceback.install()

	_init_dirs()
	_set_logging()

	if not SQUISHY_SETTINGS_FILE.exists():
		with SQUISHY_SETTINGS_FILE.open('w') as cfg:
			json.dump(DEFAULT_SETTINGS, cfg)

def _common_options(parser) -> None:
	'''Initialize common CLI options.

	Registers common options between the CLI and GUI for invocation.

	Parameters
	----------
	parser : argparse.ArgumentParser
		The argument parser to register commands with.

	'''

	core_options = parser.add_argument_group('Core configuration options')

	core_options.add_argument(
		'--verbose',
		action = 'store_true',
		help   = 'Enable verbose output during synth and pnr'
	)

def main_gui() -> int:
	'''Squishy GUI Runner

	This is the main invocation point for the Squishy QT5 GUI.

	Returns
	-------
	int
		0 if execution was successfull, otherwise any other integer on error

	'''
	from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
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

def _get_device(args):
	'''Get attached Squishy device.

	Get the attached and selected squishy device if possible, or if only
	one is attached to the system use that one.

	Parameters
	----------
	args : argsparse.Namespace
		Any command line arguments passed.

	Returns
	-------
	None
		If no device is selected

	squishy.core.device.SquishyHardwareDevice
		The selected hardware if available.

	'''

	devices = list(SquishyDeviceContainer.enumerate())
	dev_count = len(devices)
	if dev_count > 1:
		if args.device is None:
			log.error(f'No device serial number specified, unable to pick from the {dev_count} devices.')
			log.info('Connected devices are:')
			for d in devices:
				log.info(f'\t{d.serial}')
			return None

		devs = list(filter(lambda d: d.serial == args.device, devices))

		if len(devs) == 0:
			log.error(f'No device with serial number \'{args.device}\'')
			log.info('Connected devices are:')
			for d in devices:
				log.info(f'\t{d.serial}')
			return None
		elif len(devs) > 1:
			log.error('Multiple Squishy devices with the same serial number found.')
			return None
		else:
			log.info(f'Found Squishy rev{devs[0].rev} \'{devs[0].serial}\'')
			return devs[0].to_device()
	elif dev_count == 1:
		if args.device is not None:
			if args.device != devices[0].serial:
				log.error(f'Connected Squishy has serial of \'{devices[0].serial}\', but device serial \'{args.device}\' was specified.')
				return None
		else:
			log.warning('No serial number specified.')
			log.warning('Using only Squishy attached to system.')
		log.info(f'Found Squishy rev{devices[0].rev} \'{devices[0].serial}\'')
		return devices[0].to_device()
	else:
		log.error('No Squishy devices attached to system.')
		return None

def main() -> int:
	'''Squishy CLI/REPL Runner

	This is the main invocation point for the Squishy CLI and REPL.

	Returns
	-------
	int
		0 if execution was successfull, otherwise any other integer on error

	'''

	from argparse      import ArgumentParser, ArgumentDefaultsHelpFormatter
	from pathlib       import Path

	from .core.collect import collect_members, predicate_action
	from .             import actions

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

		parser.add_argument(
			'--device', '-d',
			type = str,
			help = 'The serial number of the squishy to use if more than one is attached'
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

		if act['instance'].requires_dev:
			dev = _get_device(args)
			if dev is not None:
				return act['instance'].run(args, dev)
			else:
				log.error('No device selected, unable to continue.')
		else:
			return act['instance'].run(args)
	except KeyboardInterrupt:
		log.info('bye!')
