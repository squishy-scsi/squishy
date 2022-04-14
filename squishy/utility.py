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

	'iec_size',
)

def print_table(lst, columns = 2):
	for idx, itm in enumerate(lst):
		print(f'{itm:<20}', end='\t')
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

def iec_size(size):
	from math import floor, log, pow

	suffixes = (
		  'B', 'KiB', 'MiB',
		'GiB', 'TiB', 'PiB',
		'EiB', 'ZiB', 'YiB',
	)

	if size == 0:
		return '0B'

	scale = int(floor(log(size, 1024)))
	power = pow(1024, scale)
	fixed = round((size / power), 2)
	return f'{fixed}{suffixes[scale]}'
