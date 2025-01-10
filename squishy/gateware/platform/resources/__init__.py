# SPDX-License-Identifier: BSD-3-Clause

'''
This module contains a collection of mostly Squishy-specific resources, for the generic SCSI bus resources see
:py:mod:`squishy.platform.resources.scsi`.

'''

from torii.build.dsl import Attrs, Pins, PinsN, Resource, Subsignal, DiffPairs, SubsigArgT, ResourceConn

__all__ = (
	'BankedHyperRAM',
	'PDController',
	'PhyADC',
	'SquishySupervisor',
	'USB3SerDesPHY',
)

def BankedHyperRAM(
	name_or_number: str | int, number: int | None = None, *,
	data_even: str, cs_even: str, clk_even: str,
	data_odd: str,  cs_odd: str,  clk_odd: str,
	rwds: str, rst: str,
	conn: ResourceConn | None = None, attrs: Attrs | None = None
) -> Resource:
	'''
	Squishy rev2 has a weird even/odd banked HyperRAM setup, so we can't use the Torii built-in resource
	'''

	clk_even_p, clk_even_n = clk_even.split(' ', maxsplit = 1)
	clk_odd_p, clk_odd_n   = clk_odd.split(' ', maxsplit = 1)

	ios: list[SubsigArgT] = [
		# Even bank
		Subsignal('dq_evn',       Pins(data_even,              dir = 'io', conn = conn, assert_width = 8)),
		Subsignal('cs_evn',      PinsN(cs_even,                dir = 'o',  conn = conn, assert_width = 2)),
		Subsignal('clk_evn', DiffPairs(clk_even_p, clk_even_n, dir = 'o',  conn = conn, assert_width = 1)),

		# Odd bank
		Subsignal('dq_odd',       Pins(data_odd,             dir = 'io', conn = conn, assert_width = 8)),
		Subsignal('cs_odd',      PinsN(cs_odd,               dir = 'o',  conn = conn, assert_width = 2)),
		Subsignal('clk_odd', DiffPairs(clk_odd_p, clk_odd_n, dir = 'o',  conn = conn, assert_width = 1)),

		# Common
		Subsignal('rwds', Pins(rwds, dir = 'io', conn = conn, assert_width = 1)),
		Subsignal('rst',  Pins(rst,  dir = 'o',  conn = conn, assert_width = 1)),
	]

	if attrs is not None:
		ios.append(attrs)

	return Resource.family(name_or_number, number, default_name = 'hyperram', ios = ios)


def PDController(
	name_or_number: str | int, number: int | None = None, *,
	scl: str, sda: str, pol: str | None = None,
	conn: ResourceConn | None = None, attrs: Attrs | None = None
) -> Resource:
	''' Basically just I²C with an outgoing `pol` signal for a USB-3 mux '''

	ios: list[SubsigArgT] = [
		Subsignal('scl', Pins(scl, dir = 'io', conn = conn, assert_width = 1)),
		Subsignal('sda', Pins(sda, dir = 'io', conn = conn, assert_width = 1)),
	]

	if pol is not None:
		ios.append(Subsignal('pol', Pins(pol, dir = 'o', conn = conn, assert_width = 1)))

	if attrs is not None:
		ios.append(attrs)

	return Resource.family(name_or_number, number, default_name = 'usb_pd', ios = ios)

def PhyADC(
	name_or_number: str | int, number: int | None = None, *,
	clk: str, dat: str, chan: str,
	conn: ResourceConn | None = None, attrs: Attrs | None = None
) -> Resource:
	ios: list[SubsigArgT] = [
		Subsignal('clk',  Pins(clk,  dir = 'o', conn = conn, assert_width = 1)),
		Subsignal('dat',  Pins(dat,  dir = 'i', conn = conn, assert_width = 1)),
		Subsignal('chan', Pins(chan, dir = 'o', conn = conn, assert_width = 1)),
	]

	if attrs is not None:
		ios.append(attrs)

	return Resource.family(name_or_number, number, default_name = 'phy_adc', ios = ios)

def SquishySupervisor(
	clk: str, copi: str, cipo: str, attn: str, psram: str, su_irq: str, bus_hold: str,
	conn: ResourceConn | None = None, attrs: Attrs | None = None
) -> Resource:
	ios: list[SubsigArgT] = [
		Subsignal('clk',   Pins(clk,  dir = 'io', conn = conn, assert_width = 1)),
		Subsignal('copi',  Pins(cipo, dir = 'io', conn = conn, assert_width = 1)),
		Subsignal('cipo',  Pins(copi, dir = 'io', conn = conn, assert_width = 1)),
		# Supervisor -> FPGA "CS"
		Subsignal('attn', PinsN(attn, dir = 'i',  conn = conn, assert_width = 1)),
		# FPGA -> PSRAM CS
		Subsignal('psram', Pins(psram, dir = 'o', conn = conn, assert_width = 1)),
		# FPGA -> Supervisor IRQ/Bus Hold
		Subsignal('su_irq',   Pins(su_irq,   dir = 'o', conn = conn, assert_width = 1)),
		Subsignal('bus_hold', Pins(bus_hold, dir = 'o', conn = conn, assert_width = 1)),
	]

	if attrs is not None:
		ios.append(attrs)

	return Resource.family('supervisor', 0, default_name = 'supervisor', ios = ios)

def USB3SerDesPHY(
	name_or_number: str | int, number: int | None = None, *,
	rx_p: str, rx_n: str, tx_p: str, tx_n: str, refclk_p: str | None = None, refclk_n: str | None = None
) -> Resource:
	ios: list[SubsigArgT] = [
		Subsignal('rx', DiffPairs(rx_p, rx_n, dir = 'i', assert_width = 1)),
		Subsignal('tx', DiffPairs(tx_p, tx_n, dir = 'o', assert_width = 1)),
	]

	if None not in (refclk_p, refclk_n):
		ios.append(Subsignal('refclk', DiffPairs(refclk_p, refclk_n, dir = 'i', assert_width = 1)))

	return Resource.family(name_or_number, number, default_name = 'usb3', ios = ios)
