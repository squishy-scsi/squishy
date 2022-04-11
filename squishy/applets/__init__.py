# SPDX-License-Identifier: BSD-3-Clause

from abc import ABCMeta, abstractmethod, abstractproperty

__all__ = (
	'SquishyApplet',
)

class SquishyApplet(metaclass = ABCMeta):
	'''Squishy applet base class

	This is the abstract base class that is used
	to implement any possible applet for squisy.

	It represents a combination of client-side python,
	and gateware that will run the the hardware platform.


	Users can then invoke the build and execution of implemented
	applets by name.

	Attributes
	----------

	preview : bool
		If the applet is a preview/pre-release applet.

	pretty_name : str
		A pretty string name of the applet.

	short_help : str
		A short section of help for the applet.

	help : str
		A longer more detailed help string.

	description : str
		A brief description about the applet.

	hardware_rev : str, tuple
		A single string, or a tuple of strings for supported hardware revisions

	supports_gui : bool
		Indicates if the applet has a GUI mode.

	supports_repl : bool
		Indicates if the applet has a REPL mode.
	'''

	preview       = abstractproperty()
	pretty_name   = abstractproperty()
	short_help    = abstractproperty()
	help          = '<HELP MISSING>'
	description   = '<DESCRIPTION MISSING>'
	hardware_rev  = abstractproperty()
	supports_gui  = abstractproperty()
	supports_repl = abstractproperty()

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
		''' Check to see if the given platform is supported

		Parameters
		----------
		platform : str
			The platform to check

		Returns
		-------
		bool
			True if the applet supports the platform, otherwise False.

		'''

		if isinstance(self.hardware_rev, str):
			return platform == self.hardware_rev
		else:
			return platform in self.hardware_rev

	def show_help(self):
		'''Shows applets built-in help'''
		pass

	def init_gui(self, main_window, args):
		'''Initializes applet GUI component'''
		pass

	def init_repl(self, repl_ctx, args):
		'''Initializes applet REPL component'''

		pass

	@abstractmethod
	def init_applet(self, args):
		'''Applet Initialization

		Called to initialize the applet prior to
		the applet being built and ran

		Parameters
		----------
		args
			Any command line arguments passed.

		Returns
		-------
		bool
			True if the was initialized, otherwise False.

		Raises
		------
		NotImplementedError
			The abstract method must be implemented by the applet
		'''

		raise NotImplementedError('Applets must implement this method')

	@abstractmethod
	def register_args(self, parser):
		'''Applet argument registration

		Called to register any applet specific arguments.

		Parameters
		----------
		parser
			The root argparse parser.

		Raises
		------
		NotImplementedError
			The abstract method must be implemented by the applet
		'''

		raise NotImplementedError('Applets must implement this method')

	@abstractmethod
	def build(self, target, args):
		'''Applet build step

		Called to build the gateware for the applet.

		Parameters
		----------
		target
			TBD

		args
			Any command line arguments passed.

		Raises
		------
		NotImplementedError
			The abstract method must be implemented by the applet
		'''

		raise NotImplementedError('Applets must implement this method')

	@abstractmethod
	def run(self, device, args):
		'''Applet run step

		Called to run any specialized machinery for the applet.

		Parameters
		----------
		device
			TBD

		args
			Any command line arguments passed.

		Raises
		------
		NotImplementedError
			The abstract method must be implemented by the applet
		'''

		raise NotImplementedError('Applets must implement this method')
