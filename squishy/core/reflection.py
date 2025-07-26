# SPDX-License-Identifier: BSD-3-Clause

'''
This module provides runtime/dynamic reflection helpers for iterating Python
module/package contents and the like.

'''

from collections.abc import Callable
from importlib       import import_module
from inspect         import getmembers, isclass
from pkgutil         import walk_packages

__all__ = (
	'collect_members',
	# Helper predicates
	'is_applet',
)

# TODO(aki): This is likely awful
def is_applet(member: object) -> bool:
	'''
	Determine if the given object is a :py:class:`SquishyApplet` or not.

	Parameters
	----------
	member : object
		The member object to inspect

	Returns
	-------
	bool
		Returns True if the given ``member`` object is an instance of :py:class:`SquishyApplet`, otherwise False.
	'''

	from ..applets import SquishyApplet
	if isclass(member):
		return issubclass(member, SquishyApplet) and member is not SquishyApplet
	return False

# TODO(aki): This is slow and bad, needs a re-think
def collect_members(pkg: str, predicate: Callable[[object], bool], prefix: str = '', make_instance: bool = False):
	'''
	Collect members from package.

	This method collects a list of members from a given package, and optionally
	creates an instance of them.

	Parameters
	----------
	pkg : str
		The name of the Python package to iterate over.

	predicate : Callable[[object], bool]
		The discriminator predicate used to filter members.

	prefix : str
		The prefix to add to the result of the package walk.

	make_instance : bool
		If True, instantiate an instance of the found types matching the predicate prior to returning.

	Returns
	-------

	'''

	members = []

	for (_, name, _) in walk_packages(path = (pkg, ), prefix = prefix):
		pkg_import     = import_module(name)
		found_members  = getmembers(pkg_import, predicate)

		if len(found_members) > 0:
			for (_, member) in found_members:
				members.append(member if not make_instance else member())

	return members
