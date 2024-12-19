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
