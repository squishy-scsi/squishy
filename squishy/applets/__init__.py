# SPDX-License-Identifier: BSD-3-Clause

from abc           import ABCMeta, abstractmethod
from argparse      import ArgumentParser, Namespace


from ..gateware    import AppletElaboratable
from ..core.device import SquishyHardwareDevice

__all__ = (
	'SquishyApplet',
)

class SquishyApplet(metaclass = ABCMeta):
	'''
	Squishy applet base class.

	This is the abstract base class that is used
	to implement any possible applet for squishy.

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

	'''
	@property
	@abstractmethod
	def preview(self) -> bool:
		raise NotImplementedError('Applets must implement this property')

	@property
	@abstractmethod
	def pretty_name(self) -> str:
		raise NotImplementedError('Applets must implement this property')

	@property
	@abstractmethod
	def short_help(self) -> str:
		raise NotImplementedError('Applets must implement this property')

	@property
	def help(self) -> str:
		return '<HELP MISSING>'

	@property
	def description(self) -> str:
		return '<DESCRIPTION MISSING>'

	@property
	@abstractmethod
	def hardware_rev(self) -> str | tuple[str, ...]:
		raise NotImplementedError('Applets must implement this property')

	def __init__(self):
		if not (
			isinstance(self.hardware_rev, str) or
			(
				isinstance(self.hardware_rev, tuple) and
				all(isinstance(r, str) for r in self.hardware_rev)
			)
		):
			raise ValueError(f'Applet `hardware_rev` must be a str or tuple of str not `{type(self.hardware_rev)!r}`')


	def supported_platform(self, platform: str) -> bool:
		'''
		Check to see if the given platform is supported

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

	def show_help(self) -> None:
		''' Shows applets built-in help '''
		pass

	@abstractmethod
	def init_applet(self, args: Namespace) -> AppletElaboratable:
		'''
		Applet Initialization

		Called to initialize the applet prior to
		the applet being built and ran

		Parameters
		----------
		args : argsparse.Namespace
			Any command line arguments passed.

		Returns
		-------
		AppletElaboratable
			The applet logic/elaboratable

		Raises
		------
		NotImplementedError
			The abstract method must be implemented by the applet

		'''

		raise NotImplementedError('Applets must implement this method')

	@abstractmethod
	def register_args(self, parser: ArgumentParser) -> None:
		'''
		Applet argument registration

		Called to register any applet specific arguments.

		Parameters
		----------
		parser : argparse.ArgumentParser
			The root argparse parser.

		Raises
		------
		NotImplementedError
			The abstract method must be implemented by the applet

		'''

		raise NotImplementedError('Applets must implement this method')

	@abstractmethod
	def run(self, device: SquishyHardwareDevice, args: Namespace) -> int:
		'''
		Applet run step

		Called to run any specialized machinery for the applet.

		Parameters
		----------
		device : squishy.core.device.SquishyHardwareDevice
			The target squishy device.

		args : argsparse.Namespace
			Any command line arguments passed.

		Returns
		-------
		int
			0 if run was successful, otherwise an error code.

		Raises
		------
		NotImplementedError
			The abstract method must be implemented by the applet

		'''

		raise NotImplementedError('Applets must implement this method')
