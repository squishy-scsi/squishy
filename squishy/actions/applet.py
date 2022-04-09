# SPDX-License-Identifier: BSD-3-Clause
import logging as log
from pathlib   import Path

from ..applets import SquishyApplet
from ..config  import SQUISHY_APPLETS

ACTION_NAME = 'applet'
ACTION_DESC = 'Squishy applets'

def _collect_applets(pkg, prefix):
	from pkgutil    import walk_packages
	from importlib  import import_module
	from inspect    import getmembers, isclass

	pkg = str(pkg)

	applets = []

	def _filter(member):
		if isclass(member):
			return issubclass(member, SquishyApplet) and member is not SquishyApplet
		return False

	for _, name, is_pkg in walk_packages(path = (pkg,), prefix = prefix):
		pkg_import = import_module(name)
		found_applets = getmembers(pkg_import, _filter)

		if len(found_applets) > 0:
			for applet_name, applet in found_applets:
				applets.append({
					'name' : applet_name.lower(),
					'instance': applet()
				})

	return applets

def _collect_all_applets():
	from .. import applets
	return [
		*_collect_applets(Path(applets.__path__[0]), f'{applets.__name__}.'),
		*_collect_applets(SQUISHY_APPLETS, '')
	]

def parser_init(parser):
	applets = _collect_all_applets()


	# actions = parser.add_subparsers(dest = 'gateware_action')

	# do_verify = actions.add_parser('verify', help = 'Run formal verification')
	# verify_options = do_verify.add_argument_group('Verification options')

	# do_simulation  = actions.add_parser('simulate', help = 'Run simulation test cases')
	# sim_options    = do_simulation.add_argument_group('Simulation Options')

	# do_build       = actions.add_parser('build', help = 'Build the gateware')

	pnr_options    = parser.add_argument_group('Gateware Place and Route Options')
	synth_options  = parser.add_argument_group('Gateware Synth Options')

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


	applet_parser = parser.add_subparsers(
		dest     = 'applet',
		required = True
	)

	if len(applets) > 0:
		for apl in applets:
			applet = apl['instance']
			p = applet_parser.add_parser(
					apl['name'],
					help = applet.short_help,
				)
			applet.register_args(p)

def action_main(args):
	log.warning('The applet action is currently unimplemented')
	return 0
