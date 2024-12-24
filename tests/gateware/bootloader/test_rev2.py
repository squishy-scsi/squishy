# SPDX-License-Identifier: BSD-3-Clause

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

_DFU_DATA = randbytes(256)

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

	@ToriiTestCase.simulation
	def test_integration(self):
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
			yield

		dfu(self)
		psram(self)
		supervisor(self)
