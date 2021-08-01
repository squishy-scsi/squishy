# SPDX-License-Identifier: BSD-3-Clause
from nmigen                import *
from nmigen.sim            import Simulator, Settle

from .                     import sim_case
from ..core.interface.scsi import SCSIInterface

SIM_NAME = 'SCSI'

DONT_LOAD = 1

class dummy(Elaboratable):
	def elaborate(self, platform):
		m = Module()

		n = Signal()

		m.d.sync += n.eq(~n)

		return m

@sim_case(domains = [ ('sync', 48e9) ], dut = dummy())
def sim_dummy(sim, dut):
	def nya():
		yield Settle()
		for _ in range(1024):
			yield

	return [
		(nya, 'sync')
	]



SIM_CASES = [
	sim_dummy,

]
