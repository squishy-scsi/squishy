# SPDX-License-Identifier: BSD-3-Clause

import logging           as log
from pathlib             import Path
from typing              import Tuple, Optional
from argparse            import ArgumentParser, Namespace

from torii.build.run     import LocalBuildProducts

from rich.progress       import (
	Progress, SpinnerColumn, BarColumn,
	TextColumn
)

from ..config            import SQUISHY_BUILD_DIR
from ..core.device       import SquishyHardwareDevice
from ..core.flash        import FlashGeometry


from ..gateware.platform import AVAILABLE_PLATFORMS
from .                   import SquishyAction


class Provision(SquishyAction):
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
		build_dir: str, name: str, boot_products:  Tuple[str, LocalBuildProducts],
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

		build_options  = parser.add_argument_group('Build Options')
		pnr_options    = parser.add_argument_group('Gateware Place and Route Options')
		synth_options  = parser.add_argument_group('Gateware Synth Options')
		provision_opts = parser.add_argument_group('Provisioning Options')

		parser.add_argument(
			'--platform', '-p',
			dest    = 'hardware_platform',
			type    = str,
			default = list(AVAILABLE_PLATFORMS.keys())[-1],
			choices = list(AVAILABLE_PLATFORMS.keys()),
			help    = 'The target hardware platform',
		)

		# Build Options
		build_options.add_argument(
			'--build-only',
			action = 'store_true',
			help   = 'Only build the applet, and skip device programming'
		)

		build_options.add_argument(
			'--emit-debug-verilog',
			action = 'store_true',
			help   = 'Generate debug verilog for the bootloader'
		)

		build_options.add_argument(
			'--build-dir', '-b',
			type    = str,
			default = SQUISHY_BUILD_DIR,
			help    = 'The output directory for Squishy binaries and images'
		)

		build_options.add_argument(
			'--loud',
			action = 'store_true',
			help   = 'Enables the output of the Synth and PnR to the console'
		)

		# PnR Options
		pnr_options.add_argument(
			'--use-router2',
			action = 'store_true',
			help   = 'Use nextpnr\'s \'router2\' router rather than \'router1\''
		)

		pnr_options.add_argument(
			'--tmg-ripup',
			action  = 'store_true',
			help    = 'Use the timing-driven ripup router'
		)

		pnr_options.add_argument(
			'--detailed-timing-report',
			action = 'store_true',
			help   = 'Have nextpnr output a detailed net timing report'
		)

		pnr_options.add_argument(
			'--routed-svg',
			type    = Path,
			default = None,
			help    = 'Write a render of the routing to an SVG'
		)

		pnr_options.add_argument(
			'--routed-json',
			type    = Path,
			default = None,
			help   = 'Write the PnR output json for viewing in nextpnr after PnR'
		)

		pnr_options.add_argument(
			'--pnr-seed',
			type    = int,
			default = 0,
			help    = 'Specify the PnR seed to use'
		)

		# Synth Options
		synth_options.add_argument(
			'--no-abc9',
			action  = 'store_true',
			default = False,
			help    = 'Disable use of Yosys\' ABC9'
		)

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

	def run(self, args: Namespace, dev: Optional[SquishyHardwareDevice] = None) -> int:
		if not args.build_only and not args.whole_device and dev is None:
			dev = SquishyHardwareDevice.get_device(serial = args.device)
			if dev is None:
				log.error('No device selected, unable to continue.')
				return 1

		build_dir = Path(args.build_dir)
		log.info(f'Targeting platform \'{args.hardware_platform}\'')

		if not build_dir.exists():
			log.debug(f'Making build directory {args.build_dir}')
			build_dir.mkdir()
		else:
			log.debug(f'Using build directory {args.build_dir}')


		device = AVAILABLE_PLATFORMS[args.hardware_platform]()

		if device.bootloader_module is None:
			log.error('Unable to provision for platform, no bootloader module!')
			return 1

		pnr_opts = []
		synth_opts = []

		# PNR Opts
		if args.use_router2:
			pnr_opts.append('--router router2')
		else:
			pnr_opts.append('--router router1')

		if args.tmg_ripup:
			pnr_opts.append('--tmg-ripup')

		if args.detailed_timing_report:
			pnr_opts.append('--report timing.json')
			pnr_opts.append('--detailed-timing-report')

		if args.routed_svg is not None:
			svg_path = args.routed_svg.resolve()
			log.info(f'Writing PnR output svg to {svg_path}')
			pnr_opts.append(f'--routed-svg {svg_path}')

		if args.routed_json is not None:
			json_path = args.routed_json.resolve()
			log.info(f'Writing PnR output json to {json_path}')
			pnr_opts.append(f'--write {json_path}')

		if args.pnr_seed is not None:
			pnr_opts.append(f'--seed {args.pnr_seed}')

		# Synth Opts
		if not args.no_abc9:
			synth_opts.append('-abc9')

		# Provisioning Options
		if args.serial_number is not None:
			serial_number = args.serial_number
		else:
			serial_number = SquishyHardwareDevice.make_serial()

		log.info(f'Assigning device serial number \'{serial_number}\'')
		bootloader = device.bootloader_module(serial_number = serial_number)

		with Progress(
			SpinnerColumn(),
			TextColumn('[progress.description]{task.description}'),
			BarColumn(bar_width = None),
			transient = True
		) as progress:

			log.info('Building bootloader gateware')
			name, prod = device.build(
				bootloader,
				name          = 'squishy_bootloader',
				build_dir     = args.build_dir,
				do_build      = True,
				do_program    = False,
				synth_opts    = synth_opts,
				verbose       = args.loud,
				nextpnr_opts  = pnr_opts,
				skip_cache    = True,
				progress      = progress,
				debug_verilog = args.emit_debug_verilog
			)

			if args.whole_device:
				log.info('Building whole-device bitstream')
				path = self._build_multiboot(args.build_dir, 'squishy-unified.bin', (name, prod), device.flash['geometry'])
				if args.build_only:
					log.info(f'Please flash the file at \'{path}\' on to the hardware to provision the device.')
			else:
				if args.build_only:
					log.info(f'Use \'dfu-util\' to flash \'{name}\' into slot 0 to update the bootloader')
				else:
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
