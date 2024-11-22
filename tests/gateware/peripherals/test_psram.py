# SPDX-License-Identifier: BSD-3-Clause

from random                             import randbytes


from torii                              import Elaboratable, Module, Signal
from torii.lib.fifo                     import AsyncFIFO
from torii.sim                          import Settle
from torii.test                         import ToriiTestCase
from torii.test.mock                    import MockPlatform

from squishy.gateware.peripherals.spi   import SPIController, SPICPOL
from squishy.gateware.peripherals.psram import SPIPSRAM

_PSRAM_DATA = randbytes(4096)

clk  = Signal()
cs   = Signal()
copi = Signal()
cipo = Signal()



class DUTWrapper(Elaboratable):
	def __init__(self) -> None:

		self._fifo  = AsyncFIFO(width = 8, depth = 4096, r_domain = 'sync', w_domain = 'sync')
		self._spi   = SPIController(
			clk = clk, cipo = cipo, copi = copi, cs = cs, cpol = SPICPOL.LOW
		)
		self._psram = SPIPSRAM(controller = self._spi, fifo = self._fifo)


		self.fill_fifo  = False

		self.ready      = self._psram.ready
		self.done       = self._psram.done
		self.start      = self._psram.start
		self.finish     = self._psram.finish
		self.rst_addrs  = self._psram.rst_addrs
		self.start_addr = self._psram.start_addr
		self.curr_addr  = self._psram.curr_addr
		self.byte_count = self._psram.byte_count


	def elaborate(self, _) -> Module:
		m = Module()

		m.submodules.fifo  = self._fifo
		m.submodules.spi   = self._spi
		m.submodules.psram = self._psram

		return m


class SPIPSRAMTests(ToriiTestCase):
	dut: DUTWrapper = DUTWrapper
	dut_args = { }
	domains = (('sync', 60e6), )
	platform = MockPlatform()

	def spi_trans(self, *,
		copi: tuple[int, ...] | None = None, cipo: tuple[int, ...] | None = None, partial: bool = False, continuation: bool = False
	):
		if cipo is not None and copi is not None:
			self.assertEqual(len(cipo), len(copi))

		bytes = max(0 if copi is None else len(copi), 0 if cipo is None else len(cipo))
		self.assertEqual((yield self.dut._psram._spi._clk), 0)
		if continuation:
			yield Settle()
			self.assertEqual((yield self.dut._psram._spi._cs), 1)
		else:
			self.assertEqual((yield self.dut._psram._spi._cs), 0)
			yield Settle()
		yield
		self.assertEqual((yield self.dut._psram._spi._clk), 0)
		self.assertEqual((yield self.dut._psram._spi._cs), 1)
		yield Settle()
		yield
		for byte in range(bytes):
			for bit in range(8):
				self.assertEqual((yield self.dut._psram._spi._clk), 1)
				if copi is not None and copi[byte] is not None:
					self.assertEqual((yield self.dut._psram._spi._copi), ((copi[byte] << bit) & 0x80) >> 7)
				self.assertEqual((yield self.dut._psram._spi._cs), 1)
				yield Settle()
				if cipo is not None and cipo[byte] is not None:
					yield self.dut._psram._spi._cipo.eq(((cipo[byte] << bit) & 0x80) >> 7)
				yield
				self.assertEqual((yield self.dut._psram._spi._clk), 1)
				self.assertEqual((yield self.dut._psram._spi._cs), 1)
				yield Settle()
				yield
			if byte < bytes - 1:
				self.assertEqual((yield self.dut._psram._spi._clk), 1)
				self.assertEqual((yield self.dut._psram._spi._cs), 1)
			self.assertEqual((yield self.dut.done), 0)
			yield Settle()
			if cipo is not None and cipo[byte] is not None:
				yield self.dut._psram._spi._cipo.eq(0)
			if byte < bytes - 1:
				yield
		if not partial:
			self.assertEqual((yield self.dut._psram._spi._clk), 1)
			self.assertEqual((yield self.dut._psram._spi._cs), 0)
			yield Settle()
			yield

	@ToriiTestCase.simulation
	@ToriiTestCase.sync_domain(domain = 'sync')
	def test_psram(self):
		yield
		self.skipTest('aaaaa')
		yield self.dut._psram.start_addr.eq(0)
		yield self.dut.rst_addrs.eq(1)
		yield Settle()
		yield
		yield self.dut.rst_addrs.eq(0)
		yield Settle()
		yield
		yield self.dut.start.eq(1)
		yield self.dut.byte_count.eq(len(_PSRAM_DATA))
		yield Settle()
		yield
		yield self.dut.start.eq(0)
		yield Settle()
		self.assertEqual((yield self.dut.curr_addr), 0)
		self.assertEqual((yield self.dut.start_addr), 0)
		self.assertEqual((yield self.dut._psram._spi._cs), 0)
		yield
		yield from self.spi_trans(copi = (0x02,))
		yield from self.spi_trans(copi = (0x00, 0x00, 0x00))
		yield from self.spi_trans(copi = (0x05, None), cipo = (None, 0x03))
		yield from self.spi_trans(copi = (0x05, None), cipo = (None, 0x03))
		yield from self.spi_trans(copi = (0x05, None), cipo = (None, 0x03))
		yield from self.spi_trans(copi = (0x05, None), cipo = (None, 0x00))
		yield from self.spi_trans(copi = (0x06,))
		self.assertEqual((yield self.dut._fifo.r_rdy), 0)
		yield from self.spi_trans(copi = (0x02, 0x00, 0x00, 0x00), partial = True)
		yield
		yield Settle()
		self.assertEqual((yield self.dut._psram._spi._cs), 1)
		self.assertEqual((yield self.dut._psram._spi._clk), 1)
		self.assertEqual((yield self.dut._fifo.r_rdy), 0)
		self.assertEqual((yield self.dut._psram._spi._cs), 1)
		self.assertEqual((yield self.dut._psram._spi._clk), 1)
		yield
		yield Settle()
		self.assertEqual((yield self.dut._fifo.r_rdy), 0)
		self.assertEqual((yield self.dut._psram._spi._cs), 1)
		self.assertEqual((yield self.dut._psram._spi._clk), 1)
		self.dut.fill_fifo = True
		for _ in range(6):
			yield Settle()
			yield
			self.assertEqual((yield self.dut._psram._spi._cs), 1)
			self.assertEqual((yield self.dut._psram._spi._clk), 1)
		# :<
		yield from self.spi_trans(copi = _PSRAM_DATA[0:64], continuation = True)
		self.assertEqual((yield self.dut.writeAddr), 64)
		yield from self.spi_trans(copi = (0x05, None), cipo = (None, 0x03))
		yield from self.spi_trans(copi = (0x05, None), cipo = (None, 0x00))

		yield from self.spi_trans(copi = (0x06,))
		yield from self.spi_trans(copi = (0x02, 0x00, 0x00, 0x40), partial = True)
		yield from self.spi_trans(copi = _PSRAM_DATA[64:128], continuation = True)
		self.assertEqual((yield self.dut.writeAddr), 128)
		yield from self.spi_trans(copi = (0x05, None), cipo = (None, 0x00))

		yield from self.spi_trans(copi = (0x06,))
		yield from self.spi_trans(copi = (0x02, 0x00, 0x00, 0x80), partial = True)
		yield from self.spi_trans(copi = _PSRAM_DATA[128:192], continuation = True)
		self.assertEqual((yield self.dut.writeAddr), 192)
		yield from self.spi_trans(copi = (0x05, None), cipo = (None, 0x00))

		yield from self.spi_trans(copi = (0x06,))
		yield from self.spi_trans(copi = (0x02, 0x00, 0x00, 0xC0), partial = True)
		yield from self.spi_trans(copi = _PSRAM_DATA[192:256], continuation = True)
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
