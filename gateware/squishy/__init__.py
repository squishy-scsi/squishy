# SPDX-License-Identifier: BSD-3-Clause
from .utility             import *


__all__ = (
	'main',
)


def _collect_actions():
	import pkgutil
	from . import actions

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

def main():
	import sys
	from os import path, mkdir
	from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

	ACTIONS = _collect_actions()

	parser = ArgumentParser(formatter_class = ArgumentDefaultsHelpFormatter, description = 'Squishy gateware generation')

	core_options   = parser.add_argument_group('Core configuration options')

	core_options.add_argument(
		'--build-dir', '-b',
		type    = str,
		default = 'build',
		help    = 'The output directory for Squishy binaries and images'
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

	return act['main'](args)
