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

		if name == 'scsi_rx':
			return Record([
				('data', [
					('i', 9),
				]),
				('io', [
					('i', 1)
				]),
				('cd', [
					('i', 1)
				]),
				('req', [
					('i', 1)
				]),
				('sel', [
					('i', 1)
				]),
				('msg', [
					('i', 1)
				]),
				('rst', [
					('i', 1)
				]),
				('ack', [
					('i', 1)
				]),
				('bsy', [
					('i', 1)
				]),
				('atn', [
					('i', 1)
				])
			])

		if name == 'scsi_tx':
			return Record([
				('data', [
					('o', 9),
				]),
				('io', [
					('o', 1)
				]),
				('cd', [
					('o', 1)
				]),
				('req', [
					('o', 1)
				]),
				('sel', [
					('o', 1)
				]),
				('msg', [
					('o', 1)
				]),
				('rst', [
					('o', 1)
				]),
				('ack', [
					('o', 1)
				]),
				('bsy', [
					('o', 1)
				]),
				('atn', [
					('o', 1)
				])
			])

		if name == 'scsi_tx_ctl':
			return Record([
				('tp_en_n', [
					('o', 1)
				]),
				('tx_en_n', [
					('o', 1)
				]),
				('aa_en_n', [
					('o', 1)
				]),
				('bsy_en_n', [
					('o', 1)
				]),
				('sel_en_n', [
					('o', 1)
				]),
				('mr_en_n', [
					('o', 1)
				])
			])

		if name == 'scsi_ctl':
			return Record([
				('diff_sense', [
					('i', 1)
				])
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
