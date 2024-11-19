# SPDX-License-Identifier: BSD-3-Clause

from torii                            import Signal, Module, Elaboratable
from torii.sim                        import Settle
from torii.test                       import ToriiTestCase
from torii.test.mock                  import MockPlatform

from torii.lib.soc.csr.bus            import Multiplexer, Element

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
	def test_spi_controller(self):
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


class TestRegisters(Multiplexer):
	def __init__(self, *, name: str | None = None) -> None:

		self._data_width = 8

		if name is None:
			name = type(self).__name__

		super().__init__(addr_width = 2, data_width = self._data_width, name = name)

		self._test1   = Element(self._data_width, Element.Access.RW,  name = 'test1')
		self._test2   = Element(self._data_width, Element.Access.RW,  name = 'test2')


		self.add(self._test1, addr = 0x0)
		self.add(self._test2, addr = 0x1)

		self.test1_r = Signal(8)
		self.test1_w = Signal(8)
		self.test2_r = Signal(8)
		self.test2_w = Signal(8)

	def elaborate(self, platform) -> Module:
		m = super().elaborate(platform)

		m.d.comb += [
			self._test1.r_data.eq(self.test1_r),
			self._test2.r_data.eq(self.test2_r),
		]

		with m.If(self._test1.w_stb):
			m.d.sync += [ self.test1_w.eq(self._test1.w_data), ]

		with m.If(self._test2.w_stb):
			m.d.sync += [ self.test2_w.eq(self._test2.w_data), ]

		return m



class PeripheralDUTWrapper(Elaboratable):
	def __init__(self) -> None:

		self._reg_map = TestRegisters()
		self._spi     = SPIPeripheral(
			clk = clk, cipo = cipo, copi = copi, cs = cs, reg_map = self._reg_map
		)

		self.test1_r = self._reg_map.test1_r
		self.test1_w = self._reg_map.test1_w
		self.test2_r = self._reg_map.test2_r
		self.test2_w = self._reg_map.test2_w

	def elaborate(self, _) -> Module:
		m = Module()

		m.submodules.reg_map = self._reg_map
		m.submodules.spi     = self._spi

		return m

class SPIPeripheralTests(ToriiTestCase):
	dut: PeripheralDUTWrapper = PeripheralDUTWrapper
	dut_args = { }
	domains  = (('sync', 100e6), ('spi', 15e6))
	platform = MockPlatform()

	@ToriiTestCase.simulation
	def test_spi_peripheral(self):

		@ToriiTestCase.sync_domain(domain = 'sync')
		def sync_domain(self: SPIPeripheralTests):
			yield

		@ToriiTestCase.sync_domain(domain = 'spi')
		def spi_domain(self: SPIPeripheralTests):
			yield


		sync_domain(self)
		spi_domain(self)
