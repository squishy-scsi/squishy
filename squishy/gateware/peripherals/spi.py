# SPDX-License-Identifier: BSD-3-Clause

'''

'''

from enum              import Flag, auto, unique

from torii             import Elaboratable, Signal, Module, Cat, ResetSignal, ClockSignal, ClockDomain
from torii.build       import Subsignal
from torii.lib.soc.csr import Multiplexer
from torii.lib.cdc     import FFSynchronizer
from ..platform        import SquishyPlatformType

__all__ = (
	'SPIController',
)


class SPIInterface(Elaboratable):
	'''
	Generic SPI interface.


class SPIController(Elaboratable):
	'''

	A generic SPI Bus Controller for a SPI bus with one peripheral on it. (for now)

	Parameters
	----------
	clk : Signal, out
		The clock generated for the SPI bus from this controller.

	cipo : Signal, in
		The data signal coming in from the peripherals on the bus.

	copi : Signal, out
		The data signal going out to the SPI bus from this controller.

	cs : Signal, out
		The selection signal for the device on the SPI bus.

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

	def __init__(self, *, clk: Signal, cipo: Signal, copi: Signal, cs: Signal) -> None:
		self._clk  = clk
		self._cipo = cipo
		self._copi = copi
		self._cs   = cs

		self.cs   = Signal()
		self.xfr  = Signal()
		self.done = Signal()
		self.wdat = Signal(8)
		self.rdat = Signal(8)

	def elaborate(self, _: SquishyPlatformType | None) -> Module:
		m = Module()

		bit = Signal(range(8))
		clk = Signal(reset = 1)

		copi = self._copi
		cipo = self._cipo

		d_in  = Signal.like(self.rdat)
		d_out = Signal.like(self.wdat)

		m.d.comb += self.done.eq(0)

		with m.FSM(name = 'spi_controller'):
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
			self._clk.eq(clk),
			self._cs.eq(self.cs),
		]

		return m
