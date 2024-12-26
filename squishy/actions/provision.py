# SPDX-License-Identifier: BSD-3-Clause

'''

'''

import logging     as log
from argparse      import ArgumentParser, Namespace
from pathlib       import Path

from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn

from .             import SquishySynthAction
from ..paths       import SQUISHY_BUILD_BOOT
from ..device      import SquishyDevice
from ..gateware    import SquishyBootloader

__all__ = (
	'ProvisionAction',
)

class ProvisionAction(SquishySynthAction):
	'''
	Provision Squishy Hardware.

	This action is for provisioning actions, such as building full-device flash images, or
	just the bootloader.

	'''

	name         = 'provision'
	description  = 'Provision Squishy hardware'
	requires_dev = False # We need one to provision a live device, but not to build the image

	def register_args(self, parser: ArgumentParser) -> None:
		self.register_synth_args(parser)

		prov_opts = parser.add_argument_group('Provisioning Options')

		prov_opts.add_argument(
			'--serial-number', '-S',
			type    = str,
			default = None,
			help    = 'Directly specify the device serial number rather than automatically generating it'
		)

		prov_opts.add_argument(
			'--whole-device', '-W',
			action = 'store_true',
			help   = 'Generate a whole-device flash image, not just the bootloader.'
		)

	def run(self, args: Namespace, dev: SquishyDevice | None) -> int:
		# Get the platform
		platform_type = self.get_platform(args, dev)
		if platform_type is None:
			# the call to `get_platform` will have already printed an error message
			return 1

		# Initialize the platform
		plat = platform_type()

		# If we were passed a serial number, then use that
		if args.serial_number is not None:
			serial: str = args.serial_number
		# Otherwise, if we have an attached device, use it's existing serial
		elif dev is not None:
			serial = dev.serial
		# Otherwise otherwise, generate a brand new one
		else:
			serial = SquishyDevice.generate_serial()

		log.info(f'Assigning device serial number \'{serial}\'')

		build_dir = SQUISHY_BUILD_BOOT
		if args.build_dir is not None:
			build_dir = Path(args.build_dir)

		# TODO(aki): Booloader opts etc
		bootloader = SquishyBootloader(
			serial_number = serial, revision = plat.revision
		)

		boot_name = f'squishy_boot_v{plat.revision_str}'

		log.info('Building bootloader gateware')
		prod = self.run_synth(args, plat, bootloader, boot_name, build_dir)

		if prod is None:
			# Synth failed, the call to `run_synth` will have already printed the reason.
			return 1

		if args.whole_device:
			log.info('Building full device flash image')
			image_name = f'squishy-{plat.revision_str}-monolithic.bin'
			image = plat.build_image(image_name, build_dir, boot_name, prod, args = args)

			if args.build_only:
				log.info(f'Provisioning image generated at \'{image}\', Flash to device to provision')
			else:
				# TODO(aki): Eventually when we have the ability to automatically provision the flash
				#            This would be done by either making use of something like an attached
				#            blackmagic probe in SPI, or the "brainslug" passthru of a supervisor.
				#
				#            This kinda depends a lot on the hardware platform so that might need to be
				#            abstracted out to them, as only the platform really knows how to best provision
				#            itself.
				log.warning('Unable to automatically provision device at this time')
				log.warning(f'Provisioning image generated at \'{image}\', Flash to device to provision')
			return 0

		else:
			f_name = f'{boot_name}.{plat.bitstream_suffix}'
			p_name = f'{f_name}.pak'
			image = plat.pack_artifact(prod.get(f_name), args = args)

			if args.build_only:
				with (build_dir / p_name).open('wb') as f:
					f.write(image)

				log.info(self.dfu_util_msg(p_name, 0, build_dir, dev))
				return 0


		if dev is None:
			log.error('No device specified, however we were asked to program the device, aborting')
			return 1

		with Progress(
			SpinnerColumn(),
			TextColumn('[progress.description]{task.description}'),
			BarColumn(bar_width = None),
			transient = True
		) as progress:
			if args.whole_image:
				log.warning('TODO: Whole image flash stuff')
			else:
				log.info('Programming bootloader')
				if dev.upload(image, 0, progress):
					log.info('Resetting device')
					dev.reset()
				else:
					log.error('Device upload failed')
					return 1
		return 0
