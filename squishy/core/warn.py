# SPDX-License-Identifier: BSD-3-Clause

'''

This module contains the internal implementation of the ``showwarning`` override that Squishy uses to produce pretty
warning messages.

It also contains two methods, :py:meth:`install_handler` to install the warning handler as it is not done by default and
also :py:meth:`remove_handler` to replace the "original" ``showwarning`` handler.

'''

import linecache
import logging    as log
import warnings
from typing       import TypedDict

from rich         import get_console
from rich.padding import Padding
from rich.panel   import Panel
from rich.syntax  import Syntax

__all__ = (
	'install_handler',
	'remove_handler'
)

# Cache the original handler in case we need to restore it
_original_handler = warnings.showwarning


class DumpfileSettings(TypedDict):
	dump_lines: bool
	line_range: int
	dump_width: int

# TODO(aki): Eventually make these configurable
_dump_settings: DumpfileSettings = {
	'dump_lines': True,
	'line_range': 5,
	'dump_width': 100
}

def _dump_file_lines(file: str, line: int) -> None:
	cons = get_console()

	# Get the module code from the line cache
	code = ''.join(linecache.getlines(file))

	# Code might just not exist
	if not code:
		return

	code_ctx = (
		line - _dump_settings['line_range'],
		line + _dump_settings['line_range']
	)
	width = cons.width if cons.width < _dump_settings['dump_width'] else _dump_settings['dump_width']

	syn = Syntax(
		code, 'python',
		theme = Syntax.get_theme('ansi_dark'),
		line_numbers = True,
		line_range = code_ctx,
		highlight_lines={line},
		code_width = width,
		indent_guides = True,
		word_wrap = True,
		dedent = False,
	)

	code_panel = Panel.fit(
		syn, title = f'[cyan]{file}[/][white]:[/][magenta]{line}[/]',
		border_style = 'yellow'
	)

	# NOTE(aki): This is kinda a super jank way to pad  the frame, but w/e
	cons.print(Padding(code_panel, pad = (0, 0, 0, 11)))

# We don't care about the `file` or `line` args in our handler, they're optional anyway, so just discard them
def _warning_handler(msg: Warning | str, cat: type[Warning], fname: str, lineno: int, *_) -> None:
	'''
	Custom replacement warning handler for Squishy.

	Parameters
	----------
	msg : Warning | str
		The warning message itself.

	cat : type[Warning]
		The category of the warning.

	fname : str
		The file name of the warning.

	lineno : int
		The line of the file the warning was invoked on.
	'''

	do_src_dump = _dump_settings['dump_lines'] and fname != 'sys'

	if isinstance(msg, Warning):
		pass

	log.warning(f'[green]{cat.__name__}[/][white]:[/] {msg}', extra = { 'markup': True })
	# If we are allowed to dump the source and it's not the magic sys module then do so.
	if do_src_dump:
		_dump_file_lines(fname, lineno)
	else:
		log.warning(
			f'Warning originated from: [cyan]{fname}[/][white]:[/][magenta]{lineno}[/]', extra = { 'markup': True }
		)


def install_handler(reset_filter: bool = False) -> None:
	'''
	Replace the python ``warnings.showwarning`` handler with our own.

	Parameters
	----------
	reset_filter : bool
		Reset the python warnings filter so we catch all warnings.

	'''

	if reset_filter:
		# We reset all the warning filters because we want make sure we display them
		warnings.resetwarnings()

	warnings.showwarning = _warning_handler

def remove_handler() -> None:
	'''
	Replace the original value of ``warnings.showwarning`` from when this module was loaded, may not be the built-in
	'''

	warnings.showwarning = _original_handler
