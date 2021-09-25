# SPDX-License-Identifier: BSD-3-Clause
import sys

__all__ = (
	'log',
	'err',
	'wrn',
	'inf',
	'dbg',
	'print_table',

	'ns_to_s',
	'us_to_s',
	'ms_to_s',
)

def log(str, end = '\n', file = sys.stdout):
	print(f'\x1B[35m[*]\x1B[0m {str}', end = end, file = file)

def err(str, end = '\n', file = sys.stderr):
	print(f'\x1B[31m[!]\x1B[0m {str}', end = end, file = file)

def wrn(str, end = '\n', file = sys.stderr):
	print(f'\x1B[33m[~]\x1B[0m {str}', end = end, file = file)

def inf(str, end = '\n', file = sys.stdout):
	print(f'\x1B[36m[~]\x1B[0m {str}', end = end, file = file)

def dbg(str, end = '\n', file = sys.stdout):
	print(f'\x1B[34m[~]\x1B[0m {str}', end = end, file = file)

def print_table(lst, columns = 2):
	for idx, itm in enumerate(lst):
		print(f'{itm:>25}', end='\t')
		if (idx + 1) % columns == 0:
			print('')
	print('')

ns = 1e-9
us = 1e-6
ms = 1e-3

def ns_to_s(val):
	return val * ns

def us_to_s(val):
	return val * us

def ms_to_s(val):
	return val * ms
