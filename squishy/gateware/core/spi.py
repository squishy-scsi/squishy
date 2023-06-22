# SPDX-License-Identifier: BSD-3-Clause

from torii  import (
	Elaboratable, Signal, Module, Cat
)

__all__ = (
	'SPIInterface',
)

class SPIInterface(Elaboratable):
	'''
	Generic SPI interface.

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
	def __init__(self, *, resource_name: tuple[str, int]) -> None:

		self._spi_resource = resource_name
		self._status_led = None
		self._spi = None

		self.cs   = Signal()
		self.xfr  = Signal()
		self.done = Signal()
		self.wdat = Signal(8)
		self.rdat = Signal(8)

	def elaborate(self, platform) -> Module:
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
