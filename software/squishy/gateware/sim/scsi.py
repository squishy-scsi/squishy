# SPDX-License-Identifier: BSD-3-Clause
from nmigen                import *
from nmigen.sim            import Simulator, Settle

from .                     import sim_case, SimPlatform
from ..core.interface.scsi import SCSIInterface

SIM_NAME = 'SCSI'

_scsi_cfg = {
	'vid': 'Shrine-0',
	'did': 1,
}


_wb_cfg = {
	'addr': 8,	# Address width
	'data': 8,	# Data Width
	'gran': 8,	# Bus Granularity
	'feat': {	# Bus Features
		'cti', 'bte'
	}
}

scsi = SCSIInterface(
	config    = _scsi_cfg,
	wb_config = _wb_cfg,
)

@sim_case(domains = [ ('sync', 100e6) ], dut = scsi, platform = SimPlatform())
def sim_dummy(sim, dut):
	def nya():
		for _ in range(8192):
			yield

	return [
		(nya, 'sync')
	]



SIM_CASES = [
	sim_dummy,

]
