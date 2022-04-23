# SPDX-License-Identifier: BSD-3-Clause

from pkgutil    import walk_packages
from importlib  import import_module
from inspect    import getmembers, isclass

__all__ = (
	'collect_members',
	'predicate_applet',
	'predicate_action',
	'predicate_class',
)


def predicate_applet(member):
	from ..applets import SquishyApplet
	if isclass(member):
		return issubclass(member, SquishyApplet) and member is not SquishyApplet
	return False

def predicate_action(member):
	from ..actions import SquishyAction
	if isclass(member):
		return issubclass(member, SquishyAction) and member is not SquishyAction
	return False

def predicate_class(member):
	return isclass(member)

def collect_members(pkg, pred, prefix = '', make_instance = True):
	pkg = str(pkg)

	members = list()

	for _, pkg_name, __ in walk_packages(
		path  = (pkg,),
		prefix = prefix
	):
		pkg_import    = import_module(pkg_name)
		found_members = getmembers(pkg_import, pred)

		if len(found_members) > 0:
			for name, member in found_members:
				members.append({
					'name'    : name.lower(),
					'instance': member() if make_instance else member
				})

	return members