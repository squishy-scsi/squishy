# SPDX-License-Identifier: BSD-3-Clause
from argparse import ArgumentParser

from squishy.board import *

from squishy.main import TopModule

if __name__ == '__main__':
	parser = ArgumentParser(description='squishy gateware')

	parser.add_argument(
		'--synthesize',
		help='synthesize gateware',
		action='store_true'
	)
	parser.add_argument(
		'--verify',
		help='verify gateware',
		action='store_true'
	)
	parser.add_argument(
		'--simulate',
		help='simulate gateware',
		action='store_true'
	)


	args = parser.parse_args()

	board = Rev0()

	board.build(TopModule(), do_program=False)
