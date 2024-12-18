# SPDX-License-Identifier: BSD-3-Clause

'''

'''

from torii.build.dsl import Attrs, Pins, PinsN, Resource, Subsignal, DiffPairs, SubsigArgT, ResourceConn

__all__ = (
	'BankedHyperRAM',
	'PDController',
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
