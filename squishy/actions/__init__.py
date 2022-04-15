# SPDX-License-Identifier: BSD-3-Clause

from abc import ABCMeta, abstractmethod, abstractproperty

__all__ = (
	'SquishyAction',
)

class SquishyAction(metaclass = ABCMeta):
	pretty_name  = abstractproperty()
	short_help   = abstractproperty()
	help         = '<HELP MISSING>'
	description  = '<DESCRIPTION MISSING>'
	requires_dev = abstractproperty()

	def __init__(self):
		pass

	@abstractmethod
	def register_args(self, parser):
		raise NotImplementedError('Applets must implement this method')

	@abstractmethod
	def run(self, args, dev = None):
		raise NotImplementedError('Applets must implement this method')
