# SPDX-License-Identifier: BSD-3-Clause

from torii                            import Signal
from torii.sim                        import Settle
from torii.test                       import ToriiTestCase
from torii.test.mock                  import MockPlatform

from squishy.gateware.peripherals.spi import SPIInterface, SPIController, SPIPeripheral, SPIInterfaceMode

clk  = Signal()
cs   = Signal()
copi = Signal()
cipo = Signal()


class SPIControllerTests(ToriiTestCase):
	dut: SPIController = SPIController
	dut_args = {
		'clk': clk, 'cipo': cipo, 'copi': copi, 'cs': cs,
	}
	platform = MockPlatform()


	def send_recv(self, d_out, d_in, ovlp = False):
		self.assertEqual((yield clk), 1)
		yield self.dut.wdat.eq(d_out)
		yield self.dut.xfr.eq(1)
		yield Settle()
		yield
		self.assertEqual((yield clk), 1)
		yield self.dut.xfr.eq(0)
		yield Settle()
		yield
		for bit in range(8):
			self.assertEqual((yield clk), 1)
			yield cipo.eq((d_in >> (7 - bit)) & 1)
			yield Settle()
			yield
			self.assertEqual((yield clk), 0)
			self.assertEqual((yield copi), ((d_out >> (7 - bit)) & 1))
			yield Settle()
			yield
		self.assertEqual((yield clk), 1)
		self.assertEqual((yield self.dut.done), 1)
		if not ovlp:
			yield Settle()
			yield
			self.assertEqual((yield clk), 1)
			self.assertEqual((yield self.dut.done), 0)
			self.assertEqual((yield self.dut.rdat), d_in)
		yield Settle()

	@ToriiTestCase.simulation
	@ToriiTestCase.sync_domain(domain = 'sync')
	def test_spi(self):
		yield
		self.assertEqual((yield clk), 1)
		yield self.dut.cs.eq(1)
		yield Settle()
		yield
		yield from self.send_recv(0x0F, 0xF0)
		yield
		self.assertEqual((yield clk), 1)
		yield self.dut.cs.eq(0)
		yield Settle()
		yield
		self.assertEqual((yield clk), 1)
		yield self.dut.cs.eq(1)
		yield Settle()
		yield
		yield from self.send_recv(0xAA, 0x55, ovlp = True)
		yield from self.send_recv(0x55, 0xAA, ovlp = False)
		yield
		yield self.dut.cs.eq(0)
		yield Settle()
		yield
