# SPDX-License-Identifier: BSD-3-Clause

from os                          import getenv
from random                      import randbytes
from typing                      import Literal, Iterable

from torii                       import Record, Elaboratable, Module, Signal
from torii.hdl.rec               import DIR_FANIN, DIR_FANOUT
from torii.sim                   import Settle
from torii.test                  import ToriiTestCase

from usb_construct.types         import USBPacketID, USBStandardRequests

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

	def elaborate(self, _) -> Module:
		m = Module()

		m.submodules.bootloader = self.bootloader

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
			yield from self.usb_ack()
			yield from self.step(20)
			yield from self.usb_out(ADDR, 0)
			yield from self.usb_send_zlp()
			yield from self.usb_ack()
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
