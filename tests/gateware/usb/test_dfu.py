# SPDX-License-Identifier: BSD-3-Clause

from torii                               import Record, Elaboratable, Module
from torii.hdl.rec                       import DIR_FANIN, DIR_FANOUT
from torii.lib.fifo                      import AsyncFIFO
from torii.sim                           import Settle
from torii.test                          import ToriiTestCase
from usb_construct.types                 import USBRequestType
from usb_construct.types.descriptors.dfu import DFURequests

from squishy.support.test                import SquishyUSBGatewareTest
from squishy.gateware.usb.dfu            import DFURequestHandler, DFUState
from squishy.core.config                 import FlashConfig
from squishy.core.flash                  import Geometry

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

	def request(self, name, number):
		return _SPI_RECORD

class DFURequestHandlerStubTests(SquishyUSBGatewareTest):
	dut: DFURequestHandler = DFURequestHandler
	dut_args = {
		'configuration': 1,
		'interface': 0,
		'boot_stub': True
	}

	def sendDFUDetach(self):
		yield from self.sendSetup(
			type = USBRequestType.CLASS, retrieve = False, req = DFURequests.DETACH, value = 1000, index = 0, length = 0
		)

	def sendDFUGetStatus(self):
		yield from self.sendSetup(
			type = USBRequestType.CLASS, retrieve = True, req = DFURequests.GET_STATUS, value = 0, index = 0, length = 6
		)

	@ToriiTestCase.simulation
	@ToriiTestCase.sync_domain(domain = 'usb')
	def test_dfu_stub(self):
		self.assertEqual((yield self.dut.slot_selection), 0)
		yield self.dut.interface.active_config.eq(1)
		yield Settle()
		yield
		yield from self.sendSetupSetInterface()
		yield from self.receiveZLP()
		yield
		yield
		yield
		yield from self.sendDFUGetStatus()
		yield from self.receiveData(data = (0, 0, 0, 0, DFUState.AppIdle, 0))
		yield from self.sendDFUDetach()
		yield from self.receiveZLP()
		self.assertEqual((yield self.dut.trigger_reboot), 1)
		self.assertEqual((yield self.dut.slot_selection), 0)


class DUTWrapper(Elaboratable):
	def __init__(self) -> None:
		self.fifo = AsyncFIFO(
			width = 8, depth = DFUPlatform.flash.geometry.erase_size, r_domain = 'usb', w_domain = 'usb'
		)

		self.dfu = DFURequestHandler(1, 0, False, fifo = self.fifo)

		self.interface = self.dfu.interface

	def elaborate(self, platform) -> Module:
		m = Module()

		m.submodules.fifo = self.fifo
		m.submodules.dfu  = self.dfu

		return m

# TODO(aki): We need to build a DUTWrapper for this test now
class DFURequestHandlerTests(SquishyUSBGatewareTest):
	dut: DUTWrapper = DUTWrapper
	dut_args = {

	}
	domains = (('usb', 60e6),)
	platform = DFUPlatform()

	def sendDFUDetach(self):
		yield from self.sendSetup(
			type = USBRequestType.CLASS, retrieve = False, req = DFURequests.DETACH, value = 1000, index = 0, length = 0
		)

	def sendDFUDownload(self):
		yield from self.sendSetup(
			type = USBRequestType.CLASS, retrieve = False, req = DFURequests.DOWNLOAD, value = 0, index = 0, length = 256
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
	@ToriiTestCase.sync_domain(domain = 'usb')
	def test_dfu_handler(self):
		# Setup the active interface
		yield self.dut.dfu.interface.active_config.eq(1)
		yield Settle()
		yield from self.step(2)
		yield from self.wait_until_low(_SPI_RECORD.cs.o)
		yield from self.step(2)
		# Have the backing storage/programming interface tell the DFU state machine  it's happy
		yield Settle()
		yield
		yield self.dut.dfu.dl_ready.eq(1)
		yield Settle()
		yield
		yield self.dut.dfu.dl_ready.eq(0)
		yield Settle()
		yield
		# Make sure we're in Idle
		yield from self.sendDFUGetStatus()
		yield from self.receiveData(data = (0, 0, 0, 0, DFUState.DFUIdle, 0))
		# Set the interface up
		yield from self.sendSetupSetInterface(interface = 0, alt_mode = 1)
		yield from self.receiveZLP()
		yield from self.step(3)
		self.assertEqual((yield self.dut.dfu.slot_selection), 1)
		# Have the backing programmer tell the DFU state machine we've updated the slot
		yield Settle()
		yield
		yield self.dut.dfu.slot_ack.eq(1)
		yield Settle()
		yield
		yield self.dut.dfu.slot_ack.eq(0)
		yield Settle()
		yield
		# Yeet the data
		yield from self.sendDFUDownload()
		yield from self.sendData(data = _DFU_DATA)
		yield from self.sendDFUGetStatus()
		yield from self.receiveData(data = (0, 0, 0, 0, DFUState.DlBusy, 0))
		yield from self.sendDFUGetState()
		yield from self.receiveData(data = (DFUState.DlBusy, ))
		yield from self.step(6)
		# The backing storage is chewing on the data, just spin for a bit
		for _ in range(5):
			yield from self.sendDFUGetState()
			yield from self.receiveData(data = (DFUState.DlBusy, ), check = False)
		yield from self.step(3)
		# Have the backing storage tell the DFU FSM that we have ingested the data
		yield Settle()
		yield
		yield self.dut.dfu.dl_done.eq(1)
		yield Settle()
		yield
		yield self.dut.dfu.dl_done.eq(0)
		yield Settle()
		yield
		# Make sure we're in sync
		yield from self.sendDFUGetState()
		yield from self.receiveData(data = (DFUState.DlSync,))
		yield from self.sendDFUGetStatus()
		yield from self.receiveData(data = (0, 0, 0, 0, DFUState.DlSync, 0))
		# And back to Idle
		yield from self.sendDFUGetState()
		yield from self.receiveData(data = (DFUState.DlIdle,))
		yield
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
