# SPDX-License-Identifier: BSD-3-Clause
try:
	try:
		from importlib import metadata as importlib_metadata # py3.8
	except ImportError:
		import importlib_metadata # py3.7
	__version__ = importlib_metadata.version(__package__)
except ImportError:
	__version__ = ':nya_confused:' # :nocov:

from .i18n     import init_i18n
from .gateware import platform
from .utility  import *

__all__ = (
	'main',
)

def _init_dirs():
	from .  import config
	from os import path, makedirs

	dirs = (
		config.SQUISHY_CACHE,
		config.SQUISHY_DATA,
		config.SQUISHY_CONFIG,

		config.SQUISHY_APPLETS,
	)

	for d in dirs:
		if not path.exists(d):
			makedirs(d, exist_ok = True)

def _collect_actions():
	import pkgutil
	from . import actions

	# todo make this not garbage by using importlib
	acts = []
	for _, name, is_pkg in pkgutil.iter_modules(path = getattr(actions, '__path__')):
		if not is_pkg:
			__import__(f'{getattr(actions, "__name__")}.{name}')
			if not hasattr(getattr(actions, name), 'DONT_LOAD'):
				acts.append({
					'name': getattr(actions, name).ACTION_NAME,
					'description': getattr(actions, name).ACTION_DESC,
					'parser_init': getattr(actions, name).parser_init,
					'main': getattr(actions, name).action_main,
				})

	return acts

def _main_common():
	import json
	from os import path

	from .config import SQUISHY_SETTINGS_FILE, DEFAULT_SETTINGS

	_init_dirs()
	init_i18n()

	if not path.exists(SQUISHY_SETTINGS_FILE):
		with open(SQUISHY_SETTINGS_FILE, 'w') as cfg:
			json.dump(DEFAULT_SETTINGS, cfg)

def main_gui():
	import sys
	from os import path, mkdir
	from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

	from .actions import gui

	_main_common()

	parser = ArgumentParser(formatter_class = ArgumentDefaultsHelpFormatter, description = 'Squishy gateware generation')

	core_options = parser.add_argument_group('Core configuration options')

	core_options.add_argument(
		'--build-dir', '-b',
		type    = str,
		default = 'build',
		help    = 'The output directory for Squishy binaries and images'
	)

	core_options.add_argument(
		'--platform', '-p',
		dest    = 'hardware_platform',
		type    = str,
		default = list(platform.AVAILABLE_PLATFORMS.keys())[-1],
		choices = list(platform.AVAILABLE_PLATFORMS.keys()),
		help    = 'The target hardware platform',
	)

	gui.parser_init(parser)

	args = parser.parse_args()

	if not path.exists(args.build_dir):
		mkdir(args.build_dir)

	return gui.action_main(args)

def main():
	import sys
	from os import path, mkdir
	from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

	_main_common()

	ACTIONS = _collect_actions()

	parser = ArgumentParser(formatter_class = ArgumentDefaultsHelpFormatter, description = 'Squishy gateware generation')

	core_options = parser.add_argument_group('Core configuration options')

	core_options.add_argument(
		'--build-dir', '-b',
		type    = str,
		default = 'build',
		help    = 'The output directory for Squishy binaries and images'
	)

	core_options.add_argument(
		'--platform', '-p',
		dest    = 'hardware_platform',
		type    = str,
		default = list(platform.AVAILABLE_PLATFORMS.keys())[-1],
		choices = list(platform.AVAILABLE_PLATFORMS.keys()),
		help    = 'The target hardware platform',
	)

	action_parser = parser.add_subparsers(
		dest = 'action',
		required = True
	)

	for act in ACTIONS:
		a = action_parser.add_parser(
				act['name'],
				help = act['description']
			)
		act['parser_init'](a)

	args = parser.parse_args()

	if not path.exists(args.build_dir):
		mkdir(args.build_dir)

	if args.action not in map(lambda a: a['name'], ACTIONS):
		err(f'Unknown action {args.action}')
		err(f'Known actions {", ".join(map(lambda a: a["name"], ACTIONS))}')
		return 1
	else:
		act = list(filter(lambda a: a['name'] == args.action, ACTIONS))[0]

	log(f'Targeting platform \'{args.hardware_platform}\'')
	return act['main'](args)
