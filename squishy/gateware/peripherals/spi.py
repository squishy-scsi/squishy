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
	'SPIInterface',
	'SPIInterfaceMode',
	'SPIController',
	'SPIPeripheral'
)

@unique
class SPIInterfaceMode(Flag):
	CONTROLLER = auto()
	PERIPHERAL = auto()
	BOTH       = CONTROLLER | PERIPHERAL

class SPIInterface(Elaboratable):
	'''
	Generic SPI interface.


	Attributes
	----------
	active_mode: Signal

	'''

	def __init__(
		self, *,
		clk: Subsignal, cipo: Subsignal, copi: Subsignal, cs_peripheral: Subsignal, cs_controller: Subsignal,
		mode: SPIInterfaceMode = SPIInterfaceMode.BOTH, reg_map: Multiplexer | None = None
	) -> None:

		# Subsignals for SPI Bus from SPI Resource
		self._clk  = clk
		self._cipo = cipo
		self._copi = copi
		self._cs_peripheral = cs_peripheral
		self._cs_controller = cs_controller

		self._mode = mode

		if self._mode == SPIInterfaceMode.BOTH:
			self.active_mode = Signal(decoder = lambda i: 'ctrl' if i == 1 else 'perh')

		if self._mode & SPIInterfaceMode.CONTROLLER:
			self.controller = SPIController(
				clk = self._clk.o, cipo = self._cipo.i, copi = self._copi.o, cs = self._cs_controller.o
			)

		if self._mode & SPIInterfaceMode.PERIPHERAL:
			self.peripheral = SPIPeripheral(
				clk = self._clk.i, cipo = self._cipo.o, copi = self._copi.i, cs = self._cs_peripheral.i,
				reg_map = reg_map
			)

	def elaborate(self, _: SquishyPlatformType | None) -> Module:
		m = Module()

		if self._mode & SPIInterfaceMode.CONTROLLER:
			m.submodules.ctrl = self.controller

		if self._mode & SPIInterfaceMode.PERIPHERAL:
			m.submodules.perh = self.peripheral

		if self._mode == SPIInterfaceMode.BOTH:
			# active_mode: 1 = Controller; 0 = Peripheral
			m.d.comb += [
				self._clk.oe.eq(self.active_mode),
				self._cipo.oe.eq(~self.active_mode),
				self._copi.oe.eq(self.active_mode),
			]

		return m


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


class SPIPeripheral(Elaboratable):
	'''

	Attributes
	----------

	'''

	def __init__(self, *, clk: Signal, cipo: Signal, copi: Signal, cs: Signal, reg_map: Multiplexer | None = None) -> None:
		self._clk  = clk
		self._cipo = cipo
		self._copi = copi
		self._cs   = cs

		self._reg_bus = reg_map.bus

	def elaborate(self, _: SquishyPlatformType | None) -> Module:
		m = Module()

		m.domains.spi = ClockDomain()

		addr       = Signal(self._reg_bus.addr_width)
		addr_cntr  = Signal(range(self._reg_bus.addr_width))
		wait_cntr  = Signal(range(8))
		data_read  = Signal(self._reg_bus.data_width) # Out to the SPI Bus
		data_write = Signal.like(data_read)           # In from the SPI Bus
		data_cntr  = Signal(range(data_write.width))

		with m.FSM(name = 'spi_peripheral', domain = 'spi'):
			with m.State('IDLE'):
				with m.If(self._cs):
					m.d.spi += [
						addr.eq(0),
						addr_cntr.eq(0),
					]
					m.next = 'READ_ADDR'

			with m.State('READ_ADDR'):
				m.d.spi += [
					addr_cntr.eq(addr_cntr + 1),
					addr.eq(Cat(self._copi, addr.shift_left(1))),
				]

				with m.If(addr_cntr == (addr.width - 1)):
					if (addr.width & 0b111):
						m.d.spi += [ wait_cntr.eq(0), ]
						m.next = 'WAIT_DATA'
					else:
						# This and the identical block in `WAIT_DATA` can't be in their own state
						# due to cycle timing, so alas, we duplicate
						m.d.comb += [ self._reg_bus.r_stb.eq(1), ]
						m.d.spi  += [ data_read.eq(self._reg_bus.r_data), ]
						m.next = 'READ_DATA'

			with m.State('WAIT_DATA'):
				m.d.spi += [
					wait_cntr.eq(wait_cntr + 1),
				]

				with m.If(wait_cntr == 7 - (addr.width & 0b111)):
					m.d.comb += [ self._reg_bus.r_stb.eq(1), ]
					m.d.spi  += [ data_read.eq(self._reg_bus.r_data), ]
					m.next = 'READ_DATA'

			with m.State('READ_DATA'):
				m.d.spi += [
					data_cntr.eq(data_cntr + 1),
					# Wiggle in the `data_write` value
					data_write.eq(Cat(self._copi, data_write.shift_left(1))),
					# Wiggle out the `data_read` value
					self._cipo.eq(data_read.bit_select(data_cntr, 1)),
				]

				with m.If(data_cntr == (data_write.width - 1)):
					with m.If(self._cs):
						m.d.spi += [
							addr.eq(addr + 1),
							data_cntr.eq(0),
							data_read.eq(self._reg_bus.r_data),
						]
						m.d.comb += [ self._reg_bus.r_stb.eq(1), ]
						# If we're still selected, then give the address uppies and read the next register out
					with m.Else():
						m.next = 'STORE_DATA'

			with m.State('STORE_DATA'):
				m.d.spi += [ self._reg_bus.w_data.eq(data_write), ]
				m.d.comb += [ self._reg_bus.w_stb.eq(1), ]

				m.next = 'IDLE'


		m.d.comb += [
			ResetSignal('spi').eq(ClockDomain('sync').rst),
			ClockSignal('spi').eq(self._clk),

			self._reg_bus.addr.eq(addr),
		]

		return m
