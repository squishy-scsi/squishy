# SPDX-License-Identifier: BSD-3-Clause

'''

'''

from enum           import IntEnum, auto, unique

from torii.hdl      import Elaboratable, Module, Signal
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

@unique
class WaitResumeState(IntEnum):
	'''  '''
	WRITE_COMMAND = auto()
	FINISH        = auto()

class SPIPSRAM(Elaboratable):
	'''

	This module primarily implements the SPI interface for the ISSI ``IS66WVS2M8ALL/BLL``/``IS67WVS2M8ALL/BLL``
	SPI PSRAM. The datasheet can be found `here <https://www.issi.com/WW/pdf/66-67WVS2M8ALL-BLL.pdf>`_.

	Parameters
	----------
	controller : SPIController
		The SPI Controller to use, typically from an ``SPIInterface`` module instance.

	write_fifo : torii.lib.fifo.AsyncFIFO | None
		The data storage FIFO for transfers to the PSRAM.

	read_fifo : torii.lib.fifo.AsyncFIFO | None
		The data storage FIFO for transfers from the PSRAM.

	Attributes
	----------
	ready : Signal, out
		The PSRAM FSM is in the IDLE state and ready to start a transaction with `start_r` or `start_w`

	start_addr : Signal[24], in
		The address to start the transaction at.

	curr_addr : Signal[24], out
		The current address of the next access of the state machine. Due to how the PSRAM wraps ever 1024
		bytes, this is auto-incremented and wrapped appropriately.

	rst_addrs : Signal, in
		Reset `curr_addr` to the address given in `start_addr`

	byte_count : Signal[24], in
		The number of bytes to be transferred in the given read or write request

	start_r : Signal, in
		Starts a read transaction of `byte_count` bytes from the device into the `read_fifo`, starting from `curr_addr`,
		setting up the address as needed for the device.

	start_w : Signal, in
		Starts a write transaction of `byte_count` bytes from the `write_fifo`, starting from `curr_addr`, setting up
		the address as needed for the device.

	done : Signal, out
		The Transaction was fully completed and the FSM is about to transition into the `IDLE` state waiting for another
		transaction to start.

	finish : Signal, in
		Signal to the FSM that our transaction is completed so it can wrap up.

	'''

	def __init__(
			self, *, controller: SPIController, write_fifo: AsyncFIFO | None = None, read_fifo: AsyncFIFO | None = None
	) -> None:

		# Make sure we actually have
		if write_fifo is None and read_fifo is None:
			raise ValueError('One or both of `write_fifo` or `read_fifo` is required to be set')

		self._spi        = controller
		self._write_fifo = write_fifo
		self._read_fifo  = read_fifo

		self.ready      = Signal()
		self.start_addr = Signal(24)
		self.curr_addr  = Signal.like(self.start_addr)
		self.rst_addrs  = Signal()
		self.byte_count = Signal(24)

		if read_fifo is not None:
			self.start_r    = Signal()
		if write_fifo is not None:
			self.start_w    = Signal()

		self.done       = Signal()
		self.finish     = Signal()

		# Read if 1, otherwise Write
		self._rnw_op = Signal()

	def elaborate(self, _: SquishyPlatformType | None) -> Module:
		m = Module()

		write_fifo = self._write_fifo
		read_fifo  = self._read_fifo
		spi        = self._spi

		xfr_step    = Signal(range(6))
		write_count = Signal(range(1025))
		read_count  = Signal(range(1025))
		byte_count  = Signal.like(self.byte_count)

		trigger_write = Signal()
		start_w       = Signal()
		trigger_read  = Signal()
		start_r       = Signal()
		wait_cntr     = Signal(range(10))
		wait_resume   = Signal(WaitResumeState)

		m.d.comb += [
			self.done.eq(0),
			spi.xfr.eq(0),
		]

		if write_fifo is not None:
			m.d.comb += [
				start_w.eq(self.start_w),
				spi.wdat.eq(write_fifo.r_data),
			]

		if read_fifo is not None:
			m.d.comb += [
				start_r.eq(self.start_r),
				read_fifo.w_data.eq(spi.rdat),
			]

		with m.FSM(name = 'psram') as psram_fsm:
			# make sure the FMS is IDLE for our ready signal
			m.d.comb += [ self.ready.eq(psram_fsm.ongoing('IDLE')), ]
			with m.State('IDLE'):
				m.d.sync += [ xfr_step.eq(0), ]

				with m.If(self.rst_addrs):
					m.d.sync += [ self.curr_addr.eq(self.start_addr), ]

				with m.If(start_w | start_r):
					m.d.sync += [
						byte_count.eq(self.byte_count),
						self._rnw_op.eq(start_r),
					]
					m.next = 'WRITE_CMD'

			with m.State('WAIT_CS_SETTLE'):
				m.d.sync += [ wait_cntr.inc(), ]

				if read_fifo is not None:
					# with m.If(self._rnw_op):
					# Ensure the read FIFO is not inhaling garbage
					m.d.sync += [ read_fifo.w_en.eq(0), ]

				with m.If(wait_cntr == 10):
					with m.Switch(wait_resume):
						with m.Case(WaitResumeState.WRITE_COMMAND):
							m.next = 'WRITE_CMD'
						with m.Case(WaitResumeState.FINISH):
							m.next = 'FINISH'

					m.d.sync += [ wait_cntr.eq(0), ]

			with m.State('WRITE_CMD'):
				with m.Switch(xfr_step):
					# Set up CS and wait so we can then wiggle the rest of the transaction
					with m.Case(0):
						m.d.sync += [
							spi.cs.eq(1),
							xfr_step.eq(1),
							wait_resume.eq(WaitResumeState.WRITE_COMMAND),
						]
						m.next = 'WAIT_CS_SETTLE'
					# Write out the command
					with m.Case(1):
						m.d.comb += [ spi.xfr.eq(1), ]
						with m.If(self._rnw_op):
							m.d.comb += [ spi.wdat.eq(SPIPSRAMCmd.READ), ]

						with m.Else():
							m.d.comb += [ spi.wdat.eq(SPIPSRAMCmd.WRITE), ]

						m.d.sync += [ xfr_step.eq(2), ]
					# Write address byte 2
					with m.Case(2):
						with m.If(spi.done):
							m.d.comb += [
								spi.xfr.eq(1),
								spi.wdat.eq(self.curr_addr[16:24]),
							]
							m.d.sync += [ xfr_step.eq(3), ]
					# Write address byte 1
					with m.Case(3):
						with m.If(spi.done):
							m.d.comb += [
								spi.xfr.eq(1),
								spi.wdat.eq(self.curr_addr[8:16]),
							]
							m.d.sync += [ xfr_step.eq(4), ]
					# Write address byte 0
					with m.Case(4):
						with m.If(spi.done):
							m.d.comb += [
								spi.xfr.eq(1),
								spi.wdat.eq(self.curr_addr[0:8]),
							]

							with m.If(self._rnw_op):
								# Because Read is wiggly we need to stall a cycle
								m.d.sync += [ xfr_step.eq(5), ]
							with m.Else():
								m.d.sync += [ xfr_step.eq(0), ]
								# Trigger the initial write for the first data byte
								if write_fifo is not None:
									with m.If(~write_fifo.r_rdy):
										m.d.sync += [ trigger_write.eq(1), ]
								m.next = 'DATA_WRITE'
					# Stall until the read address transfer cycle is over
					with m.Case(5):
						with m.If(spi.done):
							m.d.sync += [ xfr_step.eq(0), ]
							m.d.sync += [ trigger_read.eq(1), ]
							m.next = 'DATA_READ'

			if write_fifo is not None:
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
								wait_resume.eq(WaitResumeState.WRITE_COMMAND),
							]
							m.next = 'WAIT_CS_SETTLE'

						# If there is data in the FIFO
						with m.Elif(write_fifo.r_rdy):
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
								write_fifo.r_en.eq(1),
							]

							# If we are on the last byte of the transfer
							with m.If(byte_count == 1):
								m.next = 'XFR_FINISH'
						# Otherwise the FIFO is not ready, we need to wait
						with m.Else():
							m.next = 'WRITE_WAIT'

						# Reset the write trigger, so we don't loop forever
						m.d.sync += [ trigger_write.eq(0), ]

				with m.State('WRITE_WAIT'):
					with m.If(write_fifo.r_rdy):
						m.d.sync += [ trigger_write.eq(1), ]
						m.next = 'DATA_WRITE'
			else:
				# Stub out the state as a pass through to terminate the transaction
				with m.State('DATA_WRITE'):
					m.next = 'XFR_FINISH'

			if read_fifo is not None:
				with m.State('DATA_READ'):
					# If the SPI transaction is done, write the input data into the FIFO
					with m.If(spi.done):
						m.d.sync += [ read_fifo.w_en.eq(1), ]
					with m.Else():
						m.d.sync += [ read_fifo.w_en.eq(0), ]

					# If the SPI transaction was just completed OR we need to start a transaction
					with m.If(spi.done | trigger_read):
						# If we are at the PSRAM Wrap boundary
						with m.If(read_count == 1024):
							# Reset the wrap counter, and start a new transaction with the advanced
							# address in `curr_addr`.
							m.d.sync += [
								read_count.eq(0),
								spi.cs.eq(0),
								wait_resume.eq(WaitResumeState.WRITE_COMMAND),
							]
							m.next = 'WAIT_CS_SETTLE'

						# If there is space to stuff more data into the FIFOs mouth
						with m.Elif(read_fifo.w_rdy):
							# Ensure the current address is incremented as well as our wrap position
							# and drain a byte from the byte_count
							m.d.sync += [
								self.curr_addr.inc(),
								read_count.inc(),
								byte_count.dec(),
							]

							# Start a new SPI transaction with the next byte
							m.d.comb += [ spi.xfr.eq(1), ]

							# If we are on the last byte of the transfer
							with m.If(byte_count == 1):
								m.next = 'XFR_FINISH'
						# Otherwise the FIFO is not ready, we need to wait
						with m.Else():
							m.next = 'READ_WAIT'

						# Reset the write trigger, so we don't loop forever
						m.d.sync += [ trigger_read.eq(0), ]

				with m.State('READ_WAIT'):
					m.d.sync += [ read_fifo.w_en.eq(0), ]
					with m.If(read_fifo.w_rdy):
						m.d.sync += [ trigger_read.eq(1), ]
						m.next = 'DATA_READ'
			else:
				# Stub out the state as a pass through to terminate the transaction
				with m.State('DATA_READ'):
					m.next = 'XFR_FINISH'

			with m.State('XFR_FINISH'):
				# Wait for the last SPI transfer to complete
				with m.If(spi.done):
					m.d.sync += [
						read_count.eq(0),
						write_count.eq(0),
						spi.cs.eq(0),
						wait_resume.eq(WaitResumeState.FINISH),
					]
					if read_fifo is not None:
						m.d.sync += [ read_fifo.w_en.eq(self._rnw_op), ]

					m.next = 'WAIT_CS_SETTLE'
				if read_fifo is not None:
					with m.Else():
						m.d.sync += [ read_fifo.w_en.eq(0), ]

			with m.State('FINISH'):
				if read_fifo is not None:
					m.d.sync += [ read_fifo.w_en.eq(0), ]
				m.d.comb += [ self.done.eq(1), ]

				with m.If(self.finish):
					m.next = 'IDLE'

		return m
