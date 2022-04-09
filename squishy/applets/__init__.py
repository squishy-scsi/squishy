# SPDX-License-Identifier: BSD-3-Clause

from abc import ABCMeta, abstractmethod, abstractproperty

__all__ = (
	'SquishyApplet',
)

class SquishyApplet(metaclass = ABCMeta):
	preview      = abstractproperty()
	pretty_name  = abstractproperty()
	short_help   = abstractproperty()
	help         = '<HELP MISSING>'
	description  = '<DESCRIPTION MISSING>'
	hardware_rev = abstractproperty()

	def __init__(self):
		if not (
			isinstance(self.hardware_rev, str) or
			(
				isinstance(self.hardware_rev, tuple) and
				all(isinstance(r, str) for r in self.hardware_rev)
			)
		):
			raise ValueError(f'Applet `hardware_rev` must be a str or tuple of str not `{type(self.hardware_rev)!r}`')


	def supported_platform(self, platform):
		if isinstance(self.hardware_rev, str):
			return platform == self.hardware_rev
		else:
			return platform in self.hardware_rev

	def show_help(self):
		pass

	def init_gui(self, main_window, args):
		pass

	def init_repl(self, repl_ctx, args):
		pass

	@abstractmethod
	def init_applet(self, args):
		raise NotImplementedError('Applets must implement this method')

	@abstractmethod
	def register_args(self, parser):
		raise NotImplementedError('Applets must implement this method')

	def build(self, target):
		pass

	@abstractmethod
	def run(self, device, args):
		raise NotImplementedError('Applets must implement this method')
