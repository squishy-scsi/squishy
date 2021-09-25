# SPDX-License-Identifier: BSD-3-Clause
from ..utility             import *
from ..gateware.platform   import Rev1
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


	usb_options    = parser.add_argument_group('USB PHY Options')
	uart_options   = parser.add_argument_group('Debug UART Options')
	scsi_options   = parser.add_argument_group('SCSI Options')

	usb_options.add_argument(
		'--usb-vid', '-V',
		type    = int,
		default = 0xFEED,
		help    = 'The USB Vendor ID to use'
	)

	usb_options.add_argument(
		'--usb-pid', '-P',
		type    = int,
		default = 0xACA7,
		help    = 'The USB Product ID to use'
	)

	usb_options.add_argument(
		'--usb-manufacturer', '-m',
		type    = str,
		default = 'aki-nyan',
		help    = 'The USB Device Manufacturer'
	)

	usb_options.add_argument(
		'--usb-product', '-p',
		type    = str,
		default = 'squishy',
		help    = 'The USB Device Product'
	)

	usb_options.add_argument(
		'--usb-serial-number', '-s',
		type    = str,
		default = 'ニャ〜',
		help    = 'The USB Device Serial Number'
	)

	scsi_options.add_argument(
		'--scsi-vid',
		type    = str,
		default = 'Shrine-0',
		help    = 'The SCSI Vendor ID to use'
	)

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

	plat = Rev1()

	if args.gateware_action == 'verify':
		wrn('todo')
	elif args.gateware_action == 'simulate':
		run_sims(args)
	elif args.gateware_action == 'build':
		gateware = Squishy(
			uart_config = {
				'enabled'  : args.enable_uart,
				'baud'     : args.baud,
				'parity'   : args.parity,
				'data_bits': args.data_bits,
			},

			usb_config = {
				'vid': args.usb_vid,
				'pid': args.usb_pid,

				'mfr': args.usb_manufacturer,
				'prd': args.usb_product,
				'srn': args.usb_serial_number,
			},

			scsi_config = {
				'vid': args.scsi_vid,
				'did': args.scsi_did,
			}
		)

		plat.build(gateware, name = 'squishy', build_dir = args.build_dir, do_build = True)
	else:
		inf('ニャー')
	return 0
