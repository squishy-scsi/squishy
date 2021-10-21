# SPDX-License-Identifier: BSD-3-Clause
from ..utility             import *
from ..gateware.platform   import AVAILABLE_PLATFORMS
from ..gateware.core       import Squishy
from ..gateware.simulation import *

ACTION_NAME = 'gateware'
ACTION_DESC = 'Core Squishy gateware actions'

def parser_init(parser):
	actions = parser.add_subparsers(dest = 'gateware_action')

	do_verify = actions.add_parser('verify', help = 'Run formal verification')
	verify_options = do_verify.add_argument_group('Verification options')

	do_simulation  = actions.add_parser('simulate', help = 'Run simulation test cases')
	sim_options    = do_simulation.add_argument_group('Simulation Options')

	do_build       = actions.add_parser('build', help = 'Build the gateware')

	# usb_options    = parser.add_argument_group('USB PHY Options')
	uart_options   = parser.add_argument_group('Debug UART Options')
	scsi_options   = parser.add_argument_group('SCSI Options')

	scsi_options.add_argument(
		'--scsi-did',
		type    = int,
		default = 0x01,
		help    = 'The SCSI Device ID to use'
	)

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

def action_main(args):

	plat = AVAILABLE_PLATFORMS[args.hardware_platform]()

	if args.gateware_action == 'verify':
		inf('Running verification pass')
		wrn('todo')
	elif args.gateware_action == 'simulate':
		inf('Running simulations')
		run_sims(args)
	elif args.gateware_action == 'build':
		inf('Building generic gateware')
		gateware = Squishy(
			uart_config = {
				'enabled'  : args.enable_uart,
				'baud'     : args.baud,
				'parity'   : args.parity,
				'data_bits': args.data_bits,
			},

			usb_config = {
			},

			scsi_config = {
				'did': args.scsi_did,
			}
		)

		plat.build(gateware, name = 'squishy', build_dir = args.build_dir, do_build = True, synth_opts = '-abc9')
	else:
		inf('ニャー')
	return 0
