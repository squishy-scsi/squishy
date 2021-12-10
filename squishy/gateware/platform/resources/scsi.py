# SPDX-License-Identifier: BSD-3-Clause
from amaranth.build import *

__all__ = (
	'SCSIConnectorResource',
	'SCSIDifferentialResource',
	'SCSISingleEndedResource',
	'SCSIPhyResource',
)


def TransceiverPairs(tx, rx, *, invert = False, conn = None, assert_width = None):
	return (
		Subsignal('tx', Pins(tx, dir = 'o', invert = invert, conn = conn, assert_width = assert_width)),
		Subsignal('rx', Pins(rx, dir = 'i', invert = invert, conn = conn, assert_width = assert_width)),
	)

def SCSIDifferentialResource(*args, **kwargs):
	return SCSIConnectorResource(*args, diff = True, **kwargs)

def SCSISingleEndedResource(*args, **kwargs):
	return SCSIConnectorResource(*args, diff = False, **kwargs)

def SCSIConnectorResource(*args, diff,
						  ack, atn, bsy, cd, io, msg, sel, req, rst,
						  diff_sense, d0, dp0, d1 = None, dp1  = None,
						  scsi_id = None, led  = None, spindle = None,
						  rmt     = None, dlyd = None, dir     = 'io',
						  attrs   = None):
	if diff:
		io = [
			Subsignal('ack',        DiffPairs(*ack,  dir = dir, assert_width = 1)),
			Subsignal('atn',        DiffPairs(*atn,  dir = dir, assert_width = 1)),
			Subsignal('bsy',        DiffPairs(*bsy,  dir = dir, assert_width = 1)),
			Subsignal('cd',         DiffPairs(*cd,   dir = dir, assert_width = 1)),
			Subsignal('io',         DiffPairs(*io,   dir = dir, assert_width = 1)),
			Subsignal('msg',        DiffPairs(*msg,  dir = dir, assert_width = 1)),
			Subsignal('sel',        DiffPairs(*sel,  dir = dir, assert_width = 1)),
			Subsignal('req',        DiffPairs(*req,  dir = dir, assert_width = 1)),
			Subsignal('rst',        DiffPairs(*rst,  dir = dir, assert_width = 1)),
			Subsignal('d0',         DiffPairs(*d0,   dir = dir, assert_width = 8)),
			Subsignal('dp0',        DiffPairs(*dp0,  dir = dir, assert_width = 1)),
			Subsignal('diff_sense', Pins(diff_sense, dir = dir, assert_width = 1)),
		]
	else:
		io = [
			Subsignal('ack',        Pins(ack,        dir = dir, assert_width = 1)),
			Subsignal('atn',        Pins(atn,        dir = dir, assert_width = 1)),
			Subsignal('bsy',        Pins(bsy,        dir = dir, assert_width = 1)),
			Subsignal('cd',         Pins(cd,         dir = dir, assert_width = 1)),
			Subsignal('io',         Pins(io,         dir = dir, assert_width = 1)),
			Subsignal('msg',        Pins(msg,        dir = dir, assert_width = 1)),
			Subsignal('sel',        Pins(sel,        dir = dir, assert_width = 1)),
			Subsignal('req',        Pins(req,        dir = dir, assert_width = 1)),
			Subsignal('rst',        Pins(rst,        dir = dir, assert_width = 1)),
			Subsignal('d0',         Pins(d0,         dir = dir, assert_width = 8)),
			Subsignal('dp0',        Pins(dp0,        dir = dir, assert_width = 1)),
			Subsignal('diff_sense', Pins(diff_sense, dir = dir, assert_width = 1)),
		]

	if d1 is not None:
		assert dp1 is not None, 'Parity bit for d1 must be present'
		if diff:
			io.append(Subsignal('d1',  DiffPairs(*d1,  dir = dir, assert_width = 8))),
			io.append(Subsignal('dp1', DiffPairs(*dp1, dir = dir, assert_width = 1))),
		else:
			io.append(Subsignal('d1',  Pins(d1,  dir = dir, assert_width = 8))),
			io.append(Subsignal('dp1', Pins(dp1, dir = dir, assert_width = 1))),

	if scsi_id is not None:
		assert led is not None
		assert spindle is not None
		assert rmt is not None
		assert dlyd is not None

		io.append(Subsignal('id',      Pins(scsi_id, dir = dir, assert_width = 4))),
		io.append(Subsignal('led',     Pins(led,     dir = dir, assert_width = 1))),
		io.append(Subsignal('spindle', Pins(spindle, dir = dir, assert_width = 1))),
		io.append(Subsignal('rmt',     Pins(rmt,     dir = dir, assert_width = 1))),
		io.append(Subsignal('dlyd',    Pins(dlyd,    dir = dir, assert_width = 1))),


	if attrs is not None:
		io.append(attrs)

	return Resource.family(*args, default_name = 'scsi_conn', ios = io)


def SCSIPhyResource(*args,
					 ack, atn, bsy, cd, io, msg, sel, req, rst, d0, dp0,
					 tp_en, tx_en, aa_en, bsy_en, sel_en, mr_en,
					 diff_sense,
					 d1   = None, dp1     = None, scsi_id = None,
					 led  = None, spindle = None, rmt     = None,
					 dlyd = None, attrs   = None):

	io = [
		Subsignal('ack',        *TransceiverPairs(*ack,                  assert_width = 1)),
		Subsignal('atn',        *TransceiverPairs(*atn,                  assert_width = 1)),
		Subsignal('bsy',        *TransceiverPairs(*bsy,                  assert_width = 1)),
		Subsignal('cd',         *TransceiverPairs(*cd,                   assert_width = 1)),
		Subsignal('io',         *TransceiverPairs(*io,                   assert_width = 1)),
		Subsignal('msg',        *TransceiverPairs(*msg,                  assert_width = 1)),
		Subsignal('sel',        *TransceiverPairs(*sel,                  assert_width = 1)),
		Subsignal('req',        *TransceiverPairs(*req,                  assert_width = 1)),
		Subsignal('rst',        *TransceiverPairs(*rst,                  assert_width = 1)),
		Subsignal('d0',         *TransceiverPairs(*d0,                   assert_width = 8)),
		Subsignal('dp0',        *TransceiverPairs(*dp0,                  assert_width = 1)),
		Subsignal('tp_en',                PinsN(tp_en,      dir = 'o',  assert_width = 1)),
		Subsignal('tx_en',                PinsN(tx_en,      dir = 'o',  assert_width = 1)),
		Subsignal('aa_en',                PinsN(aa_en,      dir = 'o',  assert_width = 1)),
		Subsignal('bsy_en',               PinsN(bsy_en,     dir = 'o',  assert_width = 1)),
		Subsignal('sel_en',               PinsN(sel_en,     dir = 'o',  assert_width = 1)),
		Subsignal('mr_en',                PinsN(mr_en,      dir = 'o',  assert_width = 1)),
		Subsignal('diff_sense',            Pins(diff_sense, dir = 'i',  assert_width = 1)),
	]

	if d1 is not None:
		assert dp1 is not None, 'Parity bit for d1 must be present'
		io.append(Subsignal('d1',  *TransceiverPairs(*d1,  assert_width = 8))),
		io.append(Subsignal('dp1', *TransceiverPairs(*dp1, assert_width = 1))),

	if scsi_id is not None:
		assert led is not None
		assert spindle is not None
		assert rmt is not None
		assert dlyd is not None

		io.append(Subsignal('id',      *TransceiverPairs(scsi_id, assert_width = 4))),
		io.append(Subsignal('led',     *TransceiverPairs(led,     assert_width = 1))),
		io.append(Subsignal('spindle', *TransceiverPairs(spindle, assert_width = 1))),
		io.append(Subsignal('rmt',     *TransceiverPairs(rmt,     assert_width = 1))),
		io.append(Subsignal('dlyd',    *TransceiverPairs(dlyd,    assert_width = 1))),

	if attrs is not None:
		io.append(attrs)

	return Resource.family(*args, default_name = 'scsi_phy', ios = io)
