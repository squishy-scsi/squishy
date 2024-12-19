# SPDX-License-Identifier: BSD-3-Clause

'''
This module contains resource definitions for the various SCSI bus types, as well as some Squishy-specific
SCSI interfaces.

'''

from torii.build.dsl import Attrs, Pins, PinsN, Resource, Subsignal, DiffPairs, SubsigArgT, ResourceConn

__all__ = (
	'SquishySCSIPhy',
)


def SquishySCSIPhy(
	name_or_number: str | int, number: int | None = None, *,
	data_lower: str, data_upper: str,
	atn: str, bsy: str, ack: str, rst: str, msg: str, sel: str, cd: str, req: str, io: str,
	data_lower_dir: str, data_upper_dir: str,
	target_dir: str, initiator_dir: str, bsy_dir: str, rst_dir: str, sel_dir: str,
	scl: str, sda: str,
	termpwr_en: str, prsnt: str,
	lowspeed_ctrl: str,
	phy_pwr_en: str,
	conn: ResourceConn | None = None, attrs: Attrs | None = None
) -> Resource:
	ios: list[SubsigArgT] = [
		# Data signals
		Subsignal('data_lower', Pins(data_lower, dir = 'io', conn = conn, assert_width = 9)),
		Subsignal('data_upper', Pins(data_upper, dir = 'io', conn = conn, assert_width = 9)),
		Subsignal('atn',        Pins(atn,        dir = 'io', conn = conn, assert_width = 1)),
		Subsignal('bsy',        Pins(bsy,        dir = 'io', conn = conn, assert_width = 1)),
		Subsignal('ack',        Pins(ack,        dir = 'io', conn = conn, assert_width = 1)),
		Subsignal('rst',        Pins(rst,        dir = 'io', conn = conn, assert_width = 1)),
		Subsignal('msg',        Pins(msg,        dir = 'io', conn = conn, assert_width = 1)),
		Subsignal('sel',        Pins(sel,        dir = 'io', conn = conn, assert_width = 1)),
		Subsignal('cd',         Pins(cd,         dir = 'io', conn = conn, assert_width = 1)),
		Subsignal('req',        Pins(req,        dir = 'io', conn = conn, assert_width = 1)),
		Subsignal('io',         Pins(io,         dir = 'io', conn = conn, assert_width = 1)),
		# Direction signals
		Subsignal('data_lower_dir', Pins(data_lower_dir, dir = 'o', conn = conn, assert_width = 1)),
		Subsignal('data_upper_dir', Pins(data_upper_dir, dir = 'o', conn = conn, assert_width = 1)),
		Subsignal('trgt_dir',       Pins(target_dir,     dir = 'o', conn = conn, assert_width = 1)),
		Subsignal('init_dir',       Pins(initiator_dir,  dir = 'o', conn = conn, assert_width = 1)),
		Subsignal('bsy_dir',        Pins(bsy_dir,        dir = 'o', conn = conn, assert_width = 1)),
		Subsignal('rst_dir',        Pins(rst_dir,        dir = 'o', conn = conn, assert_width = 1)),
		Subsignal('sel_dir',        Pins(sel_dir,        dir = 'o', conn = conn, assert_width = 1)),
		# PHY Control signals
		Subsignal('scl',            Pins(scl,            dir = 'io', conn = conn, assert_width = 1)),
		Subsignal('sda',            Pins(sda,            dir = 'io', conn = conn, assert_width = 1)),
		Subsignal('termpwr_en',     Pins(termpwr_en,     dir = 'o',  conn = conn, assert_width = 1)),
		Subsignal('prsnt',         PinsN(prsnt,          dir = 'i',  conn = conn, assert_width = 1)),
		Subsignal('ls_ctrl',        Pins(lowspeed_ctrl,  dir = 'io', conn = conn, assert_width = 6)),
		Subsignal('pwr_en',         Pins(phy_pwr_en,     dir = 'o',  conn = conn, assert_width = 1)),
	]

	if attrs is not None:
		ios.append(attrs)

	return Resource.family(name_or_number, number, default_name = 'scsi_phy', ios = ios)

def SCSIBus(
	name_or_number: str | int, number: int | None = None, *,
	# 8-bit bus
	d0: str, atn: str, bsy: str, ack: str, rst: str, msg: str, sel: str, cd: str, req: str, io: str,
	diffsense: str,
	# 16-bit bus
	d1: str | None = None,
	# 32-bit bus
	d2: str | None = None, ackq: str | None = None, reqq: str | None = None,
	# SCA-2 Only signals
	scsi_id: str | None = None, spindle: str | None = None,
	rmt_start: str | None = None, dlyd_start: str | None = None, led: str | None = None,
	differential: bool = False, initiator: bool = False,
	conn: ResourceConn | None = None, attrs: Attrs | None = None
) -> list[Resource]:
	# TODO(aki): We can turn a differential bus into a SE bus by just yeeting the positive side
	def _pins(pins: str, dir: str, assert_width: int) -> DiffPairs | PinsN:
		if differential:
			# Split the pins from a string of `P0 N0 P1 N1 ... ` into an in-order list
			pin_split = pins.split(' ')
			# zip every 2 elements into a list tuple pairs `('P0', 'N0'), ...` then zip all the P's and N's
			# together then re-form the strings into 2 strings of 'P0 P1 P2 ...', 'N0 N1 N2 ...'
			p, n = (' '.join(pin_list) for pin_list in zip(*zip(pin_split[::2], pin_split[1::2])))
			return DiffPairs(p, n, dir = dir, assert_width = assert_width)
		else:
			return PinsN(pins, dir = dir, conn = conn, assert_width = assert_width)

	resources: list[Resource] = []

	sig_dir = 'i' if initiator else 'o'

	ios_8bit: list[SubsigArgT] = [
		Subsignal('data0',     _pins(d0,  'io',    9)),
		Subsignal('atn',       _pins(atn, sig_dir, 1)),
		Subsignal('bsy',       _pins(bsy, sig_dir, 1)),
		Subsignal('ack',       _pins(ack, sig_dir, 1)),
		Subsignal('rst',       _pins(rst, sig_dir, 1)),
		Subsignal('msg',       _pins(msg, sig_dir, 1)),
		Subsignal('sel',       _pins(sel, sig_dir, 1)),
		Subsignal('cd',        _pins(cd,  sig_dir, 1)),
		Subsignal('req',       _pins(req, sig_dir, 1)),
		Subsignal('io',        _pins(io,  sig_dir, 1)),
		Subsignal('diffsense', Pins(diffsense, dir = 'i', conn = conn, assert_width = 1)),
	]

	if attrs is not None:
		ios_8bit.append(attrs)

	# Standard 8-bit SCSI bus
	resources.append(Resource.family(
		name_or_number, number, default_name = 'scsi', ios = ios_8bit, name_suffix = '8bit'
	))

	# 16-bit/32-bit/SCA-2
	if d1 is not None:
		ios_16bit = list(ios_8bit)
		ios_16bit.append(Subsignal('data1', _pins(d0, 'io', 9)))

		# 16-bit bus
		resources.append(Resource.family(
			name_or_number, number, default_name = 'scsi', ios = ios_16bit, name_suffix = '16bit'
		))

		# 32-bit bus
		if None not in (d2, ackq, reqq):
			ios_32bit = list(ios_16bit)
			ios_32bit.append(Subsignal('data2', _pins(d0, 'io', 9)))
			ios_32bit.append(Subsignal('ackq', _pins(d0, sig_dir, 1)))
			ios_32bit.append(Subsignal('reqq', _pins(d0, sig_dir, 1)))

			resources.append(Resource.family(
				name_or_number, number, default_name = 'scsi', ios = ios_32bit, name_suffix = '32bit'
			))

		# SCA-2
		if None not in (scsi_id, spindle, rmt_start, dlyd_start, led):
			ios_sca2 = list(ios_16bit)
			ios_sca2.append(Subsignal('scsi_id',    Pins(scsi_id,    dir = sig_dir, conn = conn, assert_width = 4)))
			ios_sca2.append(Subsignal('spindle',    Pins(spindle,    dir = sig_dir, conn = conn, assert_width = 1)))
			ios_sca2.append(Subsignal('rmt_start',  Pins(rmt_start,  dir = sig_dir, conn = conn, assert_width = 1)))
			ios_sca2.append(Subsignal('dlyd_start', Pins(dlyd_start, dir = sig_dir, conn = conn, assert_width = 1)))
			ios_sca2.append(Subsignal('led',        Pins(led,        dir = sig_dir, conn = conn, assert_width = 1)))

			resources.append(Resource.family(
				name_or_number, number, default_name = 'scsi', ios = ios_sca2, name_suffix = 'sca2'
			))

	return resources
