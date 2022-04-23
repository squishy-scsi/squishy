# SPDX-License-Identifier: BSD-3-Clause
from math             import ceil

from amaranth         import *

from ....misc.utility import us_to_s, ns_to_s

from ..common         import *


__all__ = (
	'Device',
	'Initiator',
)

class SCSI1(Elaboratable):
	'''SCSI 1 Elaboratable

	This elaboratable represents an interface for interacting with SCSI-1 compliant bus'.

	Paramaters
	----------
	is_device : bool
		If this SCSI-1 Elaboratable is a Device or Initiator.

	arbitrating : bool
		If this SCSI-1 Elaboratable has arbitration support.

	config : dict
		The configuration for this Elaboratable, including SCSI VID and DID.

	'''

	def __init__(self, *, is_device : bool, arbitrating : bool, config : dict):
		self.is_device   = is_device
		self.arbitrating = arbitrating
		self.config      = config

	def elaborate(self, platform) -> Module:
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

def Device(*args, **kwargs) -> SCSI1:
	'''Create a SCSI-1 Device Elaboratable'''
	return SCSI1(*args, is_device = True, **kwargs)

def Initiator(*args, **kwargs) -> SCSI1:
	'''Create a SCSI-1 Initiator Elaboratable'''
	return SCSI1(*args, is_device = False, **kwargs)
