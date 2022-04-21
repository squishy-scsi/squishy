# SPDX-License-Identifier: BSD-3-Clause
import logging as log
from pathlib              import Path

from ..applets           import SquishyApplet
from ..config            import SQUISHY_APPLETS, SQUISHY_BUILD_DIR
from ..core.collect           import collect_members, predicate_applet

from ..gateware          import Squishy
from ..gateware.platform import AVAILABLE_PLATFORMS
from .                   import SquishyAction


class Applet(SquishyAction):
	pretty_name  = 'Squishy Applets'
	short_help   = 'Squishy applet subsystem'
	description  = 'Build and run Squishy applets'
	requires_dev = True

	def _collect_all_applets(self):
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

	def register_args(self, parser):
		# actions = parser.add_subparsers(dest = 'gateware_action')

		# do_verify = actions.add_parser('verify', help = 'Run formal verification')
		# verify_options = do_verify.add_argument_group('Verification options')

		# do_simulation  = actions.add_parser('simulate', help = 'Run simulation test cases')
		# sim_options    = do_simulation.add_argument_group('Simulation Options')

		build_options  = parser.add_argument_group('Build Options')
		pnr_options    = parser.add_argument_group('Gateware Place and Route Options')
		synth_options  = parser.add_argument_group('Gateware Synth Options')

		usb_options    = parser.add_argument_group('USB Options')
		uart_options   = parser.add_argument_group('Debug UART Options')
		scsi_options   = parser.add_argument_group('SCSI Options')

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
			'--skip-cache',
			action = 'store_true',
			help   = 'Skip the cache lookup and subsequent caching of resultant bitstream'
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
			help   = 'Use nextpnr\'s \'router1\' router rather than \'router2\''
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
			type    = str,
			default = None,
			help    = 'Write a render of the routing to an SVG'
		)

		# Synth Options
		synth_options.add_argument(
			'--no-abc9',
			action = 'store_true',
			help   = 'Disable use of Yosys\' ABC9'
		)

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

	def run(self, args, dev = None):
		build_dir = Path(args.build_dir)
		log.info(f'Targeting platform \'{args.hardware_platform}\'')

		if not build_dir.exists():
			log.debug(f'Making build directory {args.build_dir}')
			build_dir.mkdir()
		else:
			log.debug(f'Using build directory {args.build_dir}')

		apl = list(filter(lambda a: a['name'] == args.applet, self.applets))[0]

		name   = apl['name']
		applet = apl['instance']

		if not applet.supported_platform(args.hardware_platform):
			log.error(f'Applet {name} does not support platform {args.hardware_platform}')
			log.error(f'Supported platform(s) {applet.hardware_rev}')
			return 1

		if applet.preview:
			log.warning(f'This applet is a preview, it may be buggy or not work at all')

		device = AVAILABLE_PLATFORMS[args.hardware_platform]()

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
			pnr_opts.append(f' --routed-svg {args.routed_svg}')

		# Synth Opts
		if not args.no_abc9:
			synth_opts.append('-abc9')

		applet.init_applet(args)

		uart_config = {
			'enabled'  : args.enable_uart,
			'baud'     : args.baud,
			'parity'   : args.parity,
			'data_bits': args.data_bits,
		}

		usb_config = {
			'webusb': {
				'enabled': args.enable_webusb,
				'url'    : args.webusb_url,
			}
		}

		scsi_config = {
			'did': args.scsi_did,
		}


		gateware = Squishy(
			uart_config = uart_config,
			usb_config  = usb_config,
			scsi_config = scsi_config,
		)



		device.build(
			gateware,
			name = 'squishy_applet',
			build_dir = args.build_dir,
			do_build = True,
			do_program = True,
			synth_opts = synth_opts,
			verbose = args.loud,
			nextpnr_opts = pnr_opts,
			skip_cache = args.skip_cache,
		)


		return applet.run(device, args)
