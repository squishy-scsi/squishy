# SPDX-License-Identifier: BSD-3-Clause

from torii.sim                        import Settle
from torii.test                       import ToriiTestCase
from torii.test.mock                  import MockPlatform

from squishy.gateware.peripherals.spi import SPIInterface

class SPIInterfaceTests(ToriiTestCase):
	dut: SPIInterface = SPIInterface
	dut_args = {
		'resource_name': ('spi_flash_1x', 0)
	}
	platform = MockPlatform()


	def send_recv(self, d_out, d_in, ovlp = False):
		self.assertEqual((yield self.dut._spi.clk.o), 1)
		yield self.dut.wdat.eq(d_out)
		yield self.dut.xfr.eq(1)
		yield Settle()
		yield
		self.assertEqual((yield self.dut._spi.clk.o), 1)
		yield self.dut.xfr.eq(0)
		yield Settle()
		yield
		for bit in range(8):
			self.assertEqual((yield self.dut._spi.clk.o), 1)
			yield self.dut._spi.cipo.i.eq((d_in >> (7 - bit)) & 1)
			yield Settle()
			yield
			self.assertEqual((yield self.dut._spi.clk.o), 0)
			self.assertEqual((yield self.dut._spi.copi.o), ((d_out >> (7 - bit)) & 1))
			yield Settle()
			yield
		self.assertEqual((yield self.dut._spi.clk.o), 1)
		self.assertEqual((yield self.dut.done), 1)
		if not ovlp:
			yield Settle()
			yield
			self.assertEqual((yield self.dut._spi.clk.o), 1)
			self.assertEqual((yield self.dut.done), 0)
			self.assertEqual((yield self.dut.rdat), d_in)
		yield Settle()

	@ToriiTestCase.simulation
	@ToriiTestCase.sync_domain(domain = 'sync')
	def test_spi(self):
		yield
		self.assertEqual((yield self.dut._spi.clk.o), 1)
		yield self.dut.cs.eq(1)
		yield Settle()
		yield
		yield from self.send_recv(0x0F, 0xF0)
		yield
		self.assertEqual((yield self.dut._spi.clk.o), 1)
		yield self.dut.cs.eq(0)
		yield Settle()
		yield
		self.assertEqual((yield self.dut._spi.clk.o), 1)
		yield self.dut.cs.eq(1)
		yield Settle()
		yield
		yield from self.send_recv(0xAA, 0x55, ovlp = True)
		yield from self.send_recv(0x55, 0xAA, ovlp = False)
		yield
		yield self.dut.cs.eq(0)
		yield Settle()
		yield
