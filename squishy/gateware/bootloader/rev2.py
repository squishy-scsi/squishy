# SPDX-License-Identifier: BSD-3-Clause

'''


Squishy Supervisor Bootloader Protocol:

	If we are in an applet and wish to drop into the bootloader:

		1. FPGA raises `~SU_IRQ` with the IRQ register value `DFU` set to 1
		2. Supervisor resets the FPGA configuration and loads the bootloader bitstream
		3. Supervisor then waits for the next IRQ event
		4. Supervisor then checks the IRQ register to make sure it is `in_boot`

	When the FPGA enters bootloader:

		0. FPGA waits for a DFU upload, and if done stuffs it into the PSRAM
			a. FPGA sticks the destination slot for the DFU payload into the `dest_slot` half of the `slots` register
			b. FPGA writes the DFU payload size into the `txlen` register

		1. FPGA sets the IRQ Reason to `in_boot`*
		2. FPGA raises the `~SU_IRQ` line to notify the supervisor we are in the bootloader*

		3. Supervisor reads the `slots` and `txlen` registers
			a. If the destination slot is not ephemeral:
				  I. Supervisor erases the flash region mapped to that slot
				 II. Supervisor write the contents of the PSRAM for `txlen` into the target flash slot
				III. Supervisor then writes into the FPGA control register that the erase/flash cycle is done
				 IV. Supervisor waits for the FPGA to tell it to reboot into a given slot
				  V. FPGA triggers reboot on DFU detach to last written slot?
			b. If the destination slot *is* ephemeral:
				  I. Supervisor resets the FPGA into configuration mode
				 II. Read a block into our SPI buffer from the PSRAM
				III. While we have not written the full bitstream:
					α. Read at most buffers worth of bitstream data from PSRAM
					β. Dump buffer into FPGA configuration
				 IV. Check FPGA configuration status
				  V. let the FPGA boot into new bitstream


''' # noqa: E101

from torii                 import Elaboratable, Module, Signal, Record
from torii.hdl.rec         import Direction
from torii.lib.fifo        import AsyncFIFO

from torii.lib.soc.csr.bus import Multiplexer, Element

from ..platform            import SquishyPlatformType
from ..peripherals.spi     import SPIInterface, SPIInterfaceMode
from ..peripherals.psram   import SPIPSRAM

__all__ = (
	'Rev2',
)


class CtrlRegister(Record):
	erase: Signal[1, Direction.FANOUT]
	_rsvd: Signal[7, Direction.FANOUT]

class StatusRegister(Record):
	erase_done: Signal[1, Direction.FANIN]
	_rsvd: Signal[7, Direction.FANOUT]


class SupervisorRegisters(Multiplexer):
	def __init__(self, *, name: str | None = None) -> None:

		self._data_width = 8

		super().__init__(addr_width = 2, data_width = self._data_width, name = name)

		self._ctrl_sts = Element(self._data_width,     Element.Access.RW, name = 'ctrl/status')
		self._slots    = Element(self._data_width,     Element.Access.RW, name = 'slots'      )
		self._txlen    = Element(self._data_width * 2, Element.Access.R,  name = 'txlen'      )

		self.add(self._ctrl_sts, addr = 0x0)
		self.add(self._slots,    addr = 0x1)
		self.add(self._txlen,    addr = 0x2)

		self.boot_slot = Signal(4)
		self.dest_slot = Signal(4)
		self.txlen     = Signal(16)

		self.ctrl      = CtrlRegister()
		self.status    = StatusRegister()


	def elaborate(self, platform: SquishyPlatformType | None) -> Module:
		m = super().elaborate(platform)

		m.d.comb += [
			self._txlen.r_data.eq(self.txlen),
			self._slots.r_data[0:4].eq(self.dest_slot),
			self._slots.r_data[4:8].eq(self.boot_slot),
			self._ctrl_sts.r_data.eq(self.status),
		]

		with m.If(self._ctrl_sts.w_stb):
			m.d.sync += [ self.ctrl.eq(self._ctrl_sts.w_data), ]

		return m

class Rev2(Elaboratable):
	'''

	Parameters
	----------
	fifo : AsyncFIFO | None
		The storage FIFO.

	Attributes
	----------
	trigger_reboot : Signal
		FPGA reboot trigger from DFU.

	slot_selection : Signal(2)
		Flash slot destination from DFU alt-mode.

	dl_start : Signal
		Input: Start of a DFU transfer.

	dl_finish : Signal
		Input: An acknowledgement of the `dl_done` signal

	dl_ready : Signal
		Output: If the backing storage is ready for data.

	dl_done : Signal
		Output: When the backing storage is done storing the data.

	dl_reset_slot : Signal
		Input: Signals to the storage to reset the active slot.

	dl_size : Signal(16)
		Input: The size of the DFU transfer into the the FIFO

	slot_changed : Signal
		Input: Raised when the DFU alt-mode is changed.

	slot_ack : Signal
		Output: When the `slot_changed` signal was acted on.

	'''

	def __init__(self, fifo: AsyncFIFO) -> None:
		self.trigger_reboot = Signal()
		self.slot_selection = Signal(2)

		self._bit_fifo      = fifo

		self.dl_start      = Signal()
		self.dl_finish     = Signal()
		self.dl_ready      = Signal()
		self.dl_done       = Signal()
		self.dl_reset_slot = Signal()
		self.dl_size       = Signal(16)

		self.slot_changed = Signal()
		self.slot_ack     = Signal()

	def elaborate(self, platform: SquishyPlatformType | None) -> Module:
		m = Module()

		sup_int = platform.request('supervisor', 0)

		su_irq = sup_int.su_irq.o

		# NOTE(aki): We are not using this signal for anything at the moment, drive it to a defined state
		m.d.comb += [ sup_int.dfu_trg.o.eq(0), ]

		m.submodules.regs = regs = SupervisorRegisters(name = 'supervisor')
		m.submodules.spi  = spi  = SPIInterface(
			clk = sup_int.clk, cipo = sup_int.cipo, copi = sup_int.copi,
			cs_peripheral = sup_int.attn, cs_controller = sup_int.psram,
			mode = SPIInterfaceMode.BOTH, reg_map = regs
		)

		spi_ctrl = spi.controller
		spi_perh = spi.peripheral

		m.submodules.psram = psram = SPIPSRAM(
			controller = spi_ctrl, write_fifo = self._bit_fifo
		)


		return m
