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

		if name == 'ulpi':
			return Record([
				('clk', [
					('i', 1)
				]),
				('data', [
					('i', 8),
					('o', 8)
				]),
				('dir', [
					('i', 1)
				]),
				('nxt', [
					('i', 1)
				]),
				('stp', [
					('o', 1)
				]),
				('rst', [
					('o', 1)
				])
			])

		if name == 'scsi_phy':
			return Record([
				('ack', [
					('tx', [
						('o', 1)
					]),
					('rx', [
						('i', 1)
					])
				]),
				('atn', [
					('tx', [
						('o', 1)
					]),
					('rx', [
						('i', 1)
					])
				]),
				('bsy', [
					('tx', [
						('o', 1)
					]),
					('rx', [
						('i', 1)
					])
				]),
				('cd', [
					('tx', [
						('o', 1)
					]),
					('rx', [
						('i', 1)
					])
				]),
				('io', [
					('tx', [
						('o', 1)
					]),
					('rx', [
						('i', 1)
					])
				]),
				('msg', [
					('tx', [
						('o', 1)
					]),
					('rx', [
						('i', 1)
					])
				]),
				('sel', [
					('tx', [
						('o', 1)
					]),
					('rx', [
						('i', 1)
					])
				]),
				('req', [
					('tx', [
						('o', 1)
					]),
					('rx', [
						('i', 1)
					])
				]),
				('rst', [
					('tx', [
						('o', 1)
					]),
					('rx', [
						('i', 1)
					])
				]),
				('d0', [
					('tx', [
						('o', 8)
					]),
					('rx', [
						('i', 8)
					])
				]),
				('dp0', [
					('tx', [
						('o', 1)
					]),
					('rx', [
						('i', 1)
					])
				]),

				('tp_en', [
					('o', 1)
				]),
				('tx_en', [
					('o', 1)
				]),
				('aa_en', [
					('o', 1)
				]),
				('bsy_en', [
					('o', 1)
				]),
				('sel_en', [
					('o', 1)
				]),
				('mr_en', [
					('o', 1)
				]),
				('diff_sense', [
					('i',  1),
					('o',  1),
					('oe', 1),
				]),

				('d1', [
					('tx', [
						('o', 8)
					]),
					('rx', [
						('i', 8)
					])
				]),
				('dp1', [
					('tx', [
						('o', 1)
					]),
					('rx', [
						('i', 1)
					])
				]),

				('id', [
					('tx', [
						('o', 4)
					]),
					('rx', [
						('i', 4)
					])
				]),
				('led', [
					('tx', [
						('o', 1)
					]),
					('rx', [
						('i', 1)
					])
				]),
				('spindle', [
					('tx', [
						('o', 1)
					]),
					('rx', [
						('i', 1)
					])
				]),
				('rmt', [
					('tx', [
						('o', 1)
					]),
					('rx', [
						('i', 1)
					])
				]),
				('dlyd', [
					('tx', [
						('o', 1)
					]),
					('rx', [
						('i', 1)
					])
				]),
			])

def sim_case(*, domains, dut, platform = None):
	def _reg_sim(func):
		from nmigen.sim    import Simulator
		from nmigen.hdl.ir import Fragment

		sim = Simulator(
			Fragment.get(dut, platform = platform)
		)

		for d, clk in domains:
			sim.add_clock(1 / clk, domain = d)

		for case, d in func(sim, dut):
			sim.add_sync_process(case, domain = d)

		return (sim, func.__name__)

	return _reg_sim
