# SPDX-License-Identifier: BSD-3-Clause

'''

'''

from abc           import ABCMeta, abstractmethod
from argparse      import ArgumentParser, Namespace

from ..device      import SquishyDevice
from ..gateware    import SquishyPlatformType, AppletElaboratable

__all__ = (
	'SquishyApplet',
)

class SquishyApplet(metaclass = ABCMeta):
	'''
	Base class for all Squishy applets.

	This class provides the public facing API for all Squishy applets, both internal
	and out-of-tree/third-party applet modules.

	Squishy applets are made out of a combination of host-site Python logic and hardware-side
	gateware.

	Attributes
	----------
	name : str
		The name used to address this applet and display in the help documentation.

	description : str
		A short description of this applet.

	preview : bool
		If this applet is preview/pre-release.

	version : float
		The version of the applet.

	supported_platforms : tuple[tuple[int, int], ...]
		The platform revisions this applet supports.

	pnr_seed : int | None
		If the applet needs a given PNR seed to synth, it can be supplied here.
		By default this is `None`, which uses the default PNR seed for Squishy,
		but when set will override that.

		However, the `--pnr-seed` CLI option will usurp this option if passed.

	'''

	@property
	@abstractmethod
	def name(self) -> str:
		''' The name of the applet. '''
		raise NotImplementedError('Applets must implement this property')

	@property
	@abstractmethod
	def description(self) -> str:
		''' Short description of the applet. '''
		raise NotImplementedError('Applets must implement this property')

	@property
	@abstractmethod
	def preview(self) -> bool:
		''' If this applet is a preview or not '''
		raise NotImplementedError('Applets must implement this property')

	@property
	@abstractmethod
	def version(self) -> float:
		''' Applet version '''
		raise NotImplementedError('Applets must implement this property')

	@property
	@abstractmethod
	def supported_platforms(self) -> tuple[tuple[int, int], ...]:
		''' The platforms this applet supports. '''
		raise NotImplementedError('Applets must implement this property')

	@property
	def pnr_seed(self) -> int | None:
		''' The requested PNR seed for this applet if needed '''

		return None

	def __init__(self) -> None:
		pass

	def is_supported(self, platform: SquishyPlatformType) -> bool:
		'''
		Check to see if the given platform is supported.

		Parameters
		----------
		platform : squishy.gateware.SquishyPlatformType
			The platform to check against.

		Returns
		-------
		bool
			True if the given platform is supported by this applet, otherwise False.
		'''

		return platform.revision in self.supported_platforms

	@abstractmethod
	def register_args(self, parser: ArgumentParser) -> None:
		'''
		Register applet argument parsers.

		Prior to :py:func:`.initialize` and :py:func:`.run` this method will
		be called to allow the applet to register any wanted command line options.

		This is also used when displaying help.

		Parameters
		----------
		parser : argparse.ArgumentParser
			The Squishy CLI argument parser group to register arguments into.

		Raises
		------
		NotImplementedError
			The abstract method must be implemented by the applet.

		'''
		raise NotImplementedError('Actions must implement this method')

	@abstractmethod
	def initialize(self, args: Namespace) -> AppletElaboratable | None:
		'''
		Initialize applet.

		This is called prior to the gateware side of the applet being elaborated. It ensures
		that any initialization and configuration needed to be done can be done.

		Parameters
		----------
		args : argsparse.Namespace
			The parsed arguments from the Squishy CLI

		Returns
		-------
		AppletElaboratable | None
			An AppletElaboratable if initialization was successful otherwise None

		Raises
		------
		NotImplementedError
			The abstract method must be implemented by the applet.
		'''
		raise NotImplementedError('Applets must implement this method')


	@abstractmethod
	def run(self, args: Namespace, dev: SquishyDevice) -> int:
		'''
		Invoke the applet.

		This method is run when the Squishy CLI has determined that this applet
		was to be ran.

		This is for host-side applet logic only, such as USB communication, if the
		applet does not have any host-side logic, this may simple just return ``0``
		as if it ran successfully.

		Parameters
		----------
		args : argsparse.Namespace
			The parsed arguments from the Squishy CLI

		dev : squishy.device.SquishyDevice
			The target device

		Returns
		-------
		int
			0 if run was successful, otherwise an error code.

		Raises
		------
		NotImplementedError
			The abstract method must be implemented by the applet.

		'''
		raise NotImplementedError('Actions must implement this method')
