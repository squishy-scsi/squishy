# SPDX-License-Identifier: BSD-3-Clause
from nmigen               import *
from nmigen.sim           import Simulator, Settle

from .                    import sim_case
from ..core.interface.usb import USBInterface

SIM_NAME = 'USB'

DONT_LOAD = 1

class dummy(Elaboratable):
	def elaborate(self, platform):
		m = Module()

		n = Signal()

		m.d.sync += n.eq(~n)

		return m

@sim_case(domains = [ ('sync', 100e6) ], dut = dummy())
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
