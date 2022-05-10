# SPDX-License-Identifier: BSD-3-Clause
import logging    as log
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

from .common        import (
	main_common, common_options, setup_logging
)

def main() -> int:
	'''Squishy GUI Runner

	This is the main invocation point for the Squishy QT5 GUI.

	Returns
	-------
	int
		0 if execution was successfull, otherwise any other integer on error

	'''
	try:
		from ..actions.gui import GUI
	except ImportError:
		log.error('To use the Squishy GUI please install PySide2')
		return 1

	try:
		main_common()

		parser = ArgumentParser(
			formatter_class = ArgumentDefaultsHelpFormatter,
			description     = 'Squishy SCSI Multitool GUI',
			prog            = 'squishy-gui'
		)

		common_options(parser)

		gui = GUI()

		gui.register_args(parser)

		args = parser.parse_args()

		setup_logging(args)

		return gui.run(args)
	except KeyboardInterrupt:
		log.info('bye!')
