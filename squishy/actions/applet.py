# SPDX-License-Identifier: BSD-3-Clause
import logging            as log
from pathlib              import Path
from argparse             import ArgumentParser, Namespace

from rich.progress        import (
	Progress, SpinnerColumn, BarColumn,
	TextColumn
)

from ..applets           import SquishyApplet
from ..config            import SQUISHY_APPLETS
from ..core.collect      import collect_members, predicate_applet
from ..core.device       import SquishyHardwareDevice

from ..gateware          import Squishy
from .                   import SquishySynthAction


class Applet(SquishySynthAction):
	pretty_name  = 'Squishy Applets'
	short_help   = 'Squishy applet subsystem'
	description  = 'Build and run Squishy applets'
	requires_dev = True

	def _collect_all_applets(self) -> list[dict[str, str | SquishyApplet]]:
		from .. import applets
		return [
			*collect_members(
				Path(applets.__path__[0]),
				predicate_applet,
				f'{applets.__name__}.'
			),
			*collect_members(
				SQUISHY_APPLETS,
				predicate_applet,
				''
			)
		]

	def __init__(self):
		super().__init__()
		self.applets = self._collect_all_applets()

	def register_args(self, parser: ArgumentParser) -> None:
		# actions = parser.add_subparsers(dest = 'gateware_action')

		# do_verify = actions.add_parser('verify', help = 'Run formal verification')
		# verify_options = do_verify.add_argument_group('Verification options')

		# do_simulation  = actions.add_parser('simulate', help = 'Run simulation test cases')
		# sim_options    = do_simulation.add_argument_group('Simulation Options')

		self.register_synth_args(parser, cacheable = True)

		usb_options    = parser.add_argument_group('USB Options')
		uart_options   = parser.add_argument_group('Debug UART Options')
		scsi_options   = parser.add_argument_group('SCSI Options')


		# USB Options
		usb_options.add_argument(
			'--enable-webusb',
			action = 'store_true',
			help   = 'Enable the experimental WebUSB descriptors'
		)

		usb_options.add_argument(
			'--webusb-url',
			type    = str,
			default = 'https://localhost',
			help    = 'The location URL to encode in the device descriptor'
		)

		# SCSI Options
		scsi_options.add_argument(
			'--scsi-did',
			type    = int,
			default = 0x01,
			help    = 'The SCSI Device ID to use'
		)

		scsi_options.add_argument(
			'--scsi-arbitrating',
			default = False,
			action  = 'store_true',
			help    = 'Enable SCSI Bus arbitration'
		)

		scsi_options.add_argument(
			'--scsi-device',
			default = False,
			action  = 'store_true',
			help    = 'Set the SCSI bus to be a device rather than an initiator',
		)

		# UART Options
		uart_options.add_argument(
			'--enable-uart', '-U',
			default = False,
			action  = 'store_true',
			help    = 'Enable the debug UART',
		)

		uart_options.add_argument(
			'--baud', '-B',
			type    = int,
			default = 9600,
			help    = 'The rate at which to run the debug UART'
		)

		uart_options.add_argument(
			'--data-bits', '-D',
			type    = int,
			default = 8,
			help    = 'The data bits to use for the UART'
		)

		uart_options.add_argument(
			'--parity', '-c',
			type    = str,
			choices = [
				'none', 'mark', 'space'
				'even', 'odd'
			],
			default = 'none',
			help    = 'The parity mode for the debug UART'
		)

		applet_parser = parser.add_subparsers(
			dest     = 'applet',
			required = True
		)

		if len(self.applets) > 0:
			for apl in self.applets:
				applet = apl['instance']
				p = applet_parser.add_parser(
						apl['name'],
						help = applet.short_help,
					)
				applet.register_args(p)

	def run(self, args: Namespace, dev: SquishyHardwareDevice | None = None) -> int:
		plt = self.get_hw_platform(args, dev)
		if plt is None:
			return 1

		platform, hardware_platform, dev = plt

		apl = list(filter(lambda a: a['name'] == args.applet, self.applets))[0]

		name: str             = apl['name']
		applet: SquishyApplet = apl['instance']

		if not applet.supported_platform(hardware_platform):
			log.error(f'Applet {name} does not support platform {hardware_platform}')
			log.error(f'Supported platform(s) {applet.hardware_rev}')
			return 1

		if applet.preview:
			log.warning('This applet is a preview, it may be buggy or not work at all')


		applet_elaboratable = applet.init_applet(args)

		uart_config = {
			'enabled'  : args.enable_uart,
			'baud'     : args.baud,
			'parity'   : args.parity,
			'data_bits': args.data_bits,
		}

		usb_config = {
			'vid': platform.usb_vid,
			'pid': platform.usb_pid_app,
			'manufacturer': platform.usb_mfr,
			'serial_number': SquishyHardwareDevice.make_serial() if dev is None else dev.serial,
			'product': platform.usb_prod[platform.usb_pid_app],
			'webusb': {
				'enabled': args.enable_webusb,
				'url'    : args.webusb_url,
			}
		}

		scsi_config = {
			'version'    : applet_elaboratable.scsi_version,
			'vid'        : platform.scsi_vid,
			'did'        : args.scsi_did,
			'arbitrating': args.scsi_arbitrating,
			'is_device'  : args.scsi_device,
		}


		gateware = Squishy(
			revision    = platform.revision,
			uart_config = uart_config,
			usb_config  = usb_config,
			scsi_config = scsi_config,
			applet      = applet_elaboratable
		)

		log.info('Building applet gateware')
		name, prod = self.run_synth(args, platform, gateware, 'squishy_applet', cacheable = True)

		if args.build_only:
			log.info(f'Use \'dfu-util\' to flash \'{args.build_dir / name}.bin\' into slot 1 to update the applet')
			log.info(f'e.g. \'dfu-util -d 1209:ca70,:ca71 -a 1 -R -D {args.build_dir / name}.bin\'')
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

			log.info(f'Programming applet with {file_name}')
			if dev.upload(prod.get(file_name), 1, progress):
				log.info('Resetting Device')
				dev.reset()
			else:
				log.error('Device upload failed!')
				return 1

		log.info('Running applet...')
		return applet.run(dev, args)
