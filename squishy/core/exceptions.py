# SPDX-License-Identifier: BSD-3-Clause

__all__ = (
	'SquishyException',
	'SquishyAppletError',
	'SquishyDeviceError',
	'SquishyBuildError',
)

class SquishyException(Exception):
	'''Base class for Squishy related exceptions'''
	pass

class SquishyAppletError(SquishyException):
	'''Exceptions related to Squishy applets'''
	pass

class SquishyDeviceError(SquishyException):
	'''Exceptions related to Squishy hardware'''
	pass

class SquishyBuildError(SquishyException):
	'''Exceptions related to Squishy builds'''
	pass
