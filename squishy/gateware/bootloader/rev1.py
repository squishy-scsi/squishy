# SPDX-License-Identifier: BSD-3-Clause

'''

'''

from struct              import pack, unpack

from torii.hdl           import Cat, Const, Elaboratable, Instance, Memory, Module, Signal
from torii.lib.cdc       import FFSynchronizer, PulseSynchronizer
from torii.lib.fifo      import AsyncFIFO

from ...core.flash       import Geometry
from ..peripherals.flash import SPIFlash
from ..platform          import SquishyPlatformType

__all__ = (
	'Rev1',
)

class Rev1(Elaboratable):
	'''

	Parameters
	----------
	fifo : AsyncFIFO | None
		The storage FIFO.

	Attributes
	----------
	trigger_reboot : Signal
		Input: FPGA reboot trigger from DFU.

	slot_selection : Signal(2)
		Input: Flash slot destination from DFU alt-mode.

	dl_start : Signal
		Input: Start of a DFU transfer.

	dl_finish : Signal
		Input: An acknowledgement of the `dl_done` signal

	dl_ready : Signal
		Output: If the backing storage is ready for data.

	dl_done : Signal
		Output: When the backing storage is done storing the data.

	dl_completed : Signal
		Input: Unused

	dl_size : Signal(16)
		Input: The size of the DFU transfer into the the FIFO

	slot_changed : Signal
		Input: Raised when the DFU alt-mode is changed.

	slot_ack : Signal
		Output: When the `slot_changed` signal was acted on.

	'''

	def __init__(self, fifo: AsyncFIFO) -> None:

		self._bit_fifo  = fifo

		self.trigger_reboot = Signal()

		self.slot_selection = Signal(2)
		self.slot_changed   = Signal()
		self.slot_ack       = Signal()

		self.dl_start     = Signal()
		self.dl_finish    = Signal()
		self.dl_ready     = Signal()
		self.dl_done      = Signal()
		self.dl_completed = Signal()
		self.dl_size      = Signal(16)

	def elaborate(self, platform: SquishyPlatformType | None) -> Module:
		m = Module()

		trigger_reboot = Signal.like(self.trigger_reboot)

		slot_selection = Signal.like(self.slot_selection)
		slot_changed   = Signal.like(self.slot_changed)
		slot_ack       = Signal.like(self.slot_ack)
		active_slot    = Signal.like(slot_selection)

		dl_ready       = Signal.like(self.dl_ready)
		dl_ready_delay = Signal.like(dl_ready)

		slot_rom = self._mk_rom(platform.flash.geometry)
		m.submodules.slots = slots = slot_rom.read_port(transparent = False)

		flash = SPIFlash(flash_resource = ('spi_flash_1x', 0), flash_geometry = platform.flash.geometry, fifo = self._bit_fifo)

		m.submodules.flash = flash

		# Set up the iCE40 warmboot if we're not in Sim
		if not hasattr(platform, 'SIM_PLATFORM'):
			m.submodules.warmboot = Instance(
				'SB_WARMBOOT',
				i_BOOT  = trigger_reboot,
				i_S0    = slot_selection[0],
				i_S1    = slot_selection[1],
			)

		m.d.comb += [
			flash.resetAddrs.eq(0),
			dl_ready.eq(0),
			slot_ack.eq(0),
		]

		m.d.sync += [
			dl_ready_delay.eq(dl_ready),
		]

		with m.FSM(name = 'storage'):
			with m.State('RESET'):
				m.d.sync += [ active_slot.eq(0), ]
				with m.If(flash.ready):
					m.next = 'READ_SLOT_DATA'

			with m.State('READ_SLOT_DATA'):
				m.d.comb += [ slots.addr.eq(Cat(Const(0, 1), active_slot)), ]
				m.next = 'READ_SLOT_BEGIN'

			with m.State('READ_SLOT_BEGIN'):
				m.d.comb += [ slots.addr.eq(Cat(Const(1, 1), active_slot)),    ]
				m.d.sync += [ flash.startAddr.eq(slots.data), ]
				m.next = 'READ_SLOT_END'

			with m.State('READ_SLOT_END'):
				m.d.sync += [ flash.endAddr.eq(slots.data), ]
				m.d.comb += [
					flash.resetAddrs.eq(1),
					slot_ack.eq(1),
				]
				m.next = 'IDLE'

			with m.State('IDLE'):
				m.d.comb += [ dl_ready.eq(1), ]
				with m.If(slot_changed):
					m.d.sync += [ active_slot.eq(slot_selection), ]
					m.next = 'READ_SLOT_DATA'

		# We don't need to sync reboot if we are in sim
		if not hasattr(platform, 'SIM_PLATFORM'):
			m.submodules.ffs_reboot    = FFSynchronizer(self.trigger_reboot, trigger_reboot)

		m.submodules.ffs_dl_finish = FFSynchronizer(self.dl_finish, flash.finish)
		m.submodules.ffs_dl_size   = FFSynchronizer(self.dl_size, flash.byteCount)
		m.submodules.ffs_dl_start  = FFSynchronizer(self.dl_start, flash.start)
		m.submodules.ffs_slot_chg  = FFSynchronizer(self.slot_changed, slot_changed)
		m.submodules.ffs_slot_sel  = FFSynchronizer(self.slot_selection, slot_selection)
		m.submodules.ffs_dl_done   = FFSynchronizer(flash.done, self.dl_done, o_domain = 'usb')

		m.submodules.ps_dl_ready = ps_dl_ready = PulseSynchronizer(i_domain = 'sync', o_domain = 'usb')
		m.submodules.ps_slot_ack = ps_slot_ack = PulseSynchronizer(i_domain = 'sync', o_domain = 'usb')


		m.d.comb += [
			ps_dl_ready.i.eq(dl_ready & ~dl_ready_delay),
			self.dl_ready.eq(ps_dl_ready.o),

			ps_slot_ack.i.eq(slot_ack),
			self.slot_ack.eq(ps_slot_ack.o),
		]


		return m

	def _mk_rom(self, flash_geometry: Geometry) -> Memory:
		'''
		Generate the ROM layout for the flash addresses.

		Parameters
		----------
		flash_geometry : Geometry
			The platform flash geometry.

		Returns
		-------
		Memory
			The ROM containing the flash address maps.
		'''

		total_size = flash_geometry.slots * 8

		rom        = bytearray(total_size)
		rom_addr   = 0

		for idx, partition in flash_geometry.partitions.items():
			addr_range = pack('>II', partition.start_addr, partition.end_addr)
			rom[rom_addr:rom_addr + 8] = addr_range
			rom_addr += 8

		rom_entries = ( rom[i:i + 4] for i in range(0, total_size, 4) )
		initializer = [ unpack('>I', rom_entry)[0] for rom_entry in rom_entries ]
		return Memory(width = 24, depth = flash_geometry.slots * 2, init = initializer)
