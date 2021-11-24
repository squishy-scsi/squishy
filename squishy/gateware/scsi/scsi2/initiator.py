# SPDX-License-Identifier: BSD-3-Clause
from math         import ceil, log2

from nmigen       import *

from .....utility import us_to_s, ns_to_s

__all__ = (
	'Initiator'
)


class Initiator(Elaboratable):
	def __init__(self, *, config):
		self.config = config

	def elaborate(self, platform):
		m = Module()


		return m
