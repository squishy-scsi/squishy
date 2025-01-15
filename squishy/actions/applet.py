# SPDX-License-Identifier: BSD-3-Clause

'''

'''

import logging         as log
from pathlib           import Path
from argparse          import ArgumentParser, Namespace

from rich.prompt       import Confirm
from rich.progress     import Progress, SpinnerColumn, BarColumn, TextColumn

from .                 import SquishySynthAction
from ..applets         import SquishyApplet
from ..paths           import SQUISHY_APPLETS, SQUISHY_BUILD_APPLET
from ..device          import SquishyDevice
from ..core.reflection import collect_members, is_applet
from ..gateware        import Squishy as SquishyGateware

__all__ = (
	'AppletAction',
)


class AppletAction(SquishySynthAction):
	'''
	Build and Run Squishy Applets

	This action implements all the machinery needed to build and run :py:class:`SquishyApplet`'s, on
	both gateware-side and host-side, along with setting up a the optional communication channel
	between then if needed.

	Note
	----
	Not all applets will have a host-side invocation runtime, some might be gateware only and implement
	something such as a SCSI disk endpoint over USB and let th host OS drivers deal with it.

	'''

	name         = 'applet'
	description  = 'Build and run Squishy applets'
	# TODO(aki): We /technically/ want this, but it would be nice to be able to build them w/o a device attached
	requires_dev = False

	def _collect_applets(self, external:  bool = True) -> list[SquishyApplet]:
		'''
		Try to collect known applets.

		Parameters
		----------
		external : bool
			Also try to collect applets located in the ``SQUISHY_APPLETS`` directory where
			users can drop their own or third-party applets.

		Returns
		-------
		'''

		from .. import applets
		return [
			*collect_members(
				Path(applets.__path__[0]),
				is_applet,
				f'{applets.__name__}.',
				make_instance = True
			),
			# BUG(aki): This is likely entirely busted
			*(collect_members(
				SQUISHY_APPLETS,
				is_applet,
				make_instance = True,
			) if external else ())
		]

	def __init__(self) -> None:
		super().__init__()
		self._applets = self._collect_applets()

	def register_args(self, parser: ArgumentParser) -> None:
		self.register_synth_args(parser)

		parser.add_argument(
			'--noconfirm', '-Y',
			action = 'store_true',
			help   = 'Do not ask for confirmation if the target applet is in preview.'
		)

		parser.add_argument(
			'--flash', '-f',
			action = 'store_true',
			help   = 'Flash the gateware into persistent flash rather than doing an ephemeral load'
		)

		# TODO(aki): Peripheral options and the like

		applet_parser = parser.add_subparsers(
			dest     = 'applet',
			required = True
		)

		for applet in self._applets:
			p = applet_parser.add_parser(applet.name, help = applet.description)
			applet.register_args(p)

	def run(self, args: Namespace, dev: SquishyDevice) -> int:
		# Get the platform
		platform_type = self.get_platform(args, dev)
		if platform_type is None:
			# the call to `get_platform` will have already printed an error message
			return 1

		# Initialize the platform
		plat = platform_type()

		# Pull out the selected applet
		applet: SquishyApplet = next(filter(lambda applet: applet.name == args.applet, self._applets), None)

		# Check to make sure we support this platform
		if not applet.is_supported(plat):
			log.error(f'Applet \'{applet.name}\' does not support revision {plat.revision_str} hardware')
			return 1

		# Warn the user if this applet is unstable
		if applet.preview:
			log.warning(f'The {applet.name} applet is a preview, it may be buggy or not work at all')
			if not args.noconfirm:
				if not Confirm.ask('Are you sure you would like to use this applet?'):
					return 0

		# Setup our requested build dir
		build_dir = SQUISHY_BUILD_APPLET
		if args.build_dir is not None:
			build_dir = Path(args.build_dir)

		# Try to initialize the applet gateware
		applet_elab = applet.initialize(args)
		if applet_elab is None:
			log.error('Failure initializing applet elaboratable, aborting')
			return 1

		# TODO(aki): Construct gateware superstructure peripherals and the like

		# Get the target slot, ephemeral or otherwise
		slot: int | None = plat.ephemeral_slot
		if slot is None or args.flash:
			slot = 1


		# Construct the gateware
		gateware = SquishyGateware(
			revision = plat.revision,
			applet   = applet_elab
		)

		# TODO(aki): This should be made unique to the applet being made?
		applet_name = f'squishy_applet_{applet.name}_v{plat.revision_str}'

		# Actually build the gateware
		log.info('Building applet gateware')
		prod = self.run_synth(args, plat, gateware, applet_name, build_dir, pnr_seed = applet.pnr_seed)

		if prod is None:
			# Synth failed, the call to `run_synth` will have already printed the reason.
			return 1

		f_name = f'{applet_name}.{plat.bitstream_suffix}'
		p_name = f'{f_name}.pak'

		# TODO(aki): We don't cache the packed artifact, we re-pack it each time
		#            should we cache it?
		# Pack the bitstream artifact in a way the platform wants
		packed = plat.pack_artifact(prod.get(f_name, 'b'), args = args)

		# if on the off chance the user only built the gateware, display how to use dfu-util to flash it
		if args.build_only:
			with (build_dir / p_name).open('wb') as f:
				f.write(packed)

			log.info(self.dfu_util_msg(p_name, slot, build_dir, dev))
			return 0


		# If we *are* programming the device, then
		with Progress(
			SpinnerColumn(),
			TextColumn('[progress.description]{task.description}'),
			BarColumn(bar_width = None),
			transient = True
		) as progress:

			# Make sure there is actually a device attached
			if dev is None:
				log.error('No device specified, however we were asked to program the device, aborting')
				return 1

			log.info(f'Programming device with \'{f_name}\'')
			if dev.upload(packed, slot, progress):
				log.info('Resetting device')
				dev.reset()
			else:
				log.error('Device upload failed')
				return 1

		log.info('Running applet...')
		return applet.run(args, dev)
