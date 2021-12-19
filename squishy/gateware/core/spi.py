# SPDX-License-Identifier: BSD-3-Clause
from amaranth import *

__all__ = (
	'SPI',
)

class SPI(Elaboratable):
	def __init__(self):

		self._status_led = None
		self._spi = None

	def elaborate(self, platform):
		self._spi = platform.request('spi_flash_1x')
		self._status_led = platform.request('led', 3)

		m = Module()


		return m
