# SPDX-License-Identifier: BSD-3-Clause
import logging    as log
import json

from rich         import traceback
from rich.logging import RichHandler

from ..           import config

__all__ = (
	'setup_logging',
	'init_dirs',
	'main_common',
	'common_options',
)


def setup_logging(args = None) -> None:
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

def init_dirs() -> None:
	'''Initialize Squishy application directories.

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
			d.mkdir(exist_ok = True)

def main_common() -> None:
	'''Squishy common initialization.

	This method initializes things like the application
	directories if they don't exist, as well as installing
	the rich based log handler.

	It also creates the settings JSON file if it doesn't exist.

	'''

	traceback.install()

	init_dirs()
	setup_logging()

	if not config.SQUISHY_SETTINGS_FILE.exists():
		with config.SQUISHY_SETTINGS_FILE.open('w') as cfg:
			json.dump(config.DEFAULT_SETTINGS, cfg)

def common_options(parser) -> None:
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
