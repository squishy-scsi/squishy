# SPDX-License-Identifier: BSD-3-Clause

from random                             import randbytes


from torii                              import Elaboratable, Module, Signal
from torii.lib.fifo                     import AsyncFIFO
from torii.sim                          import Settle
from torii.test                         import ToriiTestCase
from torii.test.mock                    import MockPlatform

from squishy.gateware.peripherals.spi   import SPIController, SPICPOL
from squishy.gateware.peripherals.psram import SPIPSRAM, SPIPSRAMCmd

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


		self.ready      = self._psram.ready
		self.done       = self._psram.done
		self.start_r    = self._psram.start_r
		self.start_w    = self._psram.start_w
		self.finish     = self._psram.finish
		self.rst_addrs  = self._psram.rst_addrs
		self.start_addr = self._psram.start_addr
		self.curr_addr  = self._psram.curr_addr
		self.byte_count = self._psram.byte_count

		self.itr = Signal(range(len(_PSRAM_DATA)))


	def elaborate(self, _) -> Module:
		m = Module()

		m.submodules.fifo  = self._fifo
		m.submodules.spi   = self._spi
		m.submodules.psram = self._psram

		with m.If(self._fifo.w_en):
			m.d.sync += [ self.itr.inc(), ]

		return m


class SPIPSRAMTests(ToriiTestCase):
	dut: DUTWrapper = DUTWrapper
	dut_args = { }
	domains = (('sync', 60e6), )
	platform = MockPlatform()

	def fill_fifo(self, byte: int, idx: int):
		final   = idx == len(_PSRAM_DATA) - 1
		do_cont = (idx & 1023) != 1023

		yield self.dut._fifo.w_en.eq(1)
		yield self.dut._fifo.w_data.eq(byte)
		yield
		yield self.dut._fifo.w_en.eq(0)
		yield from self.step(3)

		yield from self.spi_trans(
			copi_data = (byte,), partial = not final, continuation = True
		)

		# We are wrapping addresses
		if not do_cont:
			yield Settle()
			self.assertEqual((yield cs), 0)
			yield

			if not final:
				yield from self.spi_trans(
					copi_data = (SPIPSRAMCmd.WRITE, *(idx + 1).to_bytes(3, byteorder = 'big')), partial = True
				)

	def spi_trans(self, *,
		copi_data: tuple[int, ...] | None = None, cipo_data: tuple[int, ...] | None = None, partial: bool = False, continuation: bool = False
	):
		if cipo_data is not None and copi_data is not None:
			self.assertEqual(len(cipo_data), len(copi_data))

		bytes = max(0 if copi_data is None else len(copi_data), 0 if cipo_data is None else len(cipo_data))
		self.assertEqual((yield clk), 0)
		if continuation:
			yield Settle()
			self.assertEqual((yield cs), 1)
		else:
			self.assertEqual((yield cs), 0)
			yield Settle()
		yield
		self.assertEqual((yield clk), 0)
		self.assertEqual((yield cs), 1)
		yield Settle()
		# yield
		for byte in range(bytes):
			for bit in range(8):
				if bit == 0:
					self.assertEqual((yield clk), 0)
				else:
					self.assertEqual((yield clk), 1)
				self.assertEqual((yield cs), 1)
				yield Settle()
				if cipo_data is not None and cipo_data[byte] is not None:
					yield cipo.eq(((cipo_data[byte] << bit) & 0x80) >> 7)
				yield
				self.assertEqual((yield clk), 0)
				self.assertEqual((yield cs), 1)
				if copi_data is not None and copi_data[byte] is not None:
					self.assertEqual((yield copi), ((copi_data[byte] << bit) & 0x80) >> 7)
				yield Settle()
				yield
			if byte < bytes - 1:
				self.assertEqual((yield clk), 1)
				self.assertEqual((yield cs), 1)
			self.assertEqual((yield self.dut.done), 0)
			yield Settle()
			if cipo_data is not None and cipo_data[byte] is not None:
				yield cipo.eq(0)
			if byte < bytes - 1:
				yield
		if not partial:
			self.assertEqual((yield clk), 0)
			self.assertEqual((yield cs), 0)
			yield Settle()
			yield


	@ToriiTestCase.simulation
	@ToriiTestCase.sync_domain(domain = 'sync')
	def test_psram_write(self):
		yield
		# Check to ensure SPI bus is idle
		self.assertEqual((yield clk),  0)
		self.assertEqual((yield cs),   0)
		self.assertEqual((yield copi), 0)
		self.assertEqual((yield cipo), 0)
		# Setup the PSRAM Address stuff
		yield self.dut._psram.start_addr.eq(0)
		yield self.dut.rst_addrs.eq(1)
		yield Settle()
		yield
		yield self.dut.rst_addrs.eq(0)
		yield Settle()
		yield
		# Start a write
		yield self.dut.start_w.eq(1)
		yield self.dut.byte_count.eq(len(_PSRAM_DATA))
		yield Settle()
		yield
		yield self.dut.start_w.eq(0)
		yield Settle()
		self.assertEqual((yield self.dut.curr_addr), 0)
		self.assertEqual((yield self.dut.start_addr), 0)
		self.assertEqual((yield cs), 0)
		yield
		yield from self.spi_trans(copi_data = (SPIPSRAMCmd.WRITE, 0x00, 0x00, 0x00), partial = True)
		self.assertEqual((yield self.dut._fifo.r_rdy), 0)
		yield
		yield Settle()
		self.assertEqual((yield cs), 1)
		self.assertEqual((yield clk), 0)
		self.assertEqual((yield self.dut._fifo.r_rdy), 0)
		self.assertEqual((yield cs), 1)
		self.assertEqual((yield clk), 0)
		yield
		yield Settle()
		self.assertEqual((yield self.dut._fifo.r_rdy), 0)
		self.assertEqual((yield cs), 1)
		self.assertEqual((yield clk), 0)

		for idx, byte in enumerate(_PSRAM_DATA):
			yield from self.fill_fifo(byte, idx)

		self.assertEqual((yield self.dut.done), 1)
		# Check to ensure SPI bus is idle, again
		self.assertEqual((yield clk),  0)
		self.assertEqual((yield cs),   0)
		self.assertEqual((yield cipo), 0)
		# Set our transaction to be done
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
