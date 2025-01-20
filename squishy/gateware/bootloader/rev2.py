# SPDX-License-Identifier: BSD-3-Clause


'''

This module contains the implementation of the rev2 hardware-specific bootloader.

The rev2 hardware has a more complex boot process due to the following reasons:
	* The addition of a supervisor MCU
	* The presence of a shared PSRAM between the supervisor and the FPGA

As such, there is a boot protocol that has to be established between the supervisor and the FPGA.

===================
Bootloader Protocol
===================

Squishy Rev2 has a little bit of a complicated boot protocol due to the use of a platform supervisor,
the protocol between the FPGA in either the applet of bootloader state and the supervisor must be well
defined to avoid any potential problems.

-----------
Applet Mode
-----------

When the FPGA is hosting an applet, we can request to drop into the bootloader as follows:

0. FPGA raises ``~SU_IRQ`` with the IRQ register value ``DFU`` set to ``1``
1. Supervisor resets the FPGA configuration and loads the bootloader bitstream
2. Supervisor then waits for the next IRQ event


---------------
Bootloader Mode
---------------

Upon the FPGA entering the bootloader:

0. FPGA waits for a DFU upload, and if done stuffs it into the PSRAM
  a. FPGA Holds ``bus_hold`` high until DFU upload is complete
  b. FPGA sticks the destination slot for the DFU payload into the ``dest_slot`` half of the ``slots`` register
  c. FPGA writes the DFU payload size into the ``txlen`` register

1. FPGA sets the IRQ Reason to ``write_slot``
2. FPGA raises the ``~SU_IRQ`` line to notify the supervisor we want to write slot data
3. Supervisor reads the ``slots`` and ``txlen`` registers
4. Supervisor ACK's the IRQ

  a. If the destination slot *is not* ephemeral:

    I. Supervisor erases the flash region mapped to that slot
    II. Supervisor write the contents of the PSRAM for ``txlen`` into the target flash slot
	III. Goto 4.b

  b. If the destination slot *is* ephemeral:
	I. Supervisor then writes into the FPGA control register that the erase/flash cycle is done
    II. Supervisor waits for the FPGA to tell it to reboot into a given slot with the ``boot`` IRQ
    III. FPGA triggers reboot on DFU detach to last written slot?
    IV. Supervisor resets the FPGA into configuration mode
    V. Read a block into our SPI buffer from the slot backing storage
    VI. While we have not written the full bitstream:

      0. Read at most buffers worth of bitstream data from backing store
      1. Dump buffer into FPGA configuration

    VII. Check FPGA configuration status
    VIII. let the FPGA boot into new bitstream
''' # noqa: E101

from torii                 import Elaboratable, Module, Signal
from torii.lib.fifo        import AsyncFIFO
from torii.lib.cdc         import FFSynchronizer, PulseSynchronizer

from ..core.supervisor_csr import SupervisorCSRMap
from ..platform            import SquishyPlatformType
from ..peripherals.spi     import SPIInterface, SPIInterfaceMode, SPICPOL
from ..peripherals.psram   import SPIPSRAM

__all__ = (
	'Rev2',
)

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

	dl_completed : Signal
		Input: Signal from the DFU handler when a full slot download is completed.

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
		self.dl_completed  = Signal()
		self.dl_size       = Signal(16)

		self.slot_changed = Signal()
		self.slot_ack     = Signal()

	def elaborate(self, platform: SquishyPlatformType | None) -> Module:
		m = Module()

		sup_int = platform.request('supervisor', 0)

		su_irq: Signal   = sup_int.su_irq.o
		bus_hold: Signal = sup_int.bus_hold.o

		m.submodules.regs = regs = SupervisorCSRMap(name = 'supervisor')
		m.submodules.spi  = spi  = SPIInterface(
			clk = sup_int.clk, cipo = sup_int.cipo, copi = sup_int.copi,
			cs_peripheral = sup_int.attn, cs_controller = sup_int.psram,
			cpol = SPICPOL.LOW,
			mode = SPIInterfaceMode.BOTH, reg_map = regs
		)

		m.submodules.psram = psram = SPIPSRAM(
			controller = spi.controller, write_fifo = self._bit_fifo
		)

		trigger_reboot = Signal.like(self.trigger_reboot)
		slot_selection = Signal.like(self.slot_selection)
		slot_changed   = Signal.like(self.slot_changed)
		slot_ack       = Signal.like(self.slot_ack)

		dl_start       = Signal.like(self.dl_start)
		dl_size        = Signal.like(self.dl_size)
		dl_finish      = Signal.like(self.dl_finish)
		dl_ready       = Signal.like(self.dl_ready)
		dl_done        = Signal.like(self.dl_done)
		dl_completed   = Signal.like(self.dl_completed)

		m.d.comb += [
			regs.ctrl_rst.eq(0),
			spi.active_mode.eq(bus_hold), # We should always be a peripheral unless we're explicitly writing to the PSRAM

			dl_ready.eq(psram.ready),
			slot_ack.eq(0),
		]

		with m.FSM(name = 'storage'):
			with m.State('RESET'):
				m.d.sync += [
					regs.txlen.eq(0),
					psram.rst_addrs.eq(1),
				]
				m.next = 'IDLE'

			with m.State('IDLE'):
				m.d.sync += [ psram.rst_addrs.eq(0), ]
				with m.If(slot_changed):
					m.next = 'WAIT_SLOT'
				with m.Elif(dl_start):
					m.d.sync += [
						bus_hold.eq(1),
						regs.txlen.eq(regs.txlen + dl_size)
					]
					m.next = 'DFU_TRANSFER_START'
				with m.Elif(dl_completed):
					m.next = 'DFU_TRANSFER_DONE'
				with m.Elif(trigger_reboot):
					# Handle the case where the host doesn't do and DFU download but wants us to
					# reboot anyway.
					m.next = 'REQUEST_REBOOT'

			with m.State('WAIT_SLOT'):
				m.next = 'SLOT_CHANGED'
			with m.State('SLOT_CHANGED'):
				m.d.sync += [
					regs.slot.dest.eq(slot_selection),
					regs.slot.boot.eq(slot_selection),
				]
				m.d.comb += [
					slot_ack.eq(1),
				]
				m.next = 'IDLE'


			with m.State('DFU_TRANSFER_START'):
				with m.If(dl_finish):
					m.next = 'IDLE'

			with m.State('DFU_TRANSFER_DONE'):
				m.d.sync += [
					regs.irq_reason.write_slot.eq(1),
					bus_hold.eq(0),
					su_irq.eq(1),
				]
				m.next = 'SUPERVISOR_WAIT'

			with m.State('SUPERVISOR_WAIT'):
				with m.If(regs.ctrl.irq_ack):
					m.d.sync += [
						regs.irq_reason.write_slot.eq(0),
						su_irq.eq(0),
					]
					m.d.comb += [ regs.ctrl_rst.eq(1), ]

				with m.If(regs.ctrl.write_done & trigger_reboot):
					m.next = 'REQUEST_REBOOT'

			with m.State('REQUEST_REBOOT'):
				m.d.sync += [
					regs.irq_reason.boot.eq(1),
					su_irq.eq(1),
				]


		m.submodules.ffs_reboot   = FFSynchronizer(self.trigger_reboot, trigger_reboot)
		m.submodules.ffs_dl_size  = FFSynchronizer(self.dl_size, dl_size, stages = 3)
		m.submodules.ffs_dl_done  = FFSynchronizer(dl_done, self.dl_done, o_domain = 'usb')
		m.submodules.ffs_slot_sel = FFSynchronizer(self.slot_selection, slot_selection)
		m.submodules.ffs_dl_read  = FFSynchronizer(dl_ready, self.dl_ready, o_domain = 'usb')

		m.submodules.ps_slot_ack = ps_slot_ack = PulseSynchronizer(i_domain = 'sync', o_domain = 'usb')
		m.submodules.ps_slot_chg = ps_slot_cng = PulseSynchronizer(i_domain = 'usb', o_domain = 'sync')

		m.submodules.ps_dl_start     = ps_dl_start     = PulseSynchronizer(i_domain = 'usb', o_domain = 'sync')
		m.submodules.ps_dl_completed = ps_dl_completed = PulseSynchronizer(i_domain = 'usb', o_domain = 'sync')
		m.submodules.ps_dl_finish    = ps_dl_finish    = PulseSynchronizer(i_domain = 'usb', o_domain = 'sync')

		m.d.comb += [
			ps_slot_ack.i.eq(slot_ack),
			self.slot_ack.eq(ps_slot_ack.o),
			ps_slot_cng.i.eq(self.slot_changed),
			slot_changed.eq(ps_slot_cng.o),

			ps_dl_start.i.eq(self.dl_start),
			dl_start.eq(ps_dl_start.o),

			ps_dl_completed.i.eq(self.dl_completed),
			dl_completed.eq(ps_dl_completed.o),

			ps_dl_finish.i.eq(self.dl_finish),
			dl_finish.eq(ps_dl_finish.o),

			psram.finish.eq(dl_finish),
			dl_done.eq(psram.done),
			psram.start_w.eq(dl_start),
			psram.byte_count.eq(dl_size),
		]

		return m
