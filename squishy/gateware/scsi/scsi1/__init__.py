# SPDX-License-Identifier: BSD-3-Clause
from torii    import Elaboratable, Module

__all__ = (
	'SCSI1',

	'Device',
	'Initiator',
)

__doc__ = '''\

'''

class SCSI1(Elaboratable):
	'''
	SCSI 1 Elaboratable

	This elaboratable represents an interface for interacting with SCSI-1 compliant buses.

	Parameters
	----------
	config : dict
		The configuration for this Elaboratable, including SCSI VID and DID.

	'''

	def __init__(self, *, config: dict) -> None:
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

def Device(*, config: dict) -> SCSI1:
	''' Create a SCSI-1 Device Elaboratable '''
	return SCSI1({'is_device': True, **config})

def Initiator(*, config: dict) -> SCSI1:
	''' Create a SCSI-1 Initiator Elaboratable '''
	return SCSI1({'is_device': False, **config})

# -------------- #

# from ....core.test import SquishyGatewareTestCase, sim_test
#
# class SCSI1Tests(SquishyGatewareTestCase):
# 	dut = SCSI1
# 	dut_args = {
# 		'is_device': True,
# 		'arbitrating': True,
# 		'config': None
# 	}
#
# 	@sim_test
# 	def test_uwu(self):
# 		yield from self.step(30)
