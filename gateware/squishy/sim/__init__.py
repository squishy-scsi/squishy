# SPDX-License-Identifier: BSD-3-Clause
__all__ = ()

def sim_case(*, domains, dut):
	def _reg_sim(func):
		from nmigen.sim import Simulator

		sim = Simulator(dut)

		for d, clk in domains:
			sim.add_clock(1 / clk, domain = d)

		cases = func(sim, dut)

		for case, d in func(sim, dut):
			sim.add_sync_process(case, domain = d)

		return (sim, func.__name__)

	return _reg_sim
