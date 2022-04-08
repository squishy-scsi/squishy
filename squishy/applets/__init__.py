# SPDX-License-Identifier: BSD-3-Clause

from abc import ABCMeta, abstractmethod

__all__ = (
	'SquishyApplet',
)

class SquishyApplet(metaclass = ABCMeta):
	preview      = False
	help         = '<HELP MISSING>'
	description  = '<DESCRIPTION MISSING>'
	required_rev = 'rev1'

	@abstractmethod
	def init_gui(self, main_window, args):
		pass

	@abstractmethod
	def init_repl(self, repl_ctx, args):
		pass

	@abstractmethod
	def init_applet(self, args):
		raise NotImplementedError('Applets must implement this method')


	@abstractmethod
	def build(self, target):
		raise NotImplementedError('Applets must implement this method')

	@abstractmethod
	def run(self, device, args):
		raise NotImplementedError('Applets must implement this method')

