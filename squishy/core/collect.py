# SPDX-License-Identifier: BSD-3-Clause

from pkgutil    import walk_packages
from importlib  import import_module
from inspect    import getmembers, isclass
from typing     import (
	List, Dict, Union, Any
)

__all__ = (
	'collect_members',
	'predicate_applet',
	'predicate_action',
	'predicate_class',
)


def predicate_applet(member) -> bool:
	'''
	Applet predicate

	This predicate filters on if the member is a sub class of :py:class:`SquishyApplet`
	and not an instance of that class itself.

	Returns
	-------
	bool
		If the predicate matches.

	'''

	from ..applets import SquishyApplet
	if isclass(member):
		return issubclass(member, SquishyApplet) and member is not SquishyApplet
	return False

def predicate_action(member) -> bool:
	'''
	Action predicate

	This predicate filters on if the member is a sub class of :py:class:`SquishyAction`
	and not an instance of that class itself.

	Returns
	-------
	bool
		If the predicate matches.

	'''

	from ..actions import SquishyAction
	if isclass(member):
		return issubclass(member, SquishyAction) and member is not SquishyAction
	return False

def predicate_class(member) -> bool:
	'''
	Class predicate

	This predicate filters on if the member is a class.

	Returns
	-------
	bool
		If the predicate matches.

	'''

	return isclass(member)

def collect_members(pkg, pred, prefix: str = '', make_instance: bool = True) -> List[Dict[str, Union[str, Any]]]:
	'''
	Collect members from package

	This method collects list of members from a given package, and optionally creates
	and instance of them.

	Returns
	-------
	list[dict[str, tuple[str, type]]]
		The list of members, their name and type, or optionally and instance of said type.

	'''

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
