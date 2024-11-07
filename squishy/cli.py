# SPDX-License-Identifier: BSD-3-Clause
import logging          as log
from argparse           import ArgumentParser, ArgumentDefaultsHelpFormatter

from rich               import traceback
from rich.logging       import RichHandler

from .paths             import initialize_dirs

from .actions           import SquishyAction
from .actions.applet    import AppletAction
from .actions.provision import ProvisionAction

from .device            import SquishyDevice

from .                  import __version__

__all__ = (
	'main',
)

AVAILABLE_ACTIONS = (
	(AppletAction.name,    AppletAction()),
	(ProvisionAction.name, ProvisionAction()),
)

def setup_logging(verbose: bool = False) -> None:
	'''
	Initialize logging subscriber

	Set up the built-in rich based logging subscriber, and force it
	to be the one at runtime in case there is already one set up.

	Parameters
	----------
	verbose : bool
		If set, debug logging will be enabled

	'''

	if verbose:
		level = log.DEBUG
	else:
		level = log.INFO

	log.basicConfig(
		force    = True,
		format   = '%(message)s',
		datefmt  = '[%X]',
		level    = level,
		handlers = [
			RichHandler(rich_tracebacks = True, show_path = False)
		]
	)

def main() -> int:
	'''
	Squishy CLI Entrypoint.

	Returns
	-------
	int
		0 if execution was successful, otherwise any other integer on error

	'''

	traceback.install()

	initialize_dirs()
	setup_logging()

	parser = ArgumentParser(
		formatter_class = ArgumentDefaultsHelpFormatter,
		description     = 'Squishy SCSI Multitool',
		prog            = 'squishy'
	)

	parser.add_argument(
		'--device', '-d',
		type = str,
		help = 'The serial number of the squishy to use if more than one is attached'
	)

	parser.add_argument(
		'--verbose', '-v',
		action = 'store_true',
		help   = 'Enable verbose output during synth and pnr'
	)

	parser.add_argument(
		'--version', '-V',
		action  = 'version',
		version = f'Squishy v{__version__}',
		help    = 'Print Squishy version and exit'
	)

	action_parser = parser.add_subparsers(
		dest = 'action',
		required = True
	)

	# Enumerate available actions and register their arguments
	if len(AVAILABLE_ACTIONS) > 0:
		for (name, action) in AVAILABLE_ACTIONS:
			p = action_parser.add_parser(name, help = action.description)
			action.register_args(p)

	# Actually parse the arguments
	args = parser.parse_args()

	# Set-up logging *again* but if we want verbose output this time
	setup_logging(args.verbose)

	try:
		# Get the specified action, and invoke it with the appropriate arguments
		act: tuple[str, SquishyAction] = next(filter(lambda a: a[0] == args.action, AVAILABLE_ACTIONS), None)
		# Stupidly needed because we can't type an unpacked tuple
		(name, instance) = act

		dev: SquishyDevice | None = None

		# Pull in the option, we don't care if it's set right now.
		serial: str | None = args.device

		# This is now the specified device, or the first device, or no device
		dev = SquishyDevice.get_device(serial = serial)

		# This action requires a device, so we need ensure we have gotten one
		if instance.requires_dev:
			if dev is None:
				log.error('Selected action requires an attached device, but none found, aborting')
				return 1

			log.info(f'Selecting device: {dev}')

		ret = instance.run(args, dev)

		return ret
	except KeyboardInterrupt:
		log.info('bye!')
		return 0
