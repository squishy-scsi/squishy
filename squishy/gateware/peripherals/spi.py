# SPDX-License-Identifier: BSD-3-Clause

'''

'''

from enum              import Flag, IntEnum, auto, unique

from torii.build       import Subsignal
from torii.hdl         import Cat, ClockDomain, ClockSignal, Elaboratable, Module, ResetSignal, Signal
from torii.hdl.ast     import Fell, Rose
from torii.lib.cdc     import FFSynchronizer
from torii.lib.soc.csr import Multiplexer

from ..platform        import SquishyPlatformType

__all__ = (
	'SPIInterface',
	'SPIInterfaceMode',
	'SPIController',
	'SPIPeripheral',

	'SPICPOL',
	'SPICPHA',
)

@unique
class SPIInterfaceMode(Flag):
	''' The operating mode for ``SPIInterface`` '''
	CONTROLLER = auto()
	''' Enable the ``SPIController`` inside ``SPIInterface`` '''
	PERIPHERAL = auto()
	''' Enable the ``SPIPeripheral`` inside ``SPIInterface`` '''
	BOTH       = CONTROLLER | PERIPHERAL
	''' Enable both the ``SPIController`` and the ``SPIPeripheral`` inside ``SPIInterface`` '''

@unique
class SPICPOL(IntEnum):
	''' The state of the electrical idle for the SPI controller clock '''
	LOW  = 0
	''' SPI Controller clock is electrical idle high '''
	HIGH = 1
	''' SPI Controller clock is electrical idle low '''

@unique
class SPICPHA(IntEnum):
	''' The phase of the SPI controller clock '''
	RISING = 0
	''' Data is sampled on the rising edge '''
	FALLING = 1
	''' Data is sampled on the falling edge '''

class SPIInterface(Elaboratable):
	'''
	An SPI interface that can act as both an SPI controller and/or an SPI peripheral.

	Parameters
	----------
	clk : Subsignal, inout
		The SPI bus clock line.

	cipo : Subsignal, inout
		The SPI bus CIPO line.

	copi : Subsignal, inout
		The SPI bus COPI line.

	cs_peripheral : Subsignal, in
		The chip-select signal to route to the SPIPeripheral

	cs_controller : Subsignal, out
		The chip-select signal to route out from the SPIController

	mode : SPIInterfaceMode
		The mode this SPI interface represents, either a SPI Controller, a SPI Peripheral, or both.

	cpol : SPICPOL
		The SPI bus clock electrical idle. (default: HIGH)

	cpha : SPICPHA
		The SPI bus clock phase. (default: RISING)

	reg_map : torii.lib.soc.csr.Multiplexer | None
		The CSR register map to feed the ``SPIPeripheral`` if mode is either ``PERIPHERAL`` or ``BOTH``

	Attributes
	----------
	active_mode: Signal
		This signal is only present if ``mode`` is ``BOTH``. It controls the output-enables for the COPI,
		CIPO, and CLK lines depending if it is high, for the controller, or low, for the peripheral.


	controller : SPIController
		The ``SPIController`` module if ``mode`` is ``CONTROLLER`` or ``BOTH``.

	peripheral : SPIPeripheral
		The ``SPIPeripheral`` module if ``mode`` is ``PERIPHERAL`` or ``BOTH``.

	'''

	def __init__(
		self, *,
		clk: Subsignal, cipo: Subsignal, copi: Subsignal, cs_peripheral: Subsignal, cs_controller: Subsignal,
		mode: SPIInterfaceMode = SPIInterfaceMode.BOTH, cpol: SPICPOL = SPICPOL.HIGH, cpha: SPICPHA = SPICPHA.RISING,
		reg_map: Multiplexer | None = None
	) -> None:

		# Subsignals for SPI Bus from SPI Resource
		self._clk  = clk
		self._cipo = cipo
		self._copi = copi
		self._cs_peripheral = cs_peripheral
		self._cs_controller = cs_controller

		self._mode = mode
		self._cpol = cpol
		self._cpha = cpha

		if self._mode == SPIInterfaceMode.BOTH:
			self.active_mode = Signal(decoder = lambda i: 'ctrl' if i == 1 else 'perh')

		if self._mode & SPIInterfaceMode.CONTROLLER:
			self.controller = SPIController(
				clk = self._clk.o, cipo = self._cipo.i, copi = self._copi.o, cs = self._cs_controller.o,
				cpol = self._cpol, cpha = self._cpha
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
				self._cipo.oe.eq(~self.active_mode & self._cs_peripheral.i),
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

	cpol : SPICPOL
		The SPI bus clock electrical idle. (default: HIGH)

	cpha : SPICPHA
		The SPI bus clock phase. (default: RISING)

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

	def __init__(
		self, *, clk: Signal, cipo: Signal, copi: Signal, cs: Signal, cpol: SPICPOL = SPICPOL.HIGH,
		cpha: SPICPHA = SPICPHA.RISING
	) -> None:

		self._clk  = clk
		self._cipo = cipo
		self._copi = copi
		self._cs   = cs

		self._cpol = cpol
		self._cpha = cpha

		self.cs   = Signal()
		self.xfr  = Signal()
		self.done = Signal()
		self.wdat = Signal(8)
		self.rdat = Signal(8)

	def elaborate(self, _: SquishyPlatformType | None) -> Module:
		m = Module()

		bit   = Signal(range(8))
		clk   = Signal(reset = int(self._cpol), name = 'spi_clk')
		xfrph = Signal()

		copi = self._copi
		cipo = self._cipo

		d_in  = Signal.like(self.rdat)
		d_out = Signal.like(self.wdat)

		m.d.comb += self.done.eq(0)

		with m.FSM(name = 'spi_controller'):
			with m.State('IDLE'):
				m.d.sync += clk.eq(int(self._cpol))
				with m.If(self.xfr):
					m.d.sync += d_out.eq(self.wdat)
					m.next = 'XFR'
			with m.State('XFR'):
				with m.If(xfrph == 0):
					m.d.sync += [
						clk.eq(0 if self._cpha == SPICPHA.RISING else 1),
						bit.eq(bit + 1),
						copi.eq(d_out[7]),
						xfrph.eq(1),
					]
				with m.Else():
					m.d.sync += [
						clk.eq(1 if self._cpha == SPICPHA.RISING else 0),
						d_out.eq(d_out.shift_left(1)),
						d_in.eq(Cat(cipo, d_in[:-1])),
						xfrph.eq(0),
					]
					with m.If(bit == 0):
						m.next = 'DONE'
			with m.State('DONE'):
				m.d.comb += self.done.eq(1)
				m.d.sync += [ self.rdat.eq(d_in), clk.eq(int(self._cpol)) ]

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

	A SPI peripheral that exposes a set of registers to the SPI bus.

	Parameters
	----------

	clk : Signal, in
		The incoming SPI Bus clock signal

	cipo : Signal, out
		The output from the SPI peripheral to the bus.

	copi : Signal, in
		The input from the controller on the SPI bus to the peripheral.

	cs : Signal, in
		The chip-select signal from the SPI bus to indicate this peripheral should be active.

	reg_map : torii.lib.soc.csr.Multiplexer
		The CSR register map to expose to the SPI bus.

	'''

	def __init__(
		self, *, clk: Signal, cipo: Signal, copi: Signal, cs: Signal, reg_map: Multiplexer | None = None
	) -> None:
		self._clk  = clk
		self._cipo = cipo
		self._copi = copi
		self._cs   = cs

		self._reg_bus = reg_map.bus

	def elaborate(self, _: SquishyPlatformType | None) -> Module:
		m = Module()

		m.domains.spi = ClockDomain()

		clk  = Signal.like(self._clk,  name = 'spi_pclk' )
		cs   = Signal.like(self._cs,   name = 'spi_pcs'  )
		copi = Signal.like(self._copi, name = 'spi_pcopi')
		cipo = self._cipo

		m.submodules.clk_ff  = FFSynchronizer(self._clk,   clk, o_domain = 'sync')
		m.submodules.cs_ff   = FFSynchronizer(self._cs,     cs, o_domain = 'sync')
		m.submodules.copi_ff = FFSynchronizer(self._copi, copi, o_domain = 'sync')

		addr       = Signal(self._reg_bus.addr_width)
		addr_cntr  = Signal(range(self._reg_bus.addr_width))
		wait_cntr  = Signal(range(8))
		data_read  = Signal(self._reg_bus.data_width) # Out to the SPI Bus
		data_prep  = Signal()
		data_write = Signal.like(data_read)           # In from the SPI Bus
		data_cntr  = Signal(range(data_write.width))

		with m.FSM(name = 'spi_peripheral'):
			with m.State('IDLE'):
				with m.If(cs):
					m.d.sync += [
						addr.eq(0),
						addr_cntr.eq(0),
					]
					m.next = 'READ_ADDR'

			with m.State('READ_ADDR'):
				with m.If(~cs):
					m.next = 'IDLE'
				with m.Elif(Rose(clk)):
					m.d.sync += [
						addr_cntr.eq(addr_cntr + 1),
						addr.eq(Cat(addr[1:], copi)),
					]

					with m.If(addr_cntr == (addr.width - 1)):
						if (addr.width & 0b111):
							m.d.sync += [ wait_cntr.eq(0), ]
							m.next = 'WAIT_DATA'
						else:
							m.next = 'PREPARE_DATA'

			with m.State('WAIT_DATA'):
				with m.If(~cs):
					m.next = 'IDLE'
				with m.Elif(Rose(clk)):
					m.d.sync += [ wait_cntr.eq(wait_cntr + 1), ]
					with m.If(wait_cntr == 7 - (addr.width & 0b111)):
						m.next = 'PREPARE_DATA'

			with m.State('PREPARE_DATA'):
				with m.If(~cs):
					m.next = 'IDLE'
				with m.Elif(Fell(clk)):
					m.d.comb += [ self._reg_bus.r_stb.eq(1), ]
					m.d.sync += [ data_prep.eq(1), ]
					m.next = 'XFR_DATA'

			with m.State('XFR_DATA'):
				with m.If(data_prep):
					m.d.sync += [
						data_read.eq(self._reg_bus.r_data),
						data_prep.eq(0),
					]
				with m.If(Rose(clk)):
					m.d.sync += [
						# Wiggle in the `data_write` value
						data_write.eq(Cat(data_write[1:], copi)),
						# Wiggle out the `data_read` value
						cipo.eq(data_read.bit_select(data_cntr, 1)),
					]
					with m.If(~cs):
						m.next = 'IDLE'

				with m.Elif(Fell(clk)):
					m.d.sync += [
						data_cntr.eq(data_cntr + 1),
					]

					with m.If(data_cntr == (data_write.width - 1)):
						m.next = 'STORE_DATA'
					with m.Elif(~cs):
						m.next = 'IDLE'

			with m.State('STORE_DATA'):
				m.d.comb += [
					self._reg_bus.w_data.eq(data_write),
					self._reg_bus.w_stb.eq(1),
				]

				with m.If(cs):
					m.d.sync += [
						addr.eq(addr + 1),
						data_cntr.eq(0),
						data_prep.eq(1),
					]
					m.next = 'XFR_READY'

				with m.Else():
					m.next = 'IDLE'

			with m.State('XFR_READY'):
				m.d.comb += [ self._reg_bus.r_stb.eq(1), ]
				m.next = 'XFR_DATA'

		m.d.comb += [
			ResetSignal('spi').eq(ClockDomain('sync').rst),
			ClockSignal('spi').eq(self._clk),

			self._reg_bus.addr.eq(addr),
		]

		return m
