# SPDX-License-Identifier: BSD-3-Clause
from nmigen import *

__all__ = ('LEDInterface')

class LEDInterface(Elaboratable):
	def __init__(self):

		self._leds = None

	def elaborate(self, platform):
		self._leds = platform.request('leds')

		m = Module()


		return m
