# SPDX-License-Identifier: BSD-3-Clause
from math         import ceil

from amaranth       import *

from ....utility import us_to_s, ns_to_s

from ..common     import *


__all__ = (
	'Device',
	'Initiator',
)

class SCSI1(Elaboratable):
	def __init__(self, *, is_device, arbitrating, config):
		self.is_device   = is_device
		self.arbitrating = arbitrating
		self.config      = config

	def elaborate(self, platform):
		m = Module()

		# TODO: timers et. al. :nya_flop:


		# SCSI-1 State Machine Overview
		#    ┌────────────────────────┐
		#    │         Reset          │
		#    └────────────────────────┘
		#      │
		#      │
		#      ▼
		#    ┌──────────────────────────────────┐
		# ┌▶ │             Bus Free             │
		# │  └──────────────────────────────────┘
		# │    │                         ▲    ▲
		# │    │                         │    │
		# │    ▼                         │    │
		# │  ┌────────────────────────┐  │    │
		# │  │      Arbitration       │ ─┘    │
		# │  └────────────────────────┘       │
		# │    │                              │
		# │    │                              │
		# │    ▼                              │
		# │  ┌────────────────────────┐       │
		# │  │       Selection        │ ──────┘
		# │  └────────────────────────┘
		# │    │
		# │    │
		# │    ▼
		# │  ┌────────────────────────┐
		# └─ │ Command, Message, Data │
		#    └────────────────────────┘
		with m.FSM(reset = 'rst'):
			with m.State('rst'):

				m.next = 'bus-free'

			with m.State('bus-free'):

				m.next = 'bus-free'

			with m.State('arbitration'):

				m.next = 'bus-free'

			with m.State('selection'):

				m.next = 'bus-free'

			with m.State('re-selection'):

				m.next = 'bus-free'

			with m.State('data-in'):

				m.next = 'bus-free'

			with m.State('data_out'):

				m.next = 'bus-free'

			with m.State('command'):

				m.next = 'bus-free'

			with m.State('status'):

				m.next = 'bus-free'

			with m.State('message-in'):

				m.next = 'bus-free'

			with m.State('message-out'):

				m.next = 'bus-free'

		return m

def Device(*args, **kwargs):
	return SCSI1(*args, is_device = True, **kwargs)

def Initiator(*args, **kwargs):
	return SCSI1(*args, is_device = False, **kwargs)
