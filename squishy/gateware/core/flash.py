# SPDX-License-Identifier: BSD-3-Clause
from enum           import (
	IntEnum, auto, unique
)
from torii          import (
	Elaboratable, Module, Signal
)
from torii.lib.fifo import AsyncFIFO

from ...core.flash  import FlashGeometry

from .spi           import SPIInterface

__doc__ = '''\

'''

__all__ = (
	'SPIFlash',
	'SPIFlashOp'
)

@unique
class SPIFlashOp(IntEnum):
	''' The current SPI Flash Operation being completed '''

	NONE  = auto()
	''' No Operation '''

	ERASE = auto()
	''' Sector Erase '''

	WRITE = auto()
	''' Page Write '''

	READ  = auto()
	''' Page Read '''

@unique
class SPIFlashCmd(IntEnum):
	'''SPI Flash Command Opcodes '''
	PAGE_PROGRAM   = 0x02
	READ_STATUS    = 0x05
	WRITE_ENABLE   = 0x06
	RELEASE_PWRDWN = 0xAB

class SPIFlash(Elaboratable):
	def __init__(self, *, flash_resource: str, flash_geometry: FlashGeometry, fifo: AsyncFIFO, erase_cmd: int = None):
		self._flash_resource = flash_resource
		self.geometry        = flash_geometry
		self._fifo           = fifo
		self._spi            = SPIInterface(resource_name = self._flash_resource)
		self._erase_cmd      = erase_cmd


		self.ready      = Signal()
		self.start      = Signal()
		self.done       = Signal()
		self.finish     = Signal()
		self.resetAddrs = Signal()
		self.startAddr  = Signal(self.geometry.addr_width)
		self.endAddr    = Signal(self.geometry.addr_width)
		self.readAddr   = Signal(self.geometry.addr_width)
		self.eraseAddr  = Signal(self.geometry.addr_width)
		self.writeAddr  = Signal(self.geometry.addr_width)
		self.byteCount  = Signal(self.geometry.addr_width)

	def elaborate(self, platform) -> Module:
		m = Module()

		if hasattr(platform, 'flash'):
			erase_cmd = platform.flash['commands']['erase']
		else:
			erase_cmd = self._erase_cmd

		m.submodules.spi = self._spi

		fifo = self._fifo

		op = Signal(SPIFlashOp, reset = SPIFlashOp.NONE)

		resetStep       = Signal(range(2))
		enableStep      = Signal(range(3))
		eraseCmdStep    = Signal(range(6))
		eraseWaitStep   = Signal(range(4))
		writeCmdStep    = Signal(range(5))
		writeFinishStep = Signal(range(2))
		writeWaitStep   = Signal(range(4))
		writeTrigger    = Signal()
		writeCount      = Signal(range(self.geometry.page_size + 1))
		byteCount       = Signal.like(self.byteCount)


		m.d.comb += [
			self.ready.eq(0),
			self.done.eq(0),
			self._spi.xfr.eq(0),
			self._spi.wdat.eq(fifo.r_data),
		]

		# TODO: Add `READ` support
		with m.FSM(name = 'flash'):
			with m.State('RST'):
				with m.Switch(resetStep):
					with m.Case(0):
						m.d.comb += [
							self._spi.xfr.eq(1),
							self._spi.wdat.eq(SPIFlashCmd.RELEASE_PWRDWN),
						]
						m.d.sync += [
							self._spi.cs.eq(1),
							resetStep.eq(1),
						]
					with m.Case(1):
						with m.If(self._spi.done):
							m.d.comb += self.ready.eq(1)
							m.d.sync += [
								self._spi.cs.eq(0),
								enableStep.eq(0),
							]
							m.next = 'IDLE'
			with m.State('IDLE'):
				m.d.sync += [
					enableStep.eq(0),
					eraseCmdStep.eq(0),
					eraseWaitStep.eq(0),
					writeCmdStep.eq(0),
					writeFinishStep.eq(0),
					writeWaitStep.eq(0),
				]
				with m.If(self.resetAddrs):
					m.d.sync += [
						self.readAddr.eq(self.startAddr),
						self.eraseAddr.eq(self.startAddr),
						self.writeAddr.eq(self.startAddr),
					]
				with m.If(self.start):
					m.d.sync += [
						op.eq(SPIFlashOp.ERASE),
						byteCount.eq(self.byteCount),
					]
					m.next = 'WRITE_ENABLE'
			with m.State('WRITE_ENABLE'):
				with m.Switch(enableStep):
					with m.Case(0):
						m.d.comb += [
							self._spi.xfr.eq(1),
							self._spi.wdat.eq(SPIFlashCmd.WRITE_ENABLE),
						]
						m.d.sync += [
							self._spi.cs.eq(1),
							enableStep.eq(1),
						]
					with m.Case(1):
						with m.If(self._spi.done):
							m.d.sync += [
								self._spi.cs.eq(0),
								enableStep.eq(2),
							]
					with m.Case(2):
						m.d.sync += enableStep.eq(0)
						with m.If(op == SPIFlashOp.ERASE):
							m.next = 'CMD_ERASE'
						with m.Else():
							m.next = 'CMD_WRITE'
			with m.State('CMD_ERASE'):
				with m.Switch(eraseCmdStep):
					with m.Case(0):
						m.d.comb += [
							self._spi.xfr.eq(1),
							self._spi.wdat.eq(erase_cmd),
						]
						m.d.sync += [
							self._spi.cs.eq(1),
							eraseCmdStep.eq(1),
						]
					with m.Case(1):
						with m.If(self._spi.done):
							m.d.comb += [
								self._spi.xfr.eq(1),
								self._spi.wdat.eq(self.eraseAddr[16:24]),
							]
							m.d.sync += eraseCmdStep.eq(2)
					with m.Case(2):
						with m.If(self._spi.done):
							m.d.comb += [
								self._spi.xfr.eq(1),
								self._spi.wdat.eq(self.eraseAddr[8:16]),
							]
							m.d.sync += eraseCmdStep.eq(3)
					with m.Case(3):
						with m.If(self._spi.done):
							m.d.comb += [
								self._spi.xfr.eq(1),
								self._spi.wdat.eq(self.eraseAddr[0:8]),
							]
							m.d.sync += eraseCmdStep.eq(4)
					with m.Case(4):
						with m.If(self._spi.done):
							m.d.sync += [
								self._spi.cs.eq(0),
								eraseCmdStep.eq(5),
							]
					with m.Case(5):
						m.d.sync += [
							self.eraseAddr.eq(self.eraseAddr + self.geometry.erase_size),
							eraseCmdStep.eq(0),
						]
						m.next = 'ERASE_WAIT'
			with m.State('ERASE_WAIT'):
				with m.Switch(eraseWaitStep):
					with m.Case(0):
						m.d.comb += [
							self._spi.xfr.eq(1),
							self._spi.wdat.eq(SPIFlashCmd.READ_STATUS),
						]
						m.d.sync += [
							self._spi.cs.eq(1),
							eraseWaitStep.eq(1),
						]
					with m.Case(1):
						with m.If(self._spi.done):
							m.d.comb += [
								self._spi.xfr.eq(1),
								self._spi.wdat.eq(0),
							]
							m.d.sync += eraseWaitStep.eq(2)
					with m.Case(2):
						with m.If(self._spi.done):
							m.d.sync += [
								self._spi.cs.eq(0),
								eraseWaitStep.eq(3),
							]
					with m.Case(3):
						m.d.sync += eraseWaitStep.eq(0)
						with m.If(~self._spi.rdat[0]):
							with m.If((self.writeAddr + byteCount) <= self.endAddr):
								m.d.sync += op.eq(SPIFlashOp.WRITE)
							m.next = 'WRITE_ENABLE'
			with m.State('CMD_WRITE'):
				with m.Switch(writeCmdStep):
					with m.Case(0):
						m.d.comb += [
							self._spi.xfr.eq(1),
							self._spi.wdat.eq(SPIFlashCmd.PAGE_PROGRAM),
						]
						m.d.sync += [
							self._spi.cs.eq(1),
							writeCmdStep.eq(1),
						]
					with m.Case(1):
						with m.If(self._spi.done):
							m.d.comb += [
								self._spi.xfr.eq(1),
								self._spi.wdat.eq(self.writeAddr[16:24]),
							]
							m.d.sync += writeCmdStep.eq(2)
					with m.Case(2):
						with m.If(self._spi.done):
							m.d.comb += [
								self._spi.xfr.eq(1),
								self._spi.wdat.eq(self.writeAddr[8:16]),
							]
							m.d.sync += writeCmdStep.eq(3)
					with m.Case(3):
						with m.If(self._spi.done):
							m.d.comb += [
								self._spi.xfr.eq(1),
								self._spi.wdat.eq(self.writeAddr[0:8]),
							]
							m.d.sync += writeCmdStep.eq(4)
					with m.Case(4):
						with m.If(self._spi.done):
							m.d.sync += [
								writeTrigger.eq(1),
								writeCmdStep.eq(0)
							]
							m.next = 'WRITE'
			with m.State('WRITE'):
				with m.If(self._spi.done | writeTrigger):
					m.d.sync += writeTrigger.eq(0)
					with m.If(fifo.r_rdy):
						m.d.comb += [
							self._spi.xfr.eq(1),
							fifo.r_en.eq(1),
						]
						m.d.sync += [
							writeCount.eq(writeCount + 1),
							byteCount.eq(byteCount - 1),
						]
						with m.If((writeCount == self.geometry.page_size - 1) | (byteCount == 1)):
							m.next = 'WRITE_FINISH'
					with m.Else():
						m.next = 'DATA_WAIT'
			with m.State('DATA_WAIT'):
				with m.If(fifo.r_rdy):
					m.d.sync += writeTrigger.eq(1)
					m.next = 'WRITE'
			with m.State('WRITE_FINISH'):
				with m.Switch(writeFinishStep):
					with m.Case(0):
						with m.If(self._spi.done):
							m.d.sync += [
								self._spi.cs.eq(0),
								writeFinishStep.eq(1),
							]
					with m.Case(1):
						m.d.sync += [
							self.writeAddr.eq(self.writeAddr + writeCount),
							writeCount.eq(0),
							writeFinishStep.eq(0),
						]
						m.next = 'WRITE_WAIT'
			with m.State('WRITE_WAIT'):
				with m.Switch(writeWaitStep):
					with m.Case(0):
						m.d.comb += [
							self._spi.xfr.eq(1),
							self._spi.wdat.eq(SPIFlashCmd.READ_STATUS),
						]
						m.d.sync += [
							self._spi.cs.eq(1),
							writeWaitStep.eq(1),
						]
					with m.Case(1):
						with m.If(self._spi.done):
							m.d.comb += [
								self._spi.xfr.eq(1),
								self._spi.wdat.eq(0),
							]
							m.d.sync += writeWaitStep.eq(2)
					with m.Case(2):
						with m.If(self._spi.done):
							m.d.sync += [
								self._spi.cs.eq(0),
								writeWaitStep.eq(3),
							]
					with m.Case(3):
						m.d.sync += writeWaitStep.eq(0)
						with m.If(~self._spi.rdat[0]):
							with m.If(byteCount):
								m.next = 'WRITE_ENABLE'
							with m.Else():
								m.d.sync += op.eq(SPIFlashOp.NONE)
								m.next = 'FINISH'
			with m.State('FINISH'):
				m.d.comb += self.done.eq(1)
				with m.If(self.finish):
					m.next = 'IDLE'
		return m
