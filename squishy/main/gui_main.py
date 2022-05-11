# SPDX-License-Identifier: BSD-3-Clause
import logging    as log
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

from .common        import (
	main_common, common_options, setup_logging
)

def _check_pyside2() -> bool:
	'''Check if PySide2 is installed'''

	try:
		import PySide2 # noqa: F401
		return True
	except ImportError:
		return False

def main() -> int:
	'''Squishy GUI Runner

	This is the main invocation point for the Squishy QT5 GUI.

	Returns
	-------
	int
		0 if execution was successfull, otherwise any other integer on error

	'''

	main_common()

	if not _check_pyside2():
		log.error('To use the Squishy GUI please install PySide2')
		return 1

	from ..gui.application import SquishyGui

	try:

		parser = ArgumentParser(
			formatter_class = ArgumentDefaultsHelpFormatter,
			description     = 'Squishy SCSI Multitool GUI',
			prog            = 'squishy-gui'
		)

		common_options(parser)

		gui = SquishyGui()

		gui.register_args(parser)

		args = parser.parse_args()

		setup_logging(args)

		return gui.run(args)
	except KeyboardInterrupt:
		log.info('bye!')
