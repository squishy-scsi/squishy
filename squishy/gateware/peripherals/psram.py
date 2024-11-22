# SPDX-License-Identifier: BSD-3-Clause

'''

'''

from enum           import IntEnum, unique, auto

from torii          import Elaboratable, Module, Signal
from torii.lib.fifo import AsyncFIFO


from ..platform     import SquishyPlatformType
from .spi           import SPIController

@unique
class PSRAMOp(IntEnum):
	NONE = auto()

@unique
class SPIPSRAMCmd(IntEnum):
	''' SPI PSRAM Command Opcodes '''
	READ          = 0x03
	WRITE         = 0x02
	FAST_READ     = 0x0B
	RESET_ENABLE  = 0x66
	RESET         = 0x99
	READ_ID       = 0x9F
	SET_BURST_LEN = 0xC0

class SPIPSRAM(Elaboratable):
	'''

	This module primarily implements the SPI interface for the ISSI ``IS66WVS2M8ALL/BLL``/``IS67WVS2M8ALL/BLL``
	SPI PSRAM. The datasheet can be found `here <https://www.issi.com/WW/pdf/66-67WVS2M8ALL-BLL.pdf>`_.

	Parameters
	----------
	controller : SPIController
		The SPI Controller to use, typically from an ``SPIInterface`` module instance.

	fifo : torii.lib.fifo.AsyncFIFO
		The data storage FIFO for transfers to/from the PSRAM.

	'''

	def __init__(self, *, controller: SPIController, fifo: AsyncFIFO) -> None:
		self._spi  = controller
		self._fifo = fifo

		self.ready      = Signal()
		self.done       = Signal()
		self.finish     = Signal()
		self.start      = Signal()
		self.rst_addrs  = Signal()
		self.start_addr = Signal(24)
		self.curr_addr  = Signal.like(self.start_addr)
		self.byte_count = Signal(24)


	def elaborate(self, platform: SquishyPlatformType | None) -> Module:
		m = Module()

		fifo = self._fifo
		spi  = self._spi

		xfr_step    = Signal(range(5))
		write_count = Signal(range(1024))
		byte_count  = Signal.like(self.byte_count)

		m.d.comb += [
			self.ready.eq(0),
			self.done.eq(0),
			spi.xfr.eq(0),
			spi.wdat.eq(fifo.r_data),
		]

		with m.FSM(name = 'psram'):
			with m.State('RST'):
				m.next = 'IDLE'
			with m.State('IDLE'):
				m.d.sync += [ xfr_step.eq(0), ]

				with m.If(self.rst_addrs):
					m.d.sync += [ self.curr_addr.eq(self.start_addr), ]

				with m.If(self.start):
					m.d.sync += [ byte_count.eq(self.byte_count), ]
					m.next = 'CMD_WRITE'

			with m.State('CMD_WRITE'):
				with m.Switch(xfr_step):
					with m.Case(0):
						m.d.comb += [
							spi.xfr.eq(1),
							spi.wdat.eq(SPIPSRAMCmd.WRITE),
						]
						m.d.sync += [
							spi.cs.eq(1),
							xfr_step.eq(1)
						]
					with m.Case(1):
						with m.If(spi.done):
							m.d.comb += [
								spi.xfr.eq(1),
								spi.wdat.eq(self.curr_addr[16:24]),
							]
							m.d.sync += [ xfr_step.eq(2), ]
					with m.Case(2):
						with m.If(spi.done):
							m.d.comb += [
								spi.xfr.eq(1),
								spi.wdat.eq(self.curr_addr[8:16]),
							]
							m.d.sync += [ xfr_step.eq(3), ]
					with m.Case(3):
						with m.If(spi.done):
							m.d.comb += [
								spi.xfr.eq(1),
								spi.wdat.eq(self.curr_addr[0:8]),
							]
							m.d.sync += [ xfr_step.eq(0), ]
							m.next = 'DATA_WRITE'

			with m.State('WRITE_WAIT'):
				with m.If(fifo.r_rdy):
					m.next = 'CMD_WRITE'
			with m.State('DATA_WRITE'):
				with m.If(write_count == 1024):
					m.d.sync += [
						write_count.eq(0),
						self.curr_addr.eq(self.curr_addr + 1024),
						spi.cs.eq(0),
					]
					m.next = 'WRITE_WAIT'

				with m.If(spi.done):
					with m.If(fifo.r_rdy):
						m.d.comb += [
							spi.xfr.eq(1),
							fifo.r_en.eq(1),
						]


			with m.State('FINISH'):
				m.d.comb += [ self.done.eq(1), ]
				with m.If(self.finish):
					m.next = 'IDLE'


		return m
