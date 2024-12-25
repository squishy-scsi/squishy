# SPDX-License-Identifier: BSD-3-Clause

from os                                  import getenv
from random                              import randbytes

from torii                               import Record, Elaboratable, Module, ClockDomain, Signal
from torii.hdl.rec                       import DIR_FANIN, DIR_FANOUT
from torii.lib.fifo                      import AsyncFIFO
from torii.sim                           import Settle
from torii.test                          import ToriiTestCase

from usb_construct.types                 import USBRequestType
from usb_construct.types.descriptors.dfu import DFURequests

from squishy.support.test                import SquishyUSBGatewareTest
from squishy.core.config                 import FlashConfig
from squishy.core.flash                  import Geometry

from squishy.gateware.usb.dfu            import DFURequestHandler, DFUState
from squishy.gateware.bootloader.rev2    import Rev2
from squishy.gateware.peripherals.psram  import SPIPSRAMCmd

if getenv('GITHUB_WORKSPACE') is not None:
	_DFU_DATA = randbytes(1536) # 1024 to get an addr wrap + a bit
else:
	_DFU_DATA = randbytes(4096) # :nocov:


_SUPERVISOR_RECORD = Record((
	('clk', [
		('o', 1 , DIR_FANOUT),
		('i',  1, DIR_FANIN ),
		('oe', 1, DIR_FANOUT),
	]),
	('copi', [
		('o',  1, DIR_FANOUT),
		('i',  1, DIR_FANIN ),
		('oe', 1, DIR_FANOUT),
	]),
	('cipo', [
		('o',  1, DIR_FANOUT),
		('i',  1, DIR_FANIN ),
		('oe', 1, DIR_FANOUT),
	]),
	('attn', [
		('i',  1, DIR_FANIN ),
	]),
	('psram', [
		('o',  1, DIR_FANOUT ),
	]),
	('su_irq', [
		('o',  1, DIR_FANOUT ),
	]),
	('bus_hold', [
		('o',  1, DIR_FANOUT ),
	]),
))

class DUTPlatform:
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
		return _SUPERVISOR_RECORD

class DUTWrapper(Elaboratable):
	def __init__(self) -> None:
		self.fifo = AsyncFIFO(
			width = 8, depth = 4096, r_domain = 'sync', w_domain = 'usb'
		)

		self.dfu  = DFURequestHandler(1, 0, False, fifo = self.fifo)
		self.rev2 = Rev2(self.fifo)

		self.interface = self.dfu.interface

	def elaborate(self, _) -> Module:
		m = Module()

		m.submodules.fifo = self.fifo
		m.submodules.dfu  = self.dfu
		m.submodules.rev2 = self.rev2

		m.domains.supervisor = ClockDomain()

		sclk = Signal()

		m.d.comb += [
			self.rev2.trigger_reboot.eq(self.dfu.trigger_reboot),
			self.rev2.slot_selection.eq(self.dfu.slot_selection),
			self.rev2.slot_changed.eq(self.dfu.slot_changed),
			self.rev2.dl_start.eq(self.dfu.dl_start),
			self.rev2.dl_finish.eq(self.dfu.dl_finish),
			self.rev2.dl_size.eq(self.dfu.dl_size),
			self.rev2.dl_completed.eq(self.dfu.dl_completed),
			self.dfu.slot_ack.eq(self.rev2.slot_ack),
			self.dfu.dl_ready.eq(self.rev2.dl_ready),
			self.dfu.dl_done.eq(self.rev2.dl_done),
		]

		m.d.supervisor += [
			sclk.eq(~sclk),
		]

		return m


class Rev2BootloaderTests(SquishyUSBGatewareTest):
	dut: DUTWrapper = DUTWrapper
	dut_args = {}
	domains  = (('usb', 60e6), ('sync', 80e6), ('supervisor', 36e6),)
	platform = DUTPlatform()

	def sendDFUDetach(self):
		yield from self.sendSetup(
			type = USBRequestType.CLASS, retrieve = False, req = DFURequests.DETACH, value = 1000, index = 0, length = 0
		)

	def sendDFUDownload(self, len: int):
		yield from self.sendSetup(
			type = USBRequestType.CLASS, retrieve = False, req = DFURequests.DOWNLOAD, value = 0, index = 0, length = len
		)

	def sendDFUGetStatus(self):
		yield from self.sendSetup(
			type = USBRequestType.CLASS, retrieve = True, req = DFURequests.GET_STATUS, value = 0, index = 0, length = 6
		)

	def sendDFUGetState(self):
		yield from self.sendSetup(
			type = USBRequestType.CLASS, retrieve = True, req = DFURequests.GET_STATE, value = 0, index = 0, length = 1
		)

	def send_recv(self, addr: int | None, data_in: int, data_out: int, term: bool = True):
		self.assertEqual((yield _SUPERVISOR_RECORD.clk.i), 0)
		# Select the peripheral so we go into `READ_ADDR`
		yield _SUPERVISOR_RECORD.attn.i.eq(1)
		yield
		self.assertEqual((yield _SUPERVISOR_RECORD.clk.i), 0)

		if addr is not None:
			for addr_bit in range(8):
				yield _SUPERVISOR_RECORD.copi.i.eq((addr >> addr_bit) & 1)
				yield Settle()
				yield
				yield _SUPERVISOR_RECORD.clk.i.eq(1)
				yield Settle()
				yield
				yield _SUPERVISOR_RECORD.clk.i.eq(0)
		for bit in range(8):
			yield _SUPERVISOR_RECORD.copi.i.eq((data_in >> bit) & 1)
			yield Settle()
			yield
			yield _SUPERVISOR_RECORD.clk.i.eq(1)
			yield Settle()
			yield
			yield _SUPERVISOR_RECORD.clk.i.eq(0)
			yield Settle()
			if bit >= 1:
				self.assertEqual((yield _SUPERVISOR_RECORD.cipo.o), ((data_out >> (bit - 1)) & 1))
		if term:
			yield _SUPERVISOR_RECORD.attn.i.eq(0)
		yield Settle()
		yield
		self.assertEqual((yield _SUPERVISOR_RECORD.cipo.o), ((data_out >> 7) & 1))

	@ToriiTestCase.simulation
	def test_integration(self):
		PAYLOAD_SIZE = len(_DFU_DATA).to_bytes(2, byteorder = 'little')

		@ToriiTestCase.sync_domain(domain = 'usb')
		def dfu(self: Rev2BootloaderTests):
			# Setup the active interface
			yield self.dut.dfu.interface.active_config.eq(1)
			yield Settle()
			yield from self.wait_until_high(self.dut.dfu.dl_ready)
			# Make sure we're in Idle
			yield from self.sendDFUGetStatus()
			yield from self.receiveData(data = (0, 0, 0, 0, DFUState.DFUIdle, 0))
			# Set the interface up
			yield from self.sendSetupSetInterface(interface = 0, alt_mode = 1)
			yield from self.receiveZLP()
			self.assertEqual((yield self.dut.dfu.slot_selection), 1)
			yield from self.wait_until_high(self.dut.dfu.slot_ack)
			yield from self.step(3)
			# Yeet the data
			yield from self.sendDFUDownload(len = len(_DFU_DATA))
			yield from self.sendData(data = _DFU_DATA)
			yield from self.sendDFUGetStatus()
			yield from self.receiveData(data = (0, 0, 0, 0, DFUState.DlBusy, 0))
			yield from self.sendDFUGetState()
			yield from self.receiveData(data = (DFUState.DlBusy, ))
			yield from self.step(6)
			yield from self.sendDFUGetState()
			# The backing storage is chewing on the data, just spin for a bit
			while (yield from self.receiveData(data = (DFUState.DlBusy,), check = False)):
				yield from self.sendDFUGetState()
			yield from self.step(3)
			# Make sure we're in sync
			yield from self.sendDFUGetState()
			yield from self.receiveData(data = (DFUState.DlSync,))
			yield from self.sendDFUGetStatus()
			yield from self.receiveData(data = (0, 0, 0, 0, DFUState.DlSync, 0))
			# And back to Idle
			yield from self.sendDFUGetState()
			yield from self.receiveData(data = (DFUState.DlIdle,))
			yield
			yield from self.sendDFUDownload(len = 0)
			yield from self.sendData(data = ())
			# And trigger a reboot
			self.assertEqual((yield self.dut.dfu.trigger_reboot), 0)
			yield from self.sendDFUDetach()
			yield from self.receiveZLP()
			self.assertEqual((yield self.dut.dfu.trigger_reboot), 1)
			yield Settle()
			yield
			self.assertEqual((yield self.dut.dfu.trigger_reboot), 1)
			yield
			yield from self.step(10)

		@ToriiTestCase.sync_domain(domain = 'sync')
		def psram(self: Rev2BootloaderTests):
			yield

		@ToriiTestCase.sync_domain(domain = 'supervisor')
		def supervisor(self: Rev2BootloaderTests):
			yield
			# Ensure the whole SPI bus is idle
			self.assertEqual((yield _SUPERVISOR_RECORD.clk.i),       0)
			self.assertEqual((yield _SUPERVISOR_RECORD.su_irq.o),    0)
			self.assertEqual((yield _SUPERVISOR_RECORD.bus_hold.o),  0)
			self.assertEqual((yield _SUPERVISOR_RECORD.attn.i),      0)
			self.assertEqual((yield _SUPERVISOR_RECORD.psram.o),     0)
			self.assertEqual((yield _SUPERVISOR_RECORD.copi.o),      0)
			self.assertEqual((yield _SUPERVISOR_RECORD.cipo.i),      0)
			yield Settle()
			yield
			# wait until `bus_hold` goes high, then ensure it and `su_irq` are as expected later
			yield from self.wait_until_high(_SUPERVISOR_RECORD.bus_hold.o, timeout = 50)
			yield from self.step(50)
			yield
			self.assertEqual((yield _SUPERVISOR_RECORD.bus_hold.o), 1)
			self.assertEqual((yield _SUPERVISOR_RECORD.su_irq.o), 0)
			# Now, we need to wait until the FPGA gateware is done dumping DFU stuff into PSRAM,
			# We time out just in case `su_irq` is never actually called in a reasonable amount of time
			yield from self.wait_until_high(_SUPERVISOR_RECORD.su_irq.o, timeout = 50000)
			yield
			# We need to now read the IRQ register, the problem is that's internal so we need to actually
			# run the SPI transaction to pull the value out and check it.
			yield from self.send_recv(4, 0x00, 0x02)
			yield
			# With the proper IRQ, we then read the slots register
			yield from self.send_recv(1, 0x00, 0x11)
			yield
			# Now we read the txlen register
			yield from self.send_recv(2, 0x00, PAYLOAD_SIZE[0])
			yield
			yield from self.send_recv(3, 0x00, PAYLOAD_SIZE[1])
			yield
			# We got the slot and txlen we expected, ack the IRQ
			yield from self.send_recv(0, 0b0000_0010, 0x00)
			yield
			# Now we emulate a *really fast* erase/write
			yield from self.step(50)
			# instruct the bootloader that we did the thing
			yield from self.send_recv(0, 0b0000_0001, 0x00)
			yield
			# Now we wait for the FPGA to tell us to reboot
			yield from self.wait_until_high(_SUPERVISOR_RECORD.su_irq.o, timeout = 128)
			yield
			# Okay, FPGA wants to tell us something, it should be that it wants a reboot
			yield from self.send_recv(4, 0x00, 0x04)
			yield
			# We can now reboot the FPGA, tests pass on our end

		dfu(self)
		psram(self)
		supervisor(self)
