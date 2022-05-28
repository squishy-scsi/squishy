# SPDX-License-Identifier: BSD-3-Clause

from abc import ABCMeta, abstractmethod, abstractproperty

__all__ = (
	'SquishyAction',
)

class SquishyAction(metaclass = ABCMeta):
	'''Squishy action base class

	This is the abstract base class that is used
	to implement any possible action for the squishy
	command line interface.

	Attributes
	----------
	pretty_name : str
		The pretty name of the action to show.

	short_help : str
		A short help string for the action.

	help : str
		A more comprehensive help string for the action.

	description : str
		The description of the action.

	requires_dev : bool
		If this action requires a Squishy to be attached to the machine.

	'''

	pretty_name  = abstractproperty()
	short_help   = abstractproperty()
	help         = '<HELP MISSING>'
	description  = '<DESCRIPTION MISSING>'
	requires_dev = abstractproperty()

	def __init__(self):
		pass

	@abstractmethod
	def register_args(self, parser):
		'''Register action arguments.

		When an action instance is initialized this method is
		called so when :py:func:`run` is called any needed
		arguments can be passed to the action.

		Parameters
		----------
		parser : argparse.ArgumentParser
			The argument parser to register commands with.

		Raises
		------
		NotImplementedError
			The abstract method must be implemented by the action.

		'''

		raise NotImplementedError('Actions must implement this method')

	@abstractmethod
	def run(self, args, dev = None):
		'''Run the action.

		Run the action instance, passing the parsed
		arguments and the selected device if any.

		Parameters
		----------
		args : argsparse.Namespace
			Any command line arguments passed.

		dev : squishy.core.device.SquishyHardwareDevice, None
			The device this action was invoked on if any.

		Returns
		-------
		int
			0 if run was successful, otherwise an error code.

		Raises
		------
		NotImplementedError
			The abstract method must be implemented by the action.


		'''

		raise NotImplementedError('Acctions must implement this method')
