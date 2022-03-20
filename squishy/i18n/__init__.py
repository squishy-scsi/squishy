# SPDX-License-Identifier: BSD-3-Clause

import locale
from sys import platform
from os  import environ
import gettext

__all__ = (
	'init_i18n',
)

def _get_locale():
	l = locale.getlocale()
	lname = None
	if platform == 'win32':
		lname = locale.windows_locale.get(l[1], None)
	else:
		lname = l[0]

	return frozenset(lname, l)

def init_i18n():
	lc = _get_locale()
	# TODO: nyaaa
