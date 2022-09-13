# SPDX-License-Identifier: BSD-3-Clause
from amaranth                    import (
	Elaboratable, Module
)
from amaranth.sim                import (
	Settle
)
from amaranth.lib.fifo           import (
	AsyncFIFO
)

from squishy.core.flash          import (
	FlashGeometry
)
from squishy.gateware.core.flash import (
	SPIFlash
)

from gateware_test               import (
	SquishyGatewareTestCase, sim_test, _MockPlatform
)


class DUTWrapper(Elaboratable):
	def __init__(self, *, resource, size) -> None:
		self._flash_geometry = FlashGeometry(
			size       = 8388608, # 8MiB
			page_size  = 256,
			erase_size = 4096,    # 4KiB
			addr_width = 24
		).init_slots(device = 'iCE40HX8K')

		self._fifo = AsyncFIFO(
			width = 8, depth = self._flash_geometry.erase_size,
			r_domain = 'sync', w_domain = 'usb'
		)
		self._flash = SPIFlash(
			flash_resource = resource,
			flash_geometry = self._flash_geometry,
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

		self.dfuData = (
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


	def elaborate(self, platform) -> Module:
		m = Module()

		m.submodules.fifo  = self._fifo
		m.submodules.flash = self._flash

		return m

# class SPIFlashTests(SquishyGatewareTestCase):
# 	dut: DUTWrapper = DUTWrapper
# 	dut_args = {
# 		'resource': ('spi_flash_1x', 0),
# 		'size': 512 * 1024
# 	}
# 	domains = (('sync', 60e6), ('usb', 60e6))
#
# 	def spi_trans(self, copi = None, cipo = None, partial = False, cont = False):
# 		if copi is not None and cipo is not None:
# 			self.assertEqual(len(copi), len(cipo), 'COPI and CIPO length mismatch')
#
# 		bytes = max(0 if copi is None else len(copi), 0 if cipo is None else len(cipo))
#
# 		self.assertEqual((yield self.dut._spi_bus.clk.o), 1)
# 		self.assertEqual((yield self.dut._spi_bus.cs.o), (1 if cont else 0))
# 		yield Settle()
# 		yield
# 		self.assertEqual((yield self.dut._spi_bus.clk.o), 1)
# 		self.assertEqual((yield self.dut._spi_bus.cs.o), 1)
# 		yield Settle()
# 		yield
# 		for byte in range(bytes):
# 			for bit in range(8):
# 				self.assertEqual((yield self.dut._spi_bus.clk.o), 0)
# 				if copi is not None and copi[byte] is not None:
# 					self.assertEqual((yield self.dut._spi_bus.copi.o), (((copi[byte] << bit) & 0x80) >> 7))
# 				self.assertEqual((yield self.dut._spi_bus.cs.o), 1)
# 				if cipo is not None and cipo[byte] is not None:
# 					yield self.dut._spi_bus.cipo.i.eq((((copi[byte] << bit) & 0x80) >> 7))
# 				yield Settle()
# 				yield
# 				self.assertEqual((yield self.dut._spi_bus.clk.o), 1)
# 				self.assertEqual((yield self.dut._spi_bus.cs.o), 1)
# 				yield Settle()
# 				yield
# 			if cipo is not None and cipo[byte] is not None:
# 				yield self.dut._spi_bus.cipo.i.eq(0)
# 			if byte < bytes - 1:
# 				self.assertEqual((yield self.dut._spi_bus.clk.o), 1)
# 				self.assertEqual((yield self.dut._spi_bus.cs.o), 1)
# 				yield Settle()
# 				yield
# 		self.assertEqual((yield self.dut.done), 0)
# 		if not partial:
# 			self.assertEqual((yield self.dut._spi_bus.clk.o), 1)
# 			self.assertEqual((yield self.dut._spi_bus.cs.o), 0)
# 			yield Settle()
# 			yield
#
#
# 	@sim_test(domain = 'sync')
# 	def test_flash(self):
# 		yield self.dut.startAddr.eq(0)
# 		yield self.dut.endAddr.eq(4096)
# 		yield from self.spi_trans(copi = (0xAB,))
# 		yield Settle()
# 		yield
# 		yield Settle()
# 		yield
# 		yield self.dut.resetAddrs.eq(1)
# 		yield Settle()
# 		yield
# 		yield self.dut.resetAddrs.eq(0)
# 		yield Settle()
# 		yield
# 		yield self.dut.start.eq(1)
# 		yield self.dut.byteCount.eq(len(self.dut.dfuData))
# 		yield Settle()
# 		yield
# 		self.assertEqual((yield self.dut.readAddr), 0)
# 		self.assertEqual((yield self.dut.eraseAddr), 0)
# 		self.assertEqual((yield self.dut.writeAddr), 0)
# 		self.assertEqual((yield self.dut._spi_bus.cs.o), 0)
# 		yield self.dut.start.eq(0)
# 		yield self.dut.byteCount.eq(0)
# 		yield Settle()
# 		yield
# 		yield from self.spi_trans(copi = (0x06,))
# 		yield from self.spi_trans(copi = (0x20, 0x00, 0x00, 0x00))
# 		yield from self.spi_trans(copi = (0x05, None), cipo = (None, 0x03))
# 		yield from self.spi_trans(copi = (0x05, None), cipo = (None, 0x03))
# 		yield from self.spi_trans(copi = (0x05, None), cipo = (None, 0x03))
# 		yield from self.spi_trans(copi = (0x05, None), cipo = (None, 0x00))
# 		yield from self.spi_trans(copi = (0x06,))
# 		self.assertEqual((yield self.dut._fifo.r_rdy), 0)
# 		yield from self.spi_trans(copi = (0x02, 0x00, 0x00, 0x00), partial = True)
# 		yield
# 		self.assertEqual((yield self.dut._spi_bus.cs.o), 1)
# 		self.assertEqual((yield self.dut._spi_bus.clk.o), 1)
# 		self.assertEqual((yield self.dut._fifo.r_rdy), 0)
# 		self.assertEqual((yield self.dut._spi_bus.cs.o), 1)
# 		self.assertEqual((yield self.dut._spi_bus.clk.o), 1)
# 		yield Settle()
# 		yield
# 		self.assertEqual((yield self.dut._fifo.r_rdy), 0)
# 		self.assertEqual((yield self.dut._spi_bus.cs.o), 1)
# 		self.assertEqual((yield self.dut._spi_bus.clk.o), 1)
# 		self.dut.fill_fifo = True
# 		for _ in range(5):
# 			yield Settle()
# 			yield
# 			self.assertEqual((yield self.dut._spi_bus.cs.o), 1)
# 			self.assertEqual((yield self.dut._spi_bus.clk.o), 1)
# 		yield from self.spi_trans(copi = self.dut.dfuData[0:64], cont = True)
# 		self.assertEqual((yield self.dut.writeAddr), 64)
# 		yield from self.spi_trans(copi = (0x05, None), cipo = (None, 0x03))
# 		yield from self.spi_trans(copi = (0x05, None), cipo = (None, 0x00))
# 		yield from self.spi_trans(copi = (0x06,))
# 		yield from self.spi_trans(copi = (0x02, 0x00, 0x00, 0x40), partial = True)
# 		yield from self.spi_trans(copi = self.dut.dfuData[64:128], cont = True)
# 		self.assertEqual((yield self.dut.writeAddr), 128)
# 		yield from self.spi_trans(copi = (0x05, None), cipo = (None, 0x00))
# 		yield from self.spi_trans(copi = (0x06,))
# 		yield from self.spi_trans(copi = (0x02, 0x00, 0x00, 0x80), partial = True)
# 		yield from self.spi_trans(copi = self.dut.dfuData[128:192], cont = True)
# 		self.assertEqual((yield self.dut.writeAddr), 192)
# 		yield from self.spi_trans(copi = (0x05, None), cipo = (None, 0x00))
# 		yield from self.spi_trans(copi = (0x06,))
# 		yield from self.spi_trans(copi = (0x02, 0x00, 0x00, 0xC0), partial = True)
# 		yield from self.spi_trans(copi = self.dut.dfuData[192:256], cont = True)
# 		self.assertEqual((yield self.dut.writeAddr), 256)
# 		yield from self.spi_trans(copi = (0x05, None), cipo = (None, 0x00))
# 		self.assertEqual((yield self.dut.done), 1)
# 		yield self.dut.finish.eq(1)
# 		yield Settle()
# 		yield
# 		self.assertEqual((yield self.dut.done), 1)
# 		yield self.dut.finish.eq(0)
# 		yield Settle()
# 		yield
# 		self.assertEqual((yield self.dut.done), 0)
# 		yield Settle()
# 		yield
# 		yield Settle()
# 		yield
#
# 	@sim_test(domain = 'usb')
# 	def test_fifo(self):
# 		while not self.dut.fill_fifo:
# 			yield
# 		yield self.dut._fifo.w_en.eq(1)
# 		for byte in self.dut.dfuData:
# 			yield self.dut._fifo.w_data.eq(byte)
# 			yield
# 		yield self.dut._fifo.w_en.eq(0)
# 		yield
