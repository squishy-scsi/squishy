# SPDX-License-Identifier: BSD-3-Clause

from random                           import randbytes

from torii.hdl                        import Elaboratable, Module, Record
from torii.hdl.rec                    import Direction
from torii.lib.fifo                   import AsyncFIFO
from torii.sim                        import Settle
from torii.test                       import ToriiTestCase

from squishy.core.config              import FlashConfig
from squishy.core.flash               import Geometry
from squishy.gateware.bootloader.rev1 import Rev1
from squishy.gateware.usb.dfu         import DFURequestHandler, DFUState
from squishy.support.test             import DFUGatewareTest, USBGatewareTest

_DFU_DATA = randbytes(256)

_SPI_RECORD = Record((
	('clk', [
		('o', 1, Direction.FANOUT),
	]),
	('cs', [
		('o', 1, Direction.FANOUT),
	]),
	('copi', [
		('o', 1, Direction.FANOUT),
	]),
	('cipo', [
		('i', 1, Direction.FANIN),
	]),
))

class DFUPlatform:
	flash = FlashConfig(
		geometry = Geometry(
			size       = 8388608, # 8MiB
			page_size  = 256,
			erase_size = 4096,    # 4KiB
			slot_size  = 262144,
			addr_width = 24
		),
		commands = {
			'erase': 0x20,
		}
	)

	SIM_PLATFORM = True

	def request(self, *_):
		return _SPI_RECORD

class DUTWrapper(Elaboratable):
	def __init__(self) -> None:

		self.fifo = AsyncFIFO(
			width = 8, depth = DFUPlatform.flash.geometry.erase_size, r_domain = 'sync', w_domain = 'usb'
		)

		self.dfu  = DFURequestHandler(1, 0, False, fifo = self.fifo)
		self.rev1 = Rev1(self.fifo)

		self.interface = self.dfu.interface

	def elaborate(self, _) -> Module:
		m = Module()

		m.submodules.fifo = self.fifo
		m.submodules.dfu  = self.dfu
		m.submodules.rev1 = self.rev1

		m.d.comb += [
			self.rev1.trigger_reboot.eq(self.dfu.trigger_reboot),
			self.rev1.slot_selection.eq(self.dfu.slot_selection),
			self.rev1.slot_changed.eq(self.dfu.slot_changed),
			self.rev1.dl_start.eq(self.dfu.dl_start),
			self.rev1.dl_finish.eq(self.dfu.dl_finish),
			self.rev1.dl_size.eq(self.dfu.dl_size),
			self.dfu.slot_ack.eq(self.rev1.slot_ack),
			self.dfu.dl_ready.eq(self.rev1.dl_ready),
			self.dfu.dl_done.eq(self.rev1.dl_done),
		]

		return m

class Rev1BootloaderTests(USBGatewareTest, DFUGatewareTest):
	dut: DUTWrapper = DUTWrapper
	dut_args = {}
	domains  = (('sync', 80e6), )
	platform = DFUPlatform()

	def __init__(self, *args, **kwargs) -> None:
		super().__init__(*args, **kwargs)

	def spi_trans(self, *,
		copi: tuple[int, ...] | None = None, cipo: tuple[int, ...] | None = None, partial: bool = False, continuation: bool = False
	):
		if cipo is not None and copi is not None:
			self.assertEqual(len(cipo), len(copi))

		bytes = max(0 if copi is None else len(copi), 0 if cipo is None else len(cipo))
		self.assertEqual((yield _SPI_RECORD.clk.o), 1)
		if continuation:
			yield Settle()
			self.assertEqual((yield _SPI_RECORD.cs.o), 1)
		else:
			self.assertEqual((yield _SPI_RECORD.cs.o), 0)
			yield Settle()
		yield
		self.assertEqual((yield _SPI_RECORD.clk.o), 1)
		self.assertEqual((yield _SPI_RECORD.cs.o), 1)
		yield Settle()
		yield
		for byte in range(bytes):
			for bit in range(8):
				self.assertEqual((yield _SPI_RECORD.clk.o), 0)
				if copi is not None and copi[byte] is not None:
					self.assertEqual((yield _SPI_RECORD.copi.o), ((copi[byte] << bit) & 0x80) >> 7)
				self.assertEqual((yield _SPI_RECORD.cs.o), 1)
				yield Settle()
				if cipo is not None and cipo[byte] is not None:
					yield _SPI_RECORD.cipo.i.eq(((cipo[byte] << bit) & 0x80) >> 7)
				yield
				self.assertEqual((yield _SPI_RECORD.clk.o), 1)
				self.assertEqual((yield _SPI_RECORD.cs.o), 1)
				yield Settle()
				yield
			if byte < bytes - 1:
				self.assertEqual((yield _SPI_RECORD.clk.o), 1)
				self.assertEqual((yield _SPI_RECORD.cs.o), 1)
			yield Settle()
			if cipo is not None and cipo[byte] is not None:
				yield _SPI_RECORD.cipo.i.eq(0)
			if byte < bytes - 1:
				yield
		if not partial:
			self.assertEqual((yield _SPI_RECORD.clk.o), 1)
			self.assertEqual((yield _SPI_RECORD.cs.o), 0)
			yield Settle()
			yield

	@ToriiTestCase.simulation
	def test_integration(self):
		@ToriiTestCase.sync_domain(domain = 'usb')
		def dfu(self: Rev1BootloaderTests):
			# Setup the active interface
			yield self.dut.dfu.interface.active_config.eq(1)
			yield Settle()
			yield from self.wait_until_high(self.dut.dfu.dl_ready)
			# Make sure we're in Idle
			yield from self.send_dfu_get_status()
			yield from self.receive_data(data = (0, 0, 0, 0, DFUState.DFUIdle, 0))
			# Set the interface up
			yield from self.send_setup_set_interface(interface = 0, alt_mode = 1)
			yield from self.receive_zlp()
			self.assertEqual((yield self.dut.dfu.slot_selection), 1)
			yield from self.wait_until_high(self.dut.dfu.slot_ack)
			yield from self.step(3)
			# Yeet the data
			yield from self.send_dfu_download()
			yield from self.send_data(data = _DFU_DATA)
			yield from self.send_dfu_get_status()
			yield from self.receive_data(data = (0, 0, 0, 0, DFUState.DlBusy, 0))
			yield from self.send_dfu_get_state()
			yield from self.receive_data(data = (DFUState.DlBusy, ))
			yield from self.step(6)
			yield from self.send_dfu_get_state()
			# The backing storage is chewing on the data, just spin for a bit
			while (yield from self.receive_data(data = (DFUState.DlBusy,), check = False)):
				yield from self.send_dfu_get_state()
			yield from self.step(3)
			# Make sure we're in sync
			yield from self.send_dfu_get_state()
			yield from self.receive_data(data = (DFUState.DlSync,))
			yield from self.send_dfu_get_status()
			yield from self.receive_data(data = (0, 0, 0, 0, DFUState.DlSync, 0))
			# And back to Idle
			yield from self.send_dfu_get_state()
			yield from self.receive_data(data = (DFUState.DlIdle,))
			yield
			# And trigger a reboot
			self.assertEqual((yield self.dut.dfu.trigger_reboot), 0)
			yield from self.send_dfu_detach()
			yield from self.receive_zlp()
			self.assertEqual((yield self.dut.dfu.trigger_reboot), 1)
			yield Settle()
			yield
			self.assertEqual((yield self.dut.dfu.trigger_reboot), 1)
			yield
			yield from self.step(10)

		@ToriiTestCase.sync_domain(domain = 'sync')
		def flash(self: Rev1BootloaderTests):
			yield from self.spi_trans(copi = (0xAB,))
			yield from self.step(45)
			yield from self.spi_trans(copi = (0x06,))
			yield from self.spi_trans(copi = (self.platform.flash.commands['erase'], 0x00, 0x10, 0x00))
			yield from self.wait_until_high(self.dut.rev1.dl_finish)
			self.assertEqual((yield _SPI_RECORD.cs.o),   0)
			self.assertEqual((yield _SPI_RECORD.clk.o),  1)
			self.assertEqual((yield _SPI_RECORD.copi.o), 0)
			self.assertEqual((yield _SPI_RECORD.cipo.i), 0)


		dfu(self)
		flash(self)
