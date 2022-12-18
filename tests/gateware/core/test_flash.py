# SPDX-License-Identifier: BSD-3-Clause

from typing                      import Optional, Tuple

from torii                       import Elaboratable, Module, Record
from torii.hdl.rec               import DIR_FANIN, DIR_FANOUT
from torii.lib.fifo              import AsyncFIFO
from torii.sim                   import Settle
from torii.test                  import ToriiTestCase, sim_test

from squishy.core.flash          import FlashGeometry
from squishy.gateware.core.flash import SPIFlash

_DFU_DATA = (
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

class DFUPlatform:
	flash = {
		'geometry': FlashGeometry(
			size       = 512*1024,
			page_size  = 64,
			erase_size = 256,
			addr_width = 24
		).init_slots(device = 'iCE40HX8K'),
		'commands': {
			'erase': 0x20,
		}
	}

	def request(self, name, number):
		return _SPI_RECORD


class DUTWrapper(Elaboratable):
	def __init__(self, *, resource) -> None:
		self._fifo = AsyncFIFO(
			width = 8, depth = DFUPlatform.flash['geometry'].erase_size,
			r_domain = 'sync', w_domain = 'usb'
		)
		self._flash = SPIFlash(
			flash_resource = resource,
			flash_geometry = DFUPlatform.flash['geometry'],
			fifo = self._fifo,
			erase_cmd = 0x20
		)

		# Pull out the raw SPI bus for testing
		self._spi_bus   = self._flash._spi._spi

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

	def elaborate(self, platform) -> Module:
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


	def spi_trans(self, *,
		copi: Optional[Tuple[int]] = None, cipo: Optional[Tuple[int]] = None,
		partial: bool = False, continuation: bool = False
	):
		if cipo is not None and copi is not None:
			self.assertEqual(len(cipo), len(copi))

		bytes = max(0 if copi is None else len(copi), 0 if cipo is None else len(cipo))
		self.assertEqual((yield self.dut._spi_bus.clk.o), 1)
		self.assertEqual((yield self.dut._spi_bus.cs.o), (1 if continuation else 0))
		yield Settle()
		yield
		self.assertEqual((yield self.dut._spi_bus.clk.o), 1)
		self.assertEqual((yield self.dut._spi_bus.cs.o), 1)
		yield Settle()
		yield
		for byte in range(bytes):
			for bit in range(8):
				self.assertEqual((yield self.dut._spi_bus.clk.o), 0)
				if copi is not None and copi[byte] is not None:
					self.assertEqual((yield self.dut._spi_bus.copi.o), ((copi[byte] << bit) & 0x80) >> 7)
				self.assertEqual((yield self.dut._spi_bus.cs.o), 1)
				if cipo is not None and cipo[byte] is not None:
					yield self.dut._spi_bus.cipo.i.eq(((cipo[byte] << bit) & 0x80) >> 7)
				yield Settle()
				yield
				self.assertEqual((yield self.dut._spi_bus.clk.o), 1)
				self.assertEqual((yield self.dut._spi_bus.cs.o), 1)
				yield Settle()
				yield
			if cipo is not None and cipo[byte] is not None:
				yield self.dut._spi_bus.cipo.i.eq(0)
			if byte < bytes - 1:
				self.assertEqual((yield self.dut._spi_bus.clk.o), 1)
				self.assertEqual((yield self.dut._spi_bus.cs.o), 1)
				yield Settle()
				yield
		self.assertEqual((yield self.dut.done), 0)
		if not partial:
			self.assertEqual((yield self.dut._spi_bus.clk.o), 1)
			self.assertEqual((yield self.dut._spi_bus.cs.o), 0)
			yield Settle()
			yield



	@sim_test(domain = 'sync', defer = True)
	def flash(self):
		self.dut._spi_bus = self.dut._flash._spi._spi
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
		yield self.dut.byteCount.eq(len(_DFU_DATA))
		yield Settle()
		yield
		self.assertEqual((yield self.dut.readAddr), 0)
		self.assertEqual((yield self.dut.eraseAddr), 0)
		self.assertEqual((yield self.dut.writeAddr), 0)
		self.assertEqual((yield self.dut._spi_bus.cs.o), 0)
		yield self.dut.start.eq(1)
		yield self.dut.byteCount.eq(len(_DFU_DATA))
		yield Settle()
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
		self.assertEqual((yield self.dut._spi_bus.cs.o), 1)
		self.assertEqual((yield self.dut._spi_bus.clk.o), 1)
		self.assertEqual((yield self.dut._fifo.r_rdy), 0)
		self.assertEqual((yield self.dut._spi_bus.cs.o), 1)
		self.assertEqual((yield self.dut._spi_bus.clk.o), 1)
		yield Settle()
		yield
		self.assertEqual((yield self.dut._fifo.r_rdy), 0)
		self.assertEqual((yield self.dut._spi_bus.cs.o), 1)
		self.assertEqual((yield self.dut._spi_bus.clk.o), 1)
		self.dut.fill_fifo = True
		for _ in range(5):
			yield Settle()
			yield
			self.assertEqual((yield self.dut._spi_bus.cs.o), 1)
			self.assertEqual((yield self.dut._spi_bus.clk.o), 1)
		yield from self.spi_trans(copi = _DFU_DATA[0:64], continuation = True)
		self.assertEqual((yield self.dut.writeAddr), 64)
		yield from self.spi_trans(copi = (0x05, None), cipo = (None, 0x03))
		yield from self.spi_trans(copi = (0x05, None), cipo = (None, 0x00))

		yield from self.spi_trans(copi = (0x06,))
		yield from self.spi_trans(copi = (0x02, 0x00, 0x00, 0x40), partial = True)
		yield from self.spi_trans(copi = _DFU_DATA[64:128], continuation = True)
		self.assertEqual((yield self.dut.writeAddr), 128)
		yield from self.spi_trans(copi = (0x05, None), cipo = (None, 0x00))

		yield from self.spi_trans(copi = (0x06,))
		yield from self.spi_trans(copi = (0x02, 0x00, 0x00, 0x80), partial = True)
		yield from self.spi_trans(copi = _DFU_DATA[128:192], continuation = True)
		self.assertEqual((yield self.dut.writeAddr), 192)
		yield from self.spi_trans(copi = (0x05, None), cipo = (None, 0x00))

		yield from self.spi_trans(copi = (0x06,))
		yield from self.spi_trans(copi = (0x02, 0x00, 0x00, 0xC0), partial = True)
		yield from self.spi_trans(copi = _DFU_DATA[192:256], continuation = True)
		self.assertEqual((yield self.dut.writeAddr), 256)
		yield from self.spi_trans(copi = (0x05, None), cipo = (None, 0x00))

		self.assertEqual((yield self.dut.done), 1)
		yield self.dut.finish.eq(1)
		yield Settle()
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

	@sim_test(domain = 'usb', defer = True)
	def fifo(self):
		while not self.dut.fill_fifo:
			yield
		yield self.dut._fifo.w_en.eq(1)
		for byte in _DFU_DATA:
			yield self.dut._fifo.w_data.eq(byte)
			yield
		yield self.dut._fifo.w_en.eq(0)
		yield

	def test_flash(self):
		self.flash()
		self.fifo()

		self.run_sim(suffix = 'test_flash')
