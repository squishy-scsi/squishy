# SPDX-License-Identifier: BSD-3-Clause

'''
This module contains the Squishy supervisor interface CSR map and register definitions.

'''
from torii                 import Module, Signal, Record
from torii.hdl.rec         import Direction
from torii.lib.soc.csr.bus import Multiplexer, Element

from ..platform            import SquishyPlatformType


__all__ = (
	'SupervisorCSRMap',
	'CtrlRegister',
	'StatusRegister',
	'SlotRegister',
	'IRQRegister',
)

class CtrlRegister(Record):
	'''
	Squishy bootloader control register layout
	'''

	write_done: Signal[1, Direction.FANOUT]
	''' Supervisor is done with the slot storage write  '''

	irq_ack: Signal[1, Direction.FANOUT]
	''' Supervisor actioned on our IRQ '''

class StatusRegister(Record):
	'''
	Squishy bootloader status register layout
	'''

	_rsvd: Signal[8, Direction.FANOUT]
	''' TBD '''

class SlotRegister(Record):
	'''
	Squishy slot register layout
	'''

	boot: Signal[4, Direction.FANOUT]
	''' The slot we wish to be booted into '''

	dest: Signal[4, Direction.FANOUT]
	''' The slot to write DFU payload data into '''

class IRQRegister(Record):
	'''
	Squishy supervisor IRQ reason register layout
	'''

	want_dfu: Signal[1, Direction.FANOUT]
	''' We are in an applet, and want to be loaded with bootloader gateware '''

	write_slot: Signal[1, Direction.FANOUT]
	''' We want the supervisor to write the contents of PSRAM into the target slot '''

	boot: Signal[1, Direction.FANOUT]
	''' We want the supervisor to boot us from the given slot '''


class SupervisorCSRMap(Multiplexer):
	'''
	Squishy rev2 Supervisor CSR Map

	This module represents a CSR map interface that is exposed to the supervisor over SPI. It consists
	of a small handful of registers.


	There are 4 possible registers in this map:
	  * CTRL/Status - bootloader control/status register
	  * Slots - Dest/Boot slot register
	  * TXlen - bootloader DFU payload size in PSRAM
	  * IRQ - The reason the `SU_IRQ` signal was raised


	Parameters
	----------
	boot : bool
		If this module is being included as part of the bootloader gateware. This alters the CSR map.

	name : str | None
		The CSR Map name, if none provided it will be automatically generated.


	Attributes
	----------
	txlen : In, Signal(16)
		DFU Payload length register value

	ctrl : Out, CtrlRegister
		Write half of the supervisor CSR register, written to by the supervisor.

	status : In, StatusRegister
		Read half of the supervisor CSR register, read from by the supervisor.

	slot : In, SlotRegister
		The boot/dest slot register. Used to set the requested boot slot and/or the destination flash slot for
		the DFU payload.

	irq_reason : In, IRQRegister
		IRQ Reason register. Used to set the reason the `~SU_IRQ` interrupt was triggered.

	'''

	def __init__(self, *, boot: bool = False, name: str | None = None) -> None:

		self._data_width = 8

		super().__init__(addr_width = 3, data_width = self._data_width, name = name)

		self._ctrl_sts   = Element(self._data_width,     Element.Access.RW, name = 'ctrl/status')
		self._slots      = Element(self._data_width,     Element.Access.RW, name = 'slots'      )
		self._txlen      = Element(self._data_width * 2, Element.Access.R,  name = 'txlen'      )
		self._irq_reason = Element(self._data_width,     Element.Access.R,  name = 'IRQ'        )

		self.add(self._ctrl_sts,   addr = 0x0)
		self.add(self._slots,      addr = 0x1)
		self.add(self._txlen,      addr = 0x2)
		self.add(self._irq_reason, addr = 0x4)

		self.txlen     = Signal(16)

		self.ctrl       = CtrlRegister()
		self.status     = StatusRegister()
		self.slot       = SlotRegister()
		self.irq_reason = IRQRegister()


	def elaborate(self, platform: SquishyPlatformType | None) -> Module:
		m = super().elaborate(platform)

		m.d.comb += [
			self._txlen.r_data.eq(self.txlen),
			self._slots.r_data[0:4].eq(self.slot.dest),
			self._slots.r_data[4:8].eq(self.slot.boot),
			self._ctrl_sts.r_data.eq(self.status),
			self._irq_reason.r_data.eq(self.irq_reason),
		]

		with m.If(self._ctrl_sts.w_stb):
			m.d.sync += [ self.ctrl.eq(self._ctrl_sts.w_data), ]

		return m
