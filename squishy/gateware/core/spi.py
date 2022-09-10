# SPDX-License-Identifier: BSD-3-Clause
from amaranth import *

__all__ = (
	'SPIInterface',
)

class SPIInterface(Elaboratable):
	'''Generic SPI interface.

	Attributes
	----------
	cs : Signal
		SPI Chip Select.

	xfr : Signal
		Transfer strobe.

	done : Signal
		Transfer complete signal.

	wdat : Signal(8)
		Write data register.

	rdat : Signal(8)
		Read data register.

	'''
	def __init__(self, *, resource_name):

		self._spi_resource = resource_name
		self._status_led = None
		self._spi = None

		self.cs   = Signal()
		self.xfr  = Signal()
		self.done = Signal()
		self.wdat = Signal(8)
		self.rdat = Signal(8)

	def elaborate(self, platform):
		self._spi = platform.request(*self._spi_resource)

		m = Module()

		bit = Signal(range(8))
		clk = Signal(reset = 1)

		cipo = self._spi.cipo.i
		copi = self._spi.copi.o

		d_in  = Signal.like(self.rdat)
		d_out = Signal.like(self.wdat)

		m.d.comb += self.done.eq(0)

		with m.FSM(name = 'spi'):
			with m.State('IDLE'):
				m.d.sync += clk.eq(1)
				with m.If(self.xfr):
					m.d.sync += d_out.eq(self.wdat)
					m.next = 'XFR'
			with m.State('XFR'):
				with m.If(clk):
					m.d.sync += [
						clk.eq(0),
						bit.eq(bit + 1),
						copi.eq(d_out[7]),
					]
				with m.Else():
					m.d.sync += [
						clk.eq(1),
						d_out.eq(d_out.shift_left(1)),
						d_in.eq(Cat(cipo, d_in[:-1])),
					]
					with m.If(bit == 0):
						m.next = 'DONE'
			with m.State('DONE'):
				m.d.comb += self.done.eq(1)
				m.d.sync += self.rdat.eq(d_in)
				with m.If(self.xfr):
					m.d.sync += d_out.eq(self.wdat)
					m.next = 'XFR'
				with m.Else():
					m.next = 'IDLE'

		m.d.comb += [
			self._spi.clk.o.eq(clk),
			self._spi.cs.o.eq(self.cs),
		]

		return m


# -------------- #

from amaranth.sim     import Settle

from ...core.test     import SquishyGatewareTestCase, sim_test

class SPIInterfaceTests(SquishyGatewareTestCase):
	dut = SPIInterface

	def send_recv(self, d_out, d_in, ovlp = False):
		self.assertEqual((yield self.dut._spi.clk.o), 1)
		yield self.dut.wdat.eq(d_out)
		yield self.dut.xfr.eq(1)
		yield Settle()
		yield
		self.assertEqual((yield self.dut._spi.clk.o), 1)
		yield self.dut.xfr.eq(0)
		yield Settle()
		yield
		for bit in range(8):
			self.assertEqual((yield self.dut._spi.clk.o), 1)
			yield self.dut._spi.cipo.i.eq((d_in >> (7 - bit)) & 1)
			yield Settle()
			yield
			self.assertEqual((yield self.dut._spi.clk.o), 0)
			self.assertEqual((yield self.dut._spi.copi.o), ((d_out >> (7 - bit)) & 1))
			yield Settle()
			yield
		self.assertEqual((yield self.dut._spi.clk.o), 1)
		self.assertEqual((yield self.dut.done), 1)
		if not ovlp:
			yield Settle()
			yield
			self.assertEqual((yield self.dut._spi.clk.o), 1)
			self.assertEqual((yield self.dut.done), 0)
			self.assertEqual((yield self.dut.rdat), d_in)
		yield Settle()

	@sim_test
	def test_spi(self):
		yield
		self.assertEqual((yield self.dut._spi.clk.o), 1)
		yield self.dut.cs.eq(1)
		yield Settle()
		yield
		yield from self.send_recv(0x0F, 0xF0)
		yield
		self.assertEqual((yield self.dut._spi.clk.o), 1)
		yield self.dut.cs.eq(0)
		yield Settle()
		yield
		self.assertEqual((yield self.dut._spi.clk.o), 1)
		yield self.dut.cs.eq(1)
		yield Settle()
		yield
		yield from self.send_recv(0xAA, 0x55, ovlp = True)
		yield from self.send_recv(0x55, 0xAA, ovlp = False)
		yield
		yield self.dut.cs.eq(0)
		yield Settle()
		yield
