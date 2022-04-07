# SPDX-License-Identifier: BSD-3-Clause
import logging

from ..gateware            import Squishy
from ..gateware.platform   import AVAILABLE_PLATFORMS
from ..gateware.simulation import *

ACTION_NAME = 'gateware'
ACTION_DESC = 'Core Squishy gateware actions'

log = logging.getLogger('squishy')

def parser_init(parser):
	actions = parser.add_subparsers(dest = 'gateware_action')

	do_verify = actions.add_parser('verify', help = 'Run formal verification')
	verify_options = do_verify.add_argument_group('Verification options')

	do_simulation  = actions.add_parser('simulate', help = 'Run simulation test cases')
	sim_options    = do_simulation.add_argument_group('Simulation Options')

	do_build       = actions.add_parser('build', help = 'Build the gateware')

	pnr_options    = do_build.add_argument_group('Gateware Place and Route Options')
	synth_options  = do_build.add_argument_group('Gateware Synth Options')

	usb_options    = parser.add_argument_group('USB Options')
	uart_options   = parser.add_argument_group('Debug UART Options')
	scsi_options   = parser.add_argument_group('SCSI Options')

	# USB Options

	# WebUSB options
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

	## Synth / Route Options
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

	synth_options.add_argument(
		'--no-abc9',
		action = 'store_true',
		help   = 'Disable use of Yosys\' ABC9'
	)


def action_main(args):

	plat = AVAILABLE_PLATFORMS[args.hardware_platform]()
	pnr_opts = []
	synth_opts = []

	if args.gateware_action == 'verify':
		log.info('Running verification pass')
		log.warning('todo')
	elif args.gateware_action == 'simulate':
		log.info('Running simulations')
		run_sims(args)
	elif args.gateware_action == 'build':
		log.info('Building generic gateware')
		gateware = Squishy(
			uart_config = {
				'enabled'  : args.enable_uart,
				'baud'     : args.baud,
				'parity'   : args.parity,
				'data_bits': args.data_bits,
			},

			usb_config = {
				'webusb': {
					'enabled': args.enable_webusb,
					'url'    : args.webusb_url,
				}
			},

			scsi_config = {
				'did': args.scsi_did,
			}
		)

		## PNR Opts
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

		## Synth Opts
		if not args.no_abc9:
			synth_opts.append('-abc9')

		plat.build(
			gateware,
			name = 'squishy',
			build_dir = args.build_dir,
			do_build = True,
			synth_opts = synth_opts,
			verbose = args.verbose,
			nextpnr_opts = pnr_opts
		)
	else:
		log.info('ニャー')
	return 0
