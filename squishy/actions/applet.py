# SPDX-License-Identifier: BSD-3-Clause
import logging

from ..squishy_applet import SquishyApplet
from ..config         import SQUISHY_APPLETS
from ..utility        import *

ACTION_NAME = 'applet'
ACTION_DESC = 'Squishy applets'

log = logging.getLogger('squishy')

def _collect_applets(pkg):
	from pkgutil    import walk_packages
	from importlib  import import_module
	from inspect    import getmembers
	from os         import path

	applets = []

	for _, name, is_pkg in walk_packages(path = (pkg,), prefix = f'{pkg.replace("/", ".")}.'):
		if not is_pkg:
			pkg_import = import_module(name)
			found_applets = getmembers(pkg_import, lambda m: isinstance(m, SquishyApplet))
			applets.append({
				'name' : name,
				'applets': [applet for _, applet in found_applets]
			})

	return applets

def _collect_all_applets():
	from .. import applets
	return [*_collect_applets(applets.__file__), *_collect_applets(SQUISHY_APPLETS)]

def parser_init(parser):
	applets = _collect_all_applets()

	applet_parser = parser.add_subparsers(
		dest     = 'applet',
		required = True
	)

def action_main(args):
	wrn('The applet action is currently unimplemented')
	return 0
