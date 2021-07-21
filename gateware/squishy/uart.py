# SPDX-License-Identifier: BSD-3-Clause
from nmigen              import *
from nmigen_stdio.serial import AsyncSerial

__all__ = ('UARTInterface')

class UARTInterface(Elaboratable):
	def __init__(self, *, config):
		self.config = config

		self._uart = None

	def elaborate(self, platform):
		if self.config['enabled']:
			self._uart = AsyncSerial(
				# TODO: Figure out how to extract the global clock freq and stuff it into the divisor calc
				divisor      = int(48e6 // self.config['baud']),
				divisor_bits = None, # Will force use of `bits_for(divisor)`,
				data_bits    = self.config['data_bits'],
				parity       = self.config['parity'],
				pins         = platform.request('uart')
			)

		m = Module()


		return m
