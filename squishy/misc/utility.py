# SPDX-License-Identifier: BSD-3-Clause

__all__ = (
	'ns_to_s',
	'us_to_s',
	'ms_to_s',

	'iec_size',
)

NS = 1e-9
US = 1e-6
MS = 1e-3

def ns_to_s(val : float) -> float:
	'''Convert a value in nanoseconds to Seconds.

	Parameters
	----------
	val : float
		Nanoseconds

	Returns
	-------
	float
		Seconds

	'''

	return val * NS

def us_to_s(val : float) -> float:
	'''Convert a value in microseconds to Seconds.

	Parameters
	----------
	val : float
		Microseconds

	Returns
	-------
	float
		Seconds

	'''

	return val * US

def ms_to_s(val : float) -> float:
	'''Convert a value in milliseconds to Seconds.

	Parameters
	----------
	val : float
		Milliseconds

	Returns
	-------
	float
		Seconds

	'''

	return val * MS

def iec_size(size : int) -> str:
	'''Coverts byte count into a IEC string.

	Parameters
	----------
	size : int
		Number of bytes

	Returns
	-------
	str
		Formatted string

	'''

	from math import floor, log, pow

	suffixes = (
		'B'  , 'KiB', 'MiB',
		'GiB', 'TiB', 'PiB',
		'EiB', 'ZiB', 'YiB',
	)

	if size == 0:
		return '0B'

	scale = int(floor(log(size, 1024)))
	power = pow(1024, scale)
	fixed = round((size / power), 2)
	return f'{fixed}{suffixes[scale]}'
