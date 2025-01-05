# SPDX-License-Identifier: BSD-3-Clause

from os                          import getenv
from random                      import randbytes
from typing                      import Literal, Iterable

from torii                       import Record, Elaboratable, Module, Signal
from torii.hdl.rec               import DIR_FANIN, DIR_FANOUT
from torii.sim                   import Settle
from torii.test                  import ToriiTestCase

from usb_construct.types         import USBPacketID, USBStandardRequests
from usb_construct.types.descriptors.dfu import DFURequests

from squishy.core.config         import FlashConfig
from squishy.core.flash          import Geometry
from squishy.support.test        import SquishyGatewareTest, USBGatewarePHYTestHelpers
from squishy.core.dfu            import DFUState, DFUStatus


from squishy.gateware.bootloader import SquishyBootloader

__all__ = ()

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

_USB_RECORD = Record((
	('d_p', [
		('o',  1, DIR_FANOUT),
		('i',  1, DIR_FANIN ),
		('oe', 1, DIR_FANOUT),
	]),
	('d_n', [
		('o',  1, DIR_FANOUT),
		('i',  1, DIR_FANIN ),
		('oe', 1, DIR_FANOUT),
	])
))

_LEDS = (
	Record((('o', 1, DIR_FANOUT),)),
	Record((('o', 1, DIR_FANOUT),)),
	Record((('o', 1, DIR_FANOUT),)),
	Record((('o', 1, DIR_FANOUT),)),
	Record((('o', 1, DIR_FANOUT),)),
	Record((('o', 1, DIR_FANOUT),)),
	Record((('o', 1, DIR_FANOUT),)),
)

class DUTPlatformClockGenerator(Elaboratable):
	def __init__(self) -> None:
		self.pll_locked = Signal()

	def elaborate(self, platform: 'DUTPlatform') -> Module:
		m = Module()

		m.d.comb += [ self.pll_locked.eq(1), ]

		return m

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

	clk_domain_generator = DUTPlatformClockGenerator
	ephemeral_slot = 3
	device = 'TEST'

	SIM_PLATFORM = True

	def request(self, name: str, number: int):
		match name:
			case 'supervisor':
				return _SUPERVISOR_RECORD
			case 'ulpi':
				return _USB_RECORD
			case 'led':
				return _LEDS[number]
			case _:
				pass

class DUTWrapper(Elaboratable):
	def __init__(self) -> None:
		self.bootloader = SquishyBootloader(serial_number = 'TEST', revision = (2, 0))

		self.d_p = Signal()
		self.d_n = Signal()

	def elaborate(self, _) -> Module:
		m = Module()

		m.submodules.bootloader = self.bootloader

		with m.If(_USB_RECORD.d_p.oe):
			m.d.comb += [ self.d_p.eq(_USB_RECORD.d_p.o), ]
		with m.Else():
			m.d.comb += [ self.d_p.eq(_USB_RECORD.d_p.i), ]

		with m.If(_USB_RECORD.d_n.oe):
			m.d.comb += [ self.d_n.eq(_USB_RECORD.d_n.o), ]
		with m.Else():
			m.d.comb += [ self.d_n.eq(_USB_RECORD.d_n.i), ]

		return m


class BootloaderTests(USBGatewarePHYTestHelpers, SquishyGatewareTest):
	dut: SquishyBootloader = SquishyBootloader
	dut_args = {
		'serial_number': 'TEST',
		'revision': (2, 0),
	}
	domains  = (('sync', 170e6), )
	platform = DUTPlatform()

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs, raw_record = _USB_RECORD)

	def dfu_get_status(self, *, addr: int, exepected_status: DFUStatus, expected_state: DFUState):
		data = (exepected_status, 0x00, 0x00, 0x00, expected_state, 0x00)
		crc = self.crc16_buff(data)

		# Send the SETUP packet to the device
		yield from self.usb_send_setup_pkt(addr, (0xA1,  DFURequests.GET_STATUS, 0x00, 0x00, 0x00, 0x00, 0x06, 0x00,))
		yield from self.step(20)
		# Now solicit a response for the 6 bytes needed
		yield from self.usb_in(addr, 0)
		yield from self.usb_consume_response((
			USBPacketID.DATA1.byte(), *data, *crc.to_bytes(2, byteorder = 'little')
		))
		# ACK that response
		yield from self.usb_send_ack()
		yield from self.step(20)
		# Finish up by sending the status phase to ack our end of the bargain
		yield from self.usb_out(addr, 0)
		yield from self.usb_send_zlp()
		yield from self.usb_get_ack()


	@ToriiTestCase.simulation
	def test_integration(self):
		ADDR = 0xACA7 & 0x7F

		@ToriiTestCase.sync_domain(domain = 'usb')
		def usb(self: BootloaderTests):
			yield from self.usb_single_one()
			yield from self.step(20)
			yield from self.usb_initialize()
			yield from self.step(20)
			yield from self.usb_sof()
			yield from self.step(20)
			yield from self.usb_set_addr(ADDR)
			yield from self.step(20)
			yield from self.usb_set_config(ADDR, 1)
			yield from self.step(20)
			yield from self.usb_send_setup_pkt(ADDR, (0x81, 0x06, 0x00, 0x22, 0x00, 0x00, 0x10, 0x01,))
			yield from self.step(20)
			yield from self.usb_in(ADDR, 0)
			yield from self.usb_get_stall()
			yield from self.step(20)
			yield from self.usb_send_setup_pkt(ADDR, (0xA1, 0x03, 0x00, 0x00, 0x00, 0x00, 0x06, 0x00,))
			yield from self.step(20)
			yield from self.usb_in(ADDR, 0)
			data = (DFUStatus.Okay, 0x00, 0x00, 0x00, DFUState.DFUIdle, 0x00)
			crc = 0
			for byte in data:
				crc = self.crc16(byte, 8, crc)

			yield from self.usb_consume_response((
				USBPacketID.DATA1.byte(), *data, *crc.to_bytes(2, byteorder = 'little')
			))
			yield from self.step(20)
			yield from self.usb_send_ack()
			yield from self.step(20)
			yield from self.usb_out(ADDR, 0)
			yield from self.usb_send_zlp()
			yield from self.usb_get_ack()
			yield from self.step(200)




		@ToriiTestCase.sync_domain(domain = 'usb_io')
		def usb_io(self: BootloaderTests):
			yield

		@ToriiTestCase.sync_domain(domain = 'sync')
		def sync(self: BootloaderTests):
			yield from self.step(50)


		usb(self)
		usb_io(self)
		sync(self)
