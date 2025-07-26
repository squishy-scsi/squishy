# SPDX-License-Identifier: BSD-3-Clause

from torii.hdl                        import ClockDomain, Elaboratable, Module, Signal
from torii.lib.soc.csr.bus            import Element, Multiplexer
from torii.sim                        import Settle
from torii.test                       import ToriiTestCase
from torii.test.mock                  import MockPlatform

from squishy.gateware.peripherals.spi import SPICPOL, SPIController, SPIPeripheral
from squishy.support.test             import SPIGatewareTest

clk  = Signal(name = 'bus_clk' )
cs   = Signal(name = 'bus_cs'  )
copi = Signal(name = 'bus_copi')
cipo = Signal(name = 'bus_cipo')


class SPIControllerCLKHighTests(SPIGatewareTest):
	dut: SPIController = SPIController
	dut_args = {
		'clk': clk, 'cipo': cipo, 'copi': copi, 'cs': cs, 'cpol': SPICPOL.HIGH
	}
	domains = (('sync', 170e6), )
	platform = MockPlatform()

	def __init__(self, *args, **kwargs) -> None:
		super().__init__(*args, **kwargs)

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

class SPIControllerCLKLowTests(SPIGatewareTest):
	dut: SPIController = SPIController
	dut_args = {
		'clk': clk, 'cipo': cipo, 'copi': copi, 'cs': cs, 'cpol': SPICPOL.LOW
	}
	domains = (('sync', 170e6), )
	platform = MockPlatform()

	def __init__(self, *args, **kwargs) -> None:
		super().__init__(*args, **kwargs)

	def send_recv(self, d_out, d_in, ovlp = False):
		self.assertEqual((yield clk), 0)
		yield self.dut.wdat.eq(d_out)
		yield self.dut.xfr.eq(1)
		yield Settle()
		yield
		self.assertEqual((yield clk), 0)
		yield self.dut.xfr.eq(0)
		yield Settle()
		yield
		for bit in range(8):
			if bit == 0:
				self.assertEqual((yield clk), 0)
			else:
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
			self.assertEqual((yield clk), 0)
			self.assertEqual((yield self.dut.done), 0)
			self.assertEqual((yield self.dut.rdat), d_in)
		yield Settle()

	@ToriiTestCase.simulation
	@ToriiTestCase.sync_domain(domain = 'sync')
	def test_spi_controller(self):
		yield
		self.assertEqual((yield clk), 0)
		yield self.dut.cs.eq(1)
		yield Settle()
		yield
		yield from self.send_recv(0x0F, 0xF0)
		yield
		self.assertEqual((yield clk), 0)
		yield self.dut.cs.eq(0)
		yield Settle()
		yield
		self.assertEqual((yield clk), 0)
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

		self.csr_bus = self._reg_map.bus

	def elaborate(self, _) -> Module:
		m = Module()

		m.domains.test = ClockDomain()

		m.submodules.reg_map = self._reg_map
		m.submodules.spi     = self._spi

		return m

class SPIPeripheralTests(SPIGatewareTest):
	dut: PeripheralDUTWrapper = PeripheralDUTWrapper
	dut_args = { }
	domains  = (('sync', 100e6), ('test', 15e6))
	platform = MockPlatform()

	def __init__(self, *args, **kwargs) -> None:
		super().__init__(*args, **kwargs)

	def send_recv(self, addr: int | None, data_in: int, data_out: int, term: bool = True):
		self.assertEqual((yield clk), 0)
		# Select the peripheral so we go into `READ_ADDR`
		yield cs.eq(1)
		yield
		self.assertEqual((yield clk), 0)

		if addr is not None:
			for addr_bit in range(8):
				yield copi.eq((addr >> addr_bit) & 1)
				yield Settle()
				yield
				yield clk.eq(1)
				yield Settle()
				yield
				yield clk.eq(0)

		for bit in range(8):
			yield copi.eq((data_in >> bit) & 1)
			yield Settle()
			yield
			if bit >= 1:
				self.assertEqual((yield cipo), ((data_out >> (bit - 1)) & 1))
			yield clk.eq(1)
			yield Settle()
			yield
			yield clk.eq(0)
			yield Settle()
		if term:
			yield cs.eq(0)
		yield Settle()
		yield
		self.assertEqual((yield cipo), ((data_out >> 7) & 1))


	@ToriiTestCase.simulation
	def test_spi_peripheral(self):

		@ToriiTestCase.sync_domain(domain = 'sync')
		def sync_domain(self: SPIPeripheralTests):
			csr_bus = self.dut.csr_bus
			test1_r = self.dut.test1_r
			test2_r = self.dut.test2_r

			test2_w = self.dut.test2_w

			yield from self.wait_until_high(csr_bus.r_stb)
			self.assertEqual((yield csr_bus.addr), 1)
			yield
			self.assertEqual((yield csr_bus.r_data), 0)
			yield from self.wait_until_high(csr_bus.w_stb)
			self.assertEqual((yield csr_bus.addr), 1)
			self.assertEqual((yield csr_bus.w_data), 0xA5)
			yield Settle()
			yield
			yield Settle()
			self.assertEqual((yield test2_w), 0xA5)

			# Load the registers with data
			yield test1_r.eq(0x55)
			yield test2_r.eq(0x0F)
			yield from self.wait_until_high(csr_bus.r_stb)
			self.assertEqual((yield csr_bus.addr), 0)
			yield
			self.assertEqual((yield csr_bus.r_stb), 0)
			self.assertEqual((yield csr_bus.r_data), 0x55)
			yield from self.wait_until_high(csr_bus.w_stb)
			self.assertEqual((yield csr_bus.addr), 0)
			self.assertEqual((yield csr_bus.w_data), 0xF0)
			yield
			self.assertEqual((yield csr_bus.r_stb), 1)
			self.assertEqual((yield csr_bus.w_stb), 0)
			self.assertEqual((yield csr_bus.addr), 1)
			yield
			self.assertEqual((yield csr_bus.r_data), 0x0F)
			yield from self.wait_until_high(csr_bus.w_stb)
			self.assertEqual((yield csr_bus.addr), 1)
			self.assertEqual((yield csr_bus.w_data), 0xAA)


		@ToriiTestCase.sync_domain(domain = 'test')
		def spi_domain(self: SPIPeripheralTests):
			yield
			# Check to ensure SPI bus is idle
			self.assertEqual((yield clk),  0)
			self.assertEqual((yield cs),   0)
			self.assertEqual((yield copi), 0)
			self.assertEqual((yield cipo), 0)
			yield Settle()
			yield
			yield from self.send_recv(1, 0xA5, 0x00)
			yield
			yield from self.send_recv(0, 0xF0, 0x55, False)
			yield from self.send_recv(None, 0xAA, 0x0F, True)


		sync_domain(self)
		spi_domain(self)
