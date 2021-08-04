# SPDX-License-Identifier: BSD-3-Clause
__all__ = ()


class SimPlatform():

	default_clk = 'clk'

	pll_config = {
		'freq': 1e8,
	}

	# clock_domain_generator

	def request(self, name, num = 0):
		from nmigen     import Signal
		from nmigen.hdl import Record

		if name == 'led':
			return Signal(name = f'led_{num}')
		if name == 'uart':
			return Record([
				('rx', [
					('i', 1),
					('o', 1)
				]),
				('tx',[
					('i', 1),
					('o', 1)
				])
			])

def sim_case(*, domains, dut):
	def _reg_sim(func):
		from nmigen.sim import Simulator

		sim = Simulator(dut)

		for d, clk in domains:
			sim.add_clock(1 / clk, domain = d)

		for case, d in func(sim, dut):
			sim.add_sync_process(case, domain = d)

		return (sim, func.__name__)

	return _reg_sim
