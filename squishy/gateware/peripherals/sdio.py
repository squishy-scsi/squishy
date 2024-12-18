# SPDX-License-Identifier: BSD-3-Clause

'''

'''

from torii             import Elaboratable, Signal, Module
from ..platform        import SquishyPlatformType

__all__ = (
	'SDIOController',
)


class SDIOController(Elaboratable):
	'''

	'''

	def __init__(self):
		pass

	def elaborate(self, platform: SquishyPlatformType | None) -> Module:
		m = Module()

		return m
