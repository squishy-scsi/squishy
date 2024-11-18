# SPDX-License-Identifier: BSD-3-Clause

from torii                              import Elaboratable, Module, Record
from torii.hdl.rec                      import DIR_FANIN, DIR_FANOUT
from torii.lib.fifo                     import AsyncFIFO
from torii.sim                          import Settle
from torii.test                         import ToriiTestCase
from torii.test.mock                    import MockPlatform

from squishy.core.flash                 import Geometry
from squishy.core.config                import FlashConfig
from squishy.gateware.peripherals.flash import SPIFlash

_FLASH_DATA = (
	0xff, 0x00, 0x00, 0xff, 0x7e, 0xaa, 0x99, 0x7e, 0x51, 0x00, 0x01, 0x05, 0x92, 0x00, 0x20, 0x62,
	0x03, 0x67, 0x72, 0x01, 0x10, 0x82, 0x00, 0x00, 0x11, 0x00, 0x01, 0x01, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
)


_SPI_RECORD = Record((
	('clk', [
		('o', 1, DIR_FANOUT),
	]),
	('cs', [
		('o', 1, DIR_FANOUT),
	]),
	('copi', [
		('o', 1, DIR_FANOUT),
	]),
	('cipo', [
		('i', 1, DIR_FANIN),
	]),
))

class DUTPlatform:
	flash = FlashConfig(
		geometry = Geometry(
			size       = 512*1024,
			page_size  = 64,
			erase_size = 256,
			slot_size  = 262144,
			addr_width = 24
		),
		commands = {
			'erase': 0x20,
		}
	)

	def request(self, name, number):
		return _SPI_RECORD


class DUTWrapper(Elaboratable):
	def __init__(self, *, resource) -> None:

		self._fifo = AsyncFIFO(
			width = 8, depth = DUTPlatform.flash.geometry.erase_size, r_domain = 'sync', w_domain = 'usb'
		)

		self._flash = SPIFlash(
			flash_resource = resource, flash_geometry = DUTPlatform.flash.geometry, fifo = self._fifo, erase_cmd = 0x20
		)

		self._spi_bus   = _SPI_RECORD

		self.fill_fifo  = False

		self.start      = self._flash.start
		self.finish     = self._flash.finish
		self.done       = self._flash.done
		self.resetAddrs = self._flash.resetAddrs
		self.startAddr  = self._flash.startAddr
		self.endAddr    = self._flash.endAddr
		self.readAddr   = self._flash.readAddr
		self.eraseAddr  = self._flash.eraseAddr
		self.writeAddr  = self._flash.writeAddr
		self.byteCount  = self._flash.byteCount

	def elaborate(self, _) -> Module:
		m = Module()

		m.submodules.flash = self._flash
		m.submodules.fifo  = self._fifo

		return m


class SPIFlashTests(ToriiTestCase):
	dut: DUTWrapper = DUTWrapper
	dut_args = {
		'resource': ('spi_flash_x1', 0)
	}
	domains = (('sync', 60e6), ('usb', 60e6))
	platform = MockPlatform()

	def spi_trans(self, *,
		copi: tuple[int, ...] | None = None, cipo: tuple[int, ...] | None = None, partial: bool = False, continuation: bool = False
	):
		if cipo is not None and copi is not None:
			self.assertEqual(len(cipo), len(copi))

		bytes = max(0 if copi is None else len(copi), 0 if cipo is None else len(cipo))
		self.assertEqual((yield self.dut._flash._spi._clk), 1)
		if continuation:
			yield Settle()
			self.assertEqual((yield self.dut._flash._spi._cs), 1)
		else:
			self.assertEqual((yield self.dut._flash._spi._cs), 0)
			yield Settle()
		yield
		self.assertEqual((yield self.dut._flash._spi._clk), 1)
		self.assertEqual((yield self.dut._flash._spi._cs), 1)
		yield Settle()
		yield
		for byte in range(bytes):
			for bit in range(8):
				self.assertEqual((yield self.dut._flash._spi._clk), 0)
				if copi is not None and copi[byte] is not None:
					self.assertEqual((yield self.dut._flash._spi._copi), ((copi[byte] << bit) & 0x80) >> 7)
				self.assertEqual((yield self.dut._flash._spi._cs), 1)
				yield Settle()
				if cipo is not None and cipo[byte] is not None:
					yield self.dut._flash._spi._cipo.eq(((cipo[byte] << bit) & 0x80) >> 7)
				yield
				self.assertEqual((yield self.dut._flash._spi._clk), 1)
				self.assertEqual((yield self.dut._flash._spi._cs), 1)
				yield Settle()
				yield
			if byte < bytes - 1:
				self.assertEqual((yield self.dut._flash._spi._clk), 1)
				self.assertEqual((yield self.dut._flash._spi._cs), 1)
			self.assertEqual((yield self.dut.done), 0)
			yield Settle()
			if cipo is not None and cipo[byte] is not None:
				yield self.dut._flash._spi._cipo.eq(0)
			if byte < bytes - 1:
				yield
		if not partial:
			self.assertEqual((yield self.dut._flash._spi._clk), 1)
			self.assertEqual((yield self.dut._flash._spi._cs), 0)
			yield Settle()
			yield

	@ToriiTestCase.simulation
	def test_flash(self):
		@ToriiTestCase.sync_domain(domain = 'usb')
		def fifo(self):
			while not self.dut.fill_fifo:
				yield
			yield self.dut._fifo.w_en.eq(1)
			for byte in _FLASH_DATA:
				yield self.dut._fifo.w_data.eq(byte)
				yield
			yield self.dut._fifo.w_en.eq(0)
			yield

		@ToriiTestCase.sync_domain(domain = 'sync')
		def flash(self):
			# self.dut._spi_bus = _SPI_RECORD
			yield self.dut._flash.startAddr.eq(0)
			yield self.dut._flash.endAddr.eq(4096)
			yield from self.spi_trans(copi = (0xAB,))
			yield Settle()
			yield
			yield Settle()
			yield
			yield self.dut.resetAddrs.eq(1)
			yield Settle()
			yield
			yield self.dut.resetAddrs.eq(0)
			yield Settle()
			yield
			yield self.dut.start.eq(1)
			yield self.dut.byteCount.eq(len(_FLASH_DATA))
			yield Settle()
			yield
			yield self.dut.start.eq(0)
			yield Settle()
			self.assertEqual((yield self.dut.readAddr), 0)
			self.assertEqual((yield self.dut.eraseAddr), 0)
			self.assertEqual((yield self.dut.writeAddr), 0)
			self.assertEqual((yield self.dut._flash._spi._cs), 0)
			yield
			yield from self.spi_trans(copi = (0x06,))
			yield from self.spi_trans(copi = (0x20, 0x00, 0x00, 0x00))
			yield from self.spi_trans(copi = (0x05, None), cipo = (None, 0x03))
			yield from self.spi_trans(copi = (0x05, None), cipo = (None, 0x03))
			yield from self.spi_trans(copi = (0x05, None), cipo = (None, 0x03))
			yield from self.spi_trans(copi = (0x05, None), cipo = (None, 0x00))
			yield from self.spi_trans(copi = (0x06,))
			self.assertEqual((yield self.dut._fifo.r_rdy), 0)
			yield from self.spi_trans(copi = (0x02, 0x00, 0x00, 0x00), partial = True)
			yield
			yield Settle()
			self.assertEqual((yield self.dut._flash._spi._cs), 1)
			self.assertEqual((yield self.dut._flash._spi._clk), 1)
			self.assertEqual((yield self.dut._fifo.r_rdy), 0)
			self.assertEqual((yield self.dut._flash._spi._cs), 1)
			self.assertEqual((yield self.dut._flash._spi._clk), 1)
			yield
			yield Settle()
			self.assertEqual((yield self.dut._fifo.r_rdy), 0)
			self.assertEqual((yield self.dut._flash._spi._cs), 1)
			self.assertEqual((yield self.dut._flash._spi._clk), 1)
			self.dut.fill_fifo = True
			for _ in range(6):
				yield Settle()
				yield
				self.assertEqual((yield self.dut._flash._spi._cs), 1)
				self.assertEqual((yield self.dut._flash._spi._clk), 1)
			# :<
			yield from self.spi_trans(copi = _FLASH_DATA[0:64], continuation = True)
			self.assertEqual((yield self.dut.writeAddr), 64)
			yield from self.spi_trans(copi = (0x05, None), cipo = (None, 0x03))
			yield from self.spi_trans(copi = (0x05, None), cipo = (None, 0x00))

			yield from self.spi_trans(copi = (0x06,))
			yield from self.spi_trans(copi = (0x02, 0x00, 0x00, 0x40), partial = True)
			yield from self.spi_trans(copi = _FLASH_DATA[64:128], continuation = True)
			self.assertEqual((yield self.dut.writeAddr), 128)
			yield from self.spi_trans(copi = (0x05, None), cipo = (None, 0x00))

			yield from self.spi_trans(copi = (0x06,))
			yield from self.spi_trans(copi = (0x02, 0x00, 0x00, 0x80), partial = True)
			yield from self.spi_trans(copi = _FLASH_DATA[128:192], continuation = True)
			self.assertEqual((yield self.dut.writeAddr), 192)
			yield from self.spi_trans(copi = (0x05, None), cipo = (None, 0x00))

			yield from self.spi_trans(copi = (0x06,))
			yield from self.spi_trans(copi = (0x02, 0x00, 0x00, 0xC0), partial = True)
			yield from self.spi_trans(copi = _FLASH_DATA[192:256], continuation = True)
			self.assertEqual((yield self.dut.writeAddr), 256)
			yield from self.spi_trans(copi = (0x05, None), cipo = (None, 0x00))

			self.assertEqual((yield self.dut.done), 1)
			yield self.dut.finish.eq(1)
			yield
			self.assertEqual((yield self.dut.done), 1)
			yield self.dut.finish.eq(0)
			yield Settle()
			yield
			self.assertEqual((yield self.dut.done), 0)
			yield Settle()
			yield
			yield Settle()
			yield

		fifo(self)
		flash(self)
