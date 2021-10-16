# SPDX-License-Identifier: BSD-3-Clause
from os             import path

from ..             import __version__
from ..config       import SQUISHY_HISTORY_FILE, SQUISHY_SETTINGS_FILE, SQUISHY_SPLASH_MESSAGES
from ..utility      import print_table


from prompt_toolkit                import PromptSession
from prompt_toolkit                import print_formatted_text as print
from prompt_toolkit.formatted_text import FormattedText
from prompt_toolkit.completion     import NestedCompleter
from prompt_toolkit.auto_suggest   import AutoSuggestFromHistory
from prompt_toolkit.history        import FileHistory

ACTION_NAME = 'interactive-shell'
ACTION_DESC = 'Interactive SCSI command shell'

def _collect_commands():
	import pkgutil
	from .. import repl

	# todo make this not garbage by using importlib
	commands = []
	for _, name, is_pkg in pkgutil.iter_modules(path = getattr(repl, '__path__')):
		if not is_pkg:
			__import__(f'{getattr(repl, "__name__")}.{name}')
			if not hasattr(getattr(repl, name), 'DONT_LOAD'):
				commands.append({
					'name': getattr(repl, name).__name__.split('.')[-1],
					'help': getattr(repl, name).__doc__,
					'init': getattr(repl, name).init,
					'main': getattr(repl, name).main,
				})

	return commands

def parser_init(parser):
	pass

def _repl_ctx_to_prompt(ctx):
	if ctx['interface'] is None:
		return 'no interface> '
	else:
		return f'{ctx["interface"]!s}> '

def action_main(args):
	from random import choice

	banner = fr'''
------------------------------------------
 ####   ####  #    # #  ####  #    # #   #
#      #    # #    # # #      #    #  # #
 ####  #    # #    # #  ####  ######   #
     # #  # # #    # #      # #    #   #
#    # #   #  #    # # #    # #    #   #
 ####   ### #  ####  #  ####  #    #   #
------------------------------------------
############ Interactive REPL ############
------------------------------------------
> '{choice(SQUISHY_SPLASH_MESSAGES)}'

squishy version: {__version__}

type 'help <command>' for help on a command,
and 'list' to list commands.

type 'exit' or press ^D to exit
'''

	repl_ctx = {
		'device': None,
		'interface': None,
	}

	commands = _collect_commands()

	completion_dict = {
		'list': None,
		'exit': None,
		'help': {}, # todo: can be list?
	}

	for cmd in commands:
		completion_dict['help'][cmd['name']] = None
		completion_dict[cmd['name']] = cmd['init']()

	command_cmplt = NestedCompleter.from_nested_dict(completion_dict)

	session = PromptSession(
		completer = command_cmplt,
		history   = FileHistory(SQUISHY_HISTORY_FILE)
	)

	print(banner)
	ret = 0

	while True:
		try:
			text = session.prompt(
				_repl_ctx_to_prompt(repl_ctx),
				auto_suggest = AutoSuggestFromHistory(),
				rprompt = ':(' if ret == 1 else ''
			)
		except KeyboardInterrupt:
			continue
		except EOFError:
			break
		else:
			if text == 'exit':
				break
			elif text == 'list':
				print_table(map(lambda a: a['name'], commands))
			elif text == 'nya':
				print(choice(SQUISHY_SPLASH_MESSAGES))
			else:
				line = text.split(' ')

				if line[0] == 'help':
					if len(line) == 1:
						print('usage: help <command>')
						ret = 0
					elif line[1] not in map(lambda a: a['name'], commands):
						print(f'Unknown command {line[1]}')
						ret = 1
					else:
						print(list(filter(lambda a: a['name'] == line[1], commands))[0]['help'], end='')
						ret = 0
				elif line[0] not in map(lambda a: a['name'], commands):
					print(f'Unknown command {line[0]}')
					ret = 1
				else:
					cmd = list(filter(lambda a: a['name'] == line[0], commands))[0]
					ret = cmd['main'](repl_ctx)

	return 0
