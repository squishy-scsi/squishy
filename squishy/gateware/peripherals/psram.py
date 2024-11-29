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
		self.start_r    = Signal()
		self.start_w    = Signal()
		self.rst_addrs  = Signal()
		self.start_addr = Signal(24)
		self.curr_addr  = Signal.like(self.start_addr)
		self.byte_count = Signal(24)

		# Read if 1, otherwise Write
		self._rnw_op = Signal()


	def elaborate(self, platform: SquishyPlatformType | None) -> Module:
		m = Module()

		fifo = self._fifo
		spi  = self._spi

		xfr_step    = Signal(range(5))
		write_count = Signal(range(1025))
		byte_count  = Signal.like(self.byte_count)

		trigger_write = Signal()


		m.d.comb += [
			self.ready.eq(0),
			self.done.eq(0),
			spi.xfr.eq(0),
			spi.wdat.eq(fifo.r_data),
		]

		with m.FSM(name = 'psram'):
			with m.State('IDLE'):
				m.d.sync += [ xfr_step.eq(0), ]

				with m.If(self.rst_addrs):
					m.d.sync += [ self.curr_addr.eq(self.start_addr), ]

				with m.If(self.start_w | self.start_r):
					m.d.sync += [
						byte_count.eq(self.byte_count),
						self._rnw_op.eq(self.start_r),
					]
					m.next = 'WRITE_CMD'

			with m.State('WRITE_CMD'):
				with m.Switch(xfr_step):
					# Write out the command
					with m.Case(0):
						m.d.comb += [ spi.xfr.eq(1), ]

						with m.If(self._rnw_op):
							m.d.comb += [ spi.wdat.eq(SPIPSRAMCmd.READ), ]
						with m.Else():
							m.d.comb += [ spi.wdat.eq(SPIPSRAMCmd.WRITE), ]

						m.d.sync += [
							spi.cs.eq(1),
							xfr_step.eq(1)
						]
					# Write address byte 2
					with m.Case(1):
						with m.If(spi.done):
							m.d.comb += [
								spi.xfr.eq(1),
								spi.wdat.eq(self.curr_addr[16:24]),
							]
							m.d.sync += [ xfr_step.eq(2), ]
					# Write address byte 1
					with m.Case(2):
						with m.If(spi.done):
							m.d.comb += [
								spi.xfr.eq(1),
								spi.wdat.eq(self.curr_addr[8:16]),
							]
							m.d.sync += [ xfr_step.eq(3), ]
					# Write address byte 0
					with m.Case(3):
						with m.If(spi.done):
							m.d.comb += [
								spi.xfr.eq(1),
								spi.wdat.eq(self.curr_addr[0:8]),
							]
							m.d.sync += [ xfr_step.eq(0), ]

							with m.If(self._rnw_op):
								m.next = 'DATA_READ'
							with m.Else():
								# Trigger the initial write for the first data byte
								m.d.sync += [ trigger_write.eq(1), ]
								m.next = 'DATA_WRITE'

			with m.State('WRITE_WAIT'):
				with m.If(fifo.r_rdy):
					m.d.sync += [ trigger_write.eq(1), ]
					m.next = 'DATA_WRITE'

			with m.State('DATA_WRITE'):
				# If the SPI transaction was just completed OR we need to start a transaction
				with m.If(spi.done | trigger_write):
					# If we are at the PSRAM Wrap boundary
					with m.If(write_count == 1024):
						# Reset the wrap counter, and start a new transaction with the advanced
						# address in `curr_addr`.
						m.d.sync += [
							write_count.eq(0),
							spi.cs.eq(0),
						]
						m.next = 'WRITE_CMD'
					# If there is data in the FIFO
					with m.Elif(fifo.r_rdy):
						# Ensure the current address is incremented as well as our wrap position
						# and drain a byte from the byte_count
						m.d.sync += [
							self.curr_addr.inc(),
							write_count.inc(),
							byte_count.dec(),
						]

						# Start a new SPI transaction with the next byte
						m.d.comb += [
							spi.xfr.eq(1),
							fifo.r_en.eq(1),
						]

						# If we are on the last byte of the transfer
						with m.If(byte_count == 1):
							m.next = 'XFR_FINISH'
					# Otherwise the FIFO is not ready, we need to wait
					with m.Else():
						m.next = 'WRITE_WAIT'

					# Reset the write trigger, so we don't loop forever
					m.d.sync += [ trigger_write.eq(0), ]


			with m.State('DATA_READ'):
				pass

			with m.State('XFR_FINISH'):
				# Wait for the last SPI transfer to complete
				with m.If(spi.done):
					m.d.sync += [
						write_count.eq(0),
						spi.cs.eq(0),
					]

					m.next = 'FINISH'

			with m.State('FINISH'):
				m.d.comb += [ self.done.eq(1), ]

				with m.If(self.finish):
					m.next = 'IDLE'


		return m
