# SPDX-License-Identifier: BSD-3-Clause
import logging                          as log

from enum                               import IntEnum, unique
from struct                             import pack, unpack
from typing                             import Tuple, Union

from amaranth                           import (
	Module, Signal, DomainRenamer, Cat, Memory, Const
)
from amaranth.hdl.ast                   import Operator
from amaranth.lib.fifo                  import AsyncFIFO

from usb_protocol.types                 import (
	USBRequestType, USBRequestRecipient, USBStandardRequests
)
from usb_protocol.types.descriptors.dfu import DFURequests

from luna.gateware.usb.usb2.request     import (
	USBRequestHandler, SetupPacket
)
from luna.gateware.usb.stream           import (
	USBInStreamInterface, USBOutStreamInterface
)
from luna.gateware.stream.generator     import (
	StreamSerializer
)

from ...core.flash                      import FlashGeometry

from ..core.flash                       import SPIFlash

__all__ = (
	'DFURequestHandler',
)


@unique
class DFUState(IntEnum):
	Idle   = 2
	DlSync = 3
	DlBusy = 4
	DlIdle = 5
	UpIdle = 9
	Error  = 10

@unique
class DFUStatus(IntEnum):
	Okay = 0


class DFUConfig:
	def __init__(self) -> None:
		self.status = Signal(4, decoder = DFUStatus)
		self.state  = Signal(4, decoder = DFUState)


class DFURequestHandler(USBRequestHandler):
	def __init__(self, *, interface: int, resource_name: Tuple[str, int]):
		super().__init__()

		self._interface = interface
		self._flash     = resource_name

		self.triggerReboot = Signal()


	def elaborate(self, platform) -> Module:
		m = Module()

		interface          = self.interface
		setup: SetupPacket = interface.setup

		rxTrig = Signal()
		rxStream = USBOutStreamInterface(payload_width = 8)

		recvStart = Signal()
		recvCount = Signal.like(setup.length)
		recvConsumed = Signal.like(setup.length)

		slot = Signal(8)


		_flash: dict[str, Union[dict[str, int], FlashGeometry]] = platform.flash
		cfg = DFUConfig()

		m.submodules.bitstream_fifo = bitstream_fifo = AsyncFIFO(
			width = 8, depth = _flash['geometry'].erase_size, r_domain = 'usb', w_domain = 'usb'
		)

		flash: SPIFlash = DomainRenamer({'sync': 'usb'})(
			SPIFlash(flash_resource = self._flash, flash_geometry = platform.flash['geometry'], fifo = bitstream_fifo)
		)
		m.submodules.flash = flash

		m.submodules.transmitter = transmitter = StreamSerializer(
			data_length = 6, domain = 'usb', stream_type = USBInStreamInterface, max_length_width = 3
		)

		slot_rom = self._make_rom(_flash)

		m.submodules.slots = slots = slot_rom.read_port(domain = 'usb', transparent = False)

		m.d.comb += [
			flash.start.eq(0),
			flash.finish.eq(0),
			flash.resetAddrs.eq(0),
		]

		with m.FSM(domain = 'usb', name = 'dfu'):
			with m.State('RESET'):
				m.d.usb += [
					cfg.status.eq(DFUStatus.Okay),
					cfg.state.eq(DFUState.Idle),
					slot.eq(0)
				]
				with m.If(flash.ready):
					m.next = 'READ_SLOT_DATA'

			with m.State('IDLE'):
				with m.If(setup.received & self.handlerCondition(setup)):
					with m.If(setup.type == USBRequestType.CLASS):
						with m.Switch(setup.request):
							with m.Case(DFURequests.DETACH):
								m.next = 'HANDLE_DETACH'
							with m.Case(DFURequests.DOWNLOAD):
								m.next = 'HANDLE_DOWNLOAD'
							with m.Case(DFURequests.GET_STATUS):
								m.next = 'HANDLE_GET_STATUS'
							with m.Case(DFURequests.CLR_STATUS):
								m.next = 'HANDLE_CLR_STATUS'
							with m.Case(DFURequests.GET_STATE):
								m.next = 'HANDLE_GET_STATE'
							with m.Default():
								m.next = 'UNHANDLED'
					with m.Elif(setup.type == USBRequestType.STANDARD):
						with m.Switch(setup.request):
							with m.Case(USBStandardRequests.GET_INTERFACE):
								m.next = 'GET_INTERFACE'
							with m.Case(USBStandardRequests.SET_INTERFACE):
								m.next = 'SET_INTERFACE'
							with m.Default():
								m.next = 'UNHANDLED'

					with m.If(flash.done):
						m.d.comb += [
							flash.finish.eq(1),
						]

						m.d.usb += [
							cfg.state.eq(DFUState.DlSync)
						]

			with m.State('HANDLE_DETACH'):
				m.d.comb += [
					self.triggerReboot.eq(1),
				]

			with m.State('HANDLE_DOWNLOAD'):
				with m.If(setup.is_in_request | (setup.length > _flash['geometry'].erase_size)):
					m.next = 'UNHANDLED'
				with m.Elif(setup.length):
					m.d.comb += [
						flash.start.eq(1),
						flash.byteCount.eq(setup.length),
					]
					m.d.usb += [
						cfg.state.eq(DFUState.DlBusy),
					]
					m.next = 'HANDLE_DOWNLOAD_DATA'

			with m.State('HANDLE_DOWNLOAD_DATA'):
				m.d.comb += [
					interface.rx.connect(rxStream)
				]
				with m.If(~rxTrig):
					m.d.comb += [
						recvStart.eq(1),
					]
					m.d.usb += [
						rxTrig.eq(1),
					]

				with m.If(interface.rx_ready_for_response):
					m.d.comb += [
						interface.handshakes_out.ack.eq(1),
					]

				with m.If(interface.status_requested):
					m.d.comb += [
						self.send_zlp(),
					]
				with m.If(self.interface.handshakes_in.ack):
					m.d.usb += [
						rxTrig.eq(0),
					]
					m.next = 'IDLE'

			with m.State('HANDLE_DOWNLOAD_COMPLETE'):
				with m.If(interface.status_requested):
					m.d.usb += [
						cfg.state.eq(DFUState.Idle),
					]
					m.d.comb += [
						self.send_zlp(),
					]

				with m.If(interface.handshakes_in.ack):
					m.next = 'IDLE'

			with m.State('HANDLE_GET_STATUS'):
				m.d.comb += [
					transmitter.stream.connect(interface.tx),
					transmitter.max_length.eq(6),
				]

				m.d.comb += [
					transmitter.data[0].eq(cfg.status),
					Cat(transmitter.data[1:4]).eq(0),
					transmitter.data[4].eq(Cat(cfg.state, 0)),
					transmitter.data[5].eq(0),
				]

				with m.If(self.interface.data_requested):
					with m.If(setup.length == 6):
						m.d.comb += [
							transmitter.start.eq(1),
						]
					with m.Else():
						m.d.comb += [
							interface.handshakes_out.stall.eq(1),
						]
						m.next = 'IDLE'
				with m.If(interface.status_requested):
					m.d.comb += [
						interface.handshakes_out.ack.eq(1),
					]
					with m.If(cfg.state == DFUState.DlSync):
						m.d.usb += [
							cfg.state.eq(DFUState.DlIdle)
						]
					m.next = 'IDLE'

			with m.State('HANDLE_CLR_STATUS'):
				with m.If(setup.length == 0):
					with m.If(cfg.state == DFUState.Error):
						m.d.usb += [
							cfg.status.eq(DFUStatus.Okay),
							cfg.state.eq(DFUState.Idle),
						]
				with m.Else():
					m.d.comb += [
						interface.handshakes_out.stall.eq(1),
					]
					m.next = 'IDLE'

				with m.If(interface.status_requested):
					m.d.comb += [
						self.send_zlp(),
					]
				with m.If(interface.handshakes_in.ack):
					m.next = 'IDLE'

			with m.State('HANDLE_GET_STATE'):
				m.d.comb += [
					transmitter.stream.connect(interface.tx),
					transmitter.max_length.eq(1),
				]

				m.d.comb += [
					transmitter.data[0].eq(Cat(cfg.state, 0))
				]

				with m.If(self.interface.data_requested):
					with m.If(setup.length == 1):
						m.d.comb += [
							transmitter.start.eq(1),
						]
					with m.Else():
						m.d.comb += [
							interface.handshakes_out.stall.eq(1),
						]
						m.next = 'IDLE'

				with m.If(interface.status_requested):
					m.d.comb += [
						interface.handshakes_out.ack.eq(1),
					]
					m.next = 'IDLE'

			with m.State('GET_INTERFACE'):
				m.d.comb += [
					transmitter.stream.connect(interface.tx),
					transmitter.max_length.eq(1),
				]

				m.d.comb += [
					transmitter.data[0].eq(slot)
				]

				with m.If(self.interface.data_requested):
					with m.If(setup.length == 1):
						m.d.comb += [
							transmitter.start.eq(1)
						]
					with m.Else():
						m.d.comb += [
							interface.handshakes_out.stall.eq(1)
						]
						m.next = 'IDLE'

				with m.If(interface.status_requested):
					m.d.comb += [
						interface.handshakes_out.ack.eq(1)
					]
					m.next = 'IDLE'

			with m.State('SET_INTERFACE'):
				with m.If(interface.status_requested):
					m.d.comb += [
						self.send_zlp()
					]

				with m.If(interface.handshakes_in.ack):
					m.d.usb += [
						slot.eq(setup.value[0:8]),
					]
					m.next = 'READ_SLOT_DATA'

			with m.State('UNHANDLED'):
				with m.If(interface.data_requested | interface.status_requested):
					m.d.comb += [
						interface.handshakes_out.stall.eq(1),
					]
					m.next = 'IDLE'

			with m.State('READ_SLOT_DATA'):
				m.d.comb += [
					slots.addr.eq(Cat(Const(0, 1), slot)),
				]
				m.next = 'READ_SLOT_BEGIN'

			with m.State('READ_SLOT_BEGIN'):
				m.d.comb += [
					slots.addr.eq(Cat(Const(1, 1), slot)),
				]
				m.d.usb += [
					flash.startAddr.eq(slots.data),
				]
				m.next = 'READ_SLOT_END'

			with m.State('READ_SLOT_END'):
				m.d.usb += [
					flash.endAddr.eq(slots.data),
				]
				m.d.comb += [
					flash.resetAddrs.eq(1),
				]
				m.next = 'IDLE'

		m.d.comb += [
			bitstream_fifo.w_en.eq(0),
			bitstream_fifo.w_data.eq(rxStream.payload)
		]
		recvCont = (recvConsumed  < recvCount)

		with m.FSM(domain = 'usb', name = 'download'):
			with m.State('IDLE'):
				m.d.usb += [
					recvConsumed.eq(0),
				]

				with m.If(recvStart):
					m.d.usb += [
						recvCount.eq(setup.length - 1),
					]
					m.next = 'STREAMING'
			with m.State('STREAMING'):
				with m.If(rxStream.valid & rxStream.next):
					m.d.comb += [
						bitstream_fifo.w_en.eq(1),
					]

					with m.If(recvCont):
						m.d.usb += [
							recvConsumed.eq(recvConsumed + 1),
						]
					with m.Else():
						m.next = 'IDLE'

		return m

	def handlerCondition(self, setup: SetupPacket) -> Operator:
		return (
			((setup.type == USBRequestType.CLASS) | (setup.type == USBRequestType.STANDARD)) &
			(setup.recipient == USBRequestRecipient.INTERFACE)                               &
			(setup.index == self._interface)
		)


	def _make_rom(self, flash: dict[str, Union[dict[str, int], FlashGeometry]]) -> Memory:
		total_size = flash['geometry'].slots * 8

		rom = bytearray(total_size)
		rom_addr = 0
		for partition in range(flash['geometry'].slots):
			slot = flash['geometry'].partitions[partition]
			addr_range = pack('>II', slot['start_addr'], slot['end_addr'])
			rom[rom_addr:rom_addr + 8] = addr_range
			rom_addr += 8

		rom_entries = (rom[i:i + 4] for i in range(0, total_size, 4))
		initializer = [unpack('>I', rom_entry)[0] for rom_entry in rom_entries]
		return Memory(width = 24, depth = flash['geometry'].slots * 2, init = initializer)
