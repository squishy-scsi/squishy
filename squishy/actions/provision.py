# SPDX-License-Identifier: BSD-3-Clause

import logging           as log
from pathlib             import Path
from argparse            import ArgumentParser, Namespace

from torii.build.run     import LocalBuildProducts

from rich.progress       import (
	Progress, SpinnerColumn, BarColumn,
	TextColumn
)

from ..core.device       import SquishyHardwareDevice
from ..core.flash        import FlashGeometry

from .                   import SquishySynthAction


class Provision(SquishySynthAction):
	pretty_name  = 'Squishy Provision'
	short_help   = 'Squishy first-time provisioning'
	description  = 'Build squishy bootloader flash image'
	requires_dev = False

	def _build_slots(self, flash_geometry: FlashGeometry) -> bytes:
		'''  '''
		from ..gateware.bootloader.bitstream import iCE40BitstreamSlots

		slot_data = bytearray(flash_geometry.erase_size)
		slots     = iCE40BitstreamSlots(flash_geometry).build()

		slot_data[0:len(slots)] = slots

		for byte in range(len(slots), flash_geometry.erase_size):
			slot_data[byte] = 0xFF

		return bytes(slot_data)

	def _build_multiboot(self,
		build_dir: str, name: str, boot_products:  tuple[str, LocalBuildProducts],
		flash_geometry: FlashGeometry
	) -> Path:

		build_path = Path(build_dir) / name

		log.debug(f'Building multiboot bitstream in \'{build_path}\'')

		boot_name = boot_products[0]
		if not boot_name.endswith('.bin'):
			boot_name = boot_name + '.bin'

		log.debug(f'Bootloader bitstream name: \'{boot_name}\'')

		with build_path.open('wb') as multiboot:
			slot_data = self._build_slots(flash_geometry)

			log.debug('Writing slot data')
			multiboot.write(slot_data)
			log.debug('Writing bootloader bitstream')
			multiboot.write(boot_products[1].get(boot_name))

			start = multiboot.tell()
			end   = flash_geometry.partitions[1]['start_addr']

			log.debug('Padding bitstream')
			for _ in range(start, end):
				multiboot.write(b'\xFF')

			# Stuff in a copy of the bootloader entry
			log.debug('Copying bootloader entry to active slot')
			multiboot.write(slot_data[32:64])

		return build_path

	def __init__(self):
		super().__init__()


	def register_args(self, parser: ArgumentParser) -> None:
		self.register_synth_args(parser, cacheable = False)

		provision_opts = parser.add_argument_group('Provisioning Options')

		# Provisioning Options
		provision_opts.add_argument(
			'--serial-number', '-S',
			type    = str,
			default = None,
			help    = 'Specify the device serial number rather than automatically generating it'
		)

		provision_opts.add_argument(
			'--whole-device', '-W',
			action = 'store_true',
			default = False,
			help   = 'Program the whole device, not just the bootloader'
		)

	def run(self, args: Namespace, dev: SquishyHardwareDevice | None = None) -> int:
		plt = self.get_hw_platform(args, dev)
		if plt is None:
			return 1

		device, _, dev = plt

		if device.bootloader_module is None:
			log.error('Unable to provision for platform, no bootloader module!')
			return 1

		# Provisioning Options
		if args.serial_number is not None:
			serial_number = args.serial_number
		if dev is not None:
			serial_number = dev.serial
		else:
			serial_number = SquishyHardwareDevice.make_serial()

		log.info(f'Assigning device serial number \'{serial_number}\'')
		bootloader = device.bootloader_module(serial_number = serial_number)

		log.info('Building bootloader gateware')
		name, prod = self.run_synth(args, device, bootloader, 'squishy_bootloader', cacheable = False)

		if args.whole_device:
			log.info('Building whole-device bitstream')
			path = self._build_multiboot(args.build_dir, 'squishy-unified.bin', (name, prod), device.flash['geometry'])

			if args.build_only:
				log.info(f'Please flash the file at \'{path}\' on to the hardware to provision the device.')
				return 0

		if args.build_only:
			log.info(f'Use \'dfu-util\' to flash \'{args.build_dir / name}.bin\' into slot 0 to update the bootloader')
			log.info(f'e.g. \'dfu-util -d 1209:ca70,:ca71 -a 0 -R -D {args.build_dir / name}.bin\'')
			return 0

		with Progress(
			SpinnerColumn(),
			TextColumn('[progress.description]{task.description}'),
			BarColumn(bar_width = None),
			transient = True
		) as progress:
			file_name = name
			if not file_name.endswith('.bin'):
				file_name += '.bin'

			log.info(f'Programming bootloader with {file_name}')
			if dev.upload(prod.get(file_name), 0, progress):
				log.info('Resetting Device')
				dev.reset()
			else:
				log.error('Device upload failed!')
				return 1
		return 0
