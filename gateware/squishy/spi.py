# SPDX-License-Identifier: BSD-3-Clause
from nmigen import *

__all__ = ('SPIInterface')

class SPIInterface(Elaboratable):
	def __init__(self):

		self._spi = None

	def elaborate(self, platform):
		self._spi = platform.request('spi_flash_1x')

		m = Module()


		return m
