# SPDX-License-Identifier: BSD-3-Clause

'''

'''

from torii.hdl  import Elaboratable, Module

from ..platform import SquishyPlatformType

__all__ = (
	'I2CController',
)


class I2CController(Elaboratable):
	'''

	'''

	def __init__(self):
		pass

	def elaborate(self, platform: SquishyPlatformType | None) -> Module:
		m = Module()

		return m
