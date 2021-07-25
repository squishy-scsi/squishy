# SPDX-License-Identifier: BSD-3-Clause
from nmigen                  import *
from nmigen_stdio.serial     import AsyncSerial
from nmigen_soc.wishbone     import Interface


__all__ = ('UARTInterface')

class UARTInterface(Elaboratable):
	def __init__(self, *, config, wb_config):
		self.config = config
		self._wb_cfg = wb_config

		self.ctl_bus = Interface(
			addr_width  = self._wb_cfg['addr'],
			data_width  = self._wb_cfg['data'],
			granularity = self._wb_cfg['gran'],
			features    = self._wb_cfg['feat']
		)

		self._status_led = None

		self._uart = None

	def elaborate(self, platform):
		self._status_led = platform.request('led', 0)

		self._uart = AsyncSerial(
			# TODO: Figure out how to extract the global clock freq and stuff it into the divisor calc
			divisor      = int(platform.pll_config['freq'] // self.config['baud']),
			divisor_bits = None, # Will force use of `bits_for(divisor)`,
			data_bits    = self.config['data_bits'],
			parity       = self.config['parity'],
			pins         = platform.request('uart')
		)

		m = Module()

		m.submodules += self._uart

		return m
