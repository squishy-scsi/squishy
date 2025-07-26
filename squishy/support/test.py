# SPDX-License-Identifier: BSD-3-Clause

'''
Squishy support infrastructure for testing.

This module contains 6 classes which augment the standard :py:class:`torii.test.ToriiTestCase` with additional
functionality to help with writing and running Squishy-related gateware tests. They are as follows:

	* :py:class:`SquishyGatewareTest` - Generalized test parent, all other test classes are derived from this.
	* :py:class:`USBGatewarePHYTest` - Tests for end-to-end USB interface tests, contains machinery for driving Torii-USB Gateware USB PHY
	* :py:class:`USBGatewareTest` - A more general set of USB interface tests, directly drives the Torii-USB USB interface.
	* :py:class:`DFUGatewareTest` - Augments the :py:class:`USBGatewareTest` with DFU helpers.
	* :py:class:`SPIGatewareTest` - Tests for SPI related gateware, contains helpers for driving a SPI bus for tests.
	* :py:class:`SCSIGatewareTest` - Tests for SCSI related gateware.

'''

from collections.abc                          import Iterable
from typing                                   import Literal

from torii.sim                                import Settle
from torii.test                               import ToriiTestCase
from usb_construct.types                      import (
	LanguageIDs, USBPacketID, USBRequestRecipient, USBRequestType, USBStandardRequests
)
from usb_construct.types.descriptors.dfu      import DFURequests
from usb_construct.types.descriptors.standard import StandardDescriptorNumbers

__all__ = (
	'SquishyGatewareTest',
	'USBGatewarePHYTest',
	'USBGatewareTest',
	'DFUGatewareTest',
	'SPIGatewareTest',
	'SCSIGatewareTest',

)

class SquishyGatewareTest(ToriiTestCase):
	'''
	The base class for the more specialized Squishy subsystem tests.

	'''

	def __init__(self, *args, **kwargs):
		self.domains = (*self.domains,)
		super().__init__(*args, **kwargs)


class USBGatewarePHYTest(SquishyGatewareTest):
	'''
	Unlike :py:class:`USBGatewareTest`, this mixin is used for end-to-end USB tests where we emulate a physical USB
	bus, this helps test end-to-end integration.

	To use this, the DUT platform rather than returning a ULPI or UTMI resource should return a DirectUSB resource, this
	will cause Torii-USB to use it's gateware PHY and we can then manually drive D+ and D- for tests.

	Parameters
	----------
	raw_record : torii.hdl.rec.Record
		The Raw Torii Record representing the USB bus for the Gateware PHY.
		It must have 2 members `d_p` and `d_n`, each with `i`, `o`, and `oe` sub-members, all
		1-bit wide.

	'''

	_USB_DP_RECORD = None
	_last_frame: int = 0
	_last_state: Literal['j', 'k'] | None = None
	_last_trans: int = 0
	_last_data: USBPacketID | None = None

	def __init__(self, *args, raw_record, **kwargs):
		self.domains = (('usb', 12e6), ('usb_io', 48e6), *self.domains)
		super().__init__(*args, **kwargs)

		self._USB_DP_RECORD = raw_record

	@staticmethod
	def crc5(data: int, bit_len: int) -> int:
		'''
		Compute the CRC5 for the USB packet.

		Parameters
		----------
		data : int
			The byte we are computing the CRC5 for.

		bit_len : int
			The number of bits we are computing the CRC5 over.

		Returns
		-------
		int:
			The CRC5 of `bin(data)[0:bit_len]`.
		'''

		crc = 0x1F

		for bit_idx in range(bit_len):
			bit = (data >> bit_idx) & 1
			crc <<= 1

			if bit != (crc >> 5):
				crc ^= 0x25
			crc &= 0x1F

		crc ^= 0x1F
		return int(f'{crc:05b}'[::-1], base = 2)

	@staticmethod
	def crc16(data: int, bit_len: int, crc_in: int = 0) -> int:
		'''
		Computes the CRC16 of the given byte for the USB traffic.

		Parameters
		----------
		data : int
			The current byte to compute the CRC16 on.

		bit_len : int
			The number of bits of `data` to compute the CRC16 over.

		crc_in : int
			The result of a previous call to `crc16` if iterating over a buffer of data.

		Returns
		-------
		int
			The output CRC16 value.
		'''

		crc = int(f'{crc_in ^ 0xFFFF:016b}'[::-1], base = 2)

		for bit_idx in range(bit_len):
			bit = (data >> bit_idx) & 1
			crc <<= 1

			if bit != (crc >> 16):
				crc ^= 0x18005
			crc &= 0xFFFF

		crc ^= 0xFFFF
		return int(f'{crc:016b}'[::-1], base = 2)

	@staticmethod
	def crc16_buff(data: Iterable[int]) -> int:
		'''
		Compute the CRC16 value of a buffer of bytes.

		Parameters
		----------
		data : Iterable[int]
			The buffer of bytes to compute the CRC16 for

		Returns
		-------
		int
			The CRC16 value of the data buffer.
		'''

		crc = 0
		for byte in data:
			crc = USBGatewarePHYTest.crc16(byte, 8, crc)
		return crc

	def usb_emit_bits(self, bits: int, count: int = 8):
		'''
		Emit appropriate K and J symbols to put raw bits onto the USB bus.

		Parameters
		----------
		bits : int
			The bits to put out on the wire.

		count : int
			The number of bits in `bits` to use. (default: 8)
		'''

		for bit_idx in range(count):
			bit = (bits >> bit_idx) & 1
			if bit == 0:
				self._last_trans = 0
				match self._last_state:
					case 'k':
						yield from self.usb_j()
						self._last_state = 'j'
					case 'j':
						yield from self.usb_k()
						self._last_state = 'k'
					case _:
						yield from self.usb_j()
						self._last_state = 'j'
			else:
				self._last_trans += 1
				match self._last_state:
					case 'k':
						yield from self.usb_k()
					case 'j':
						yield from self.usb_j()

				# Do bit-stuffing if we need to
				if self._last_trans == 6:
					self._last_trans = 0
					match self._last_state:
						case 'k':
							yield from self.usb_j()
							self._last_state = 'j'
						case 'j':
							yield from self.usb_k()
							self._last_state = 'k'

	def usb_single_zero(self):
		'''
		Emit a single-ended USB 0 onto the bus.

		This drives the input side of D+ and D- on the USB record to 0:

			D+: ┈┈┈┈🮢＿＿
			D-: ┈┈┈┈🮢＿＿
		'''

		yield self._USB_DP_RECORD.d_p.i.eq(0)
		yield self._USB_DP_RECORD.d_n.i.eq(0)
		yield Settle()
		yield

	def usb_single_one(self):
		'''
		Emit a single-ended USB 1 onto the bus.

		This drives the input side of D+ and D- on the USB record to 1:

			D+: ┈┈┈┈🮠￣￣
			D-: ┈┈┈┈🮠￣￣
		'''

		yield self._USB_DP_RECORD.d_p.i.eq(1)
		yield self._USB_DP_RECORD.d_n.i.eq(1)
		yield Settle()
		yield

	def usb_j(self):
		'''
		Emit a USB J symbol onto the bus.

		This drives the input side of D+ high and D- low:

			D+: ┈┈┈┈🮠￣￣
			D-: ┈┈┈┈🮢＿＿
		'''

		yield self._USB_DP_RECORD.d_p.i.eq(1)
		yield self._USB_DP_RECORD.d_n.i.eq(0)
		yield Settle()
		yield

	def usb_wait_j(self):
		''' Wait up to 1000 cycles for the output side of the USB bus to have a J symbol emitted to it '''

		yield from self.wait_until_high(self._USB_DP_RECORD.d_p.o, timeout = 1e3)
		yield from self.usb_assert_j()

	def usb_assert_j(self):
		''' Assert that the current state of the output side of the USB bus is a valid J symbol. '''

		self.assertEqual((yield self._USB_DP_RECORD.d_p.o), 1)
		self.assertEqual((yield self._USB_DP_RECORD.d_n.o), 0)

	def usb_k(self):
		'''
		Emit a USB K symbol onto the bus.

		This drives the input side of D+ low and D- high:

			D+: ┈┈┈┈🮢＿＿
			D-: ┈┈┈┈🮠￣￣
		'''

		yield self._USB_DP_RECORD.d_p.i.eq(0)
		yield self._USB_DP_RECORD.d_n.i.eq(1)
		yield Settle()
		yield

	def usb_wait_k(self):
		''' Wait up to 1000 cycles for the output side of the USB bus to have a K symbol emitted to it '''

		yield from self.wait_until_high(self._USB_DP_RECORD.d_n.o, timeout = 1e3)
		yield from self.usb_assert_k()

	def usb_assert_k(self):
		''' Assert that the current state of the output side of the USB bus is a valid K symbol. '''

		self.assertEqual((yield self._USB_DP_RECORD.d_n.o), 1)
		self.assertEqual((yield self._USB_DP_RECORD.d_p.o), 0)

	def usb_initialize(self):
		'''
		Emit a USB bus initialization sequence which consists of a USB 0 for 30µs followed by a USB 1 for 1µs.
		'''

		yield from self.usb_single_zero()
		yield from self.wait_for(30e-6, 'usb')
		yield from self.usb_single_one()
		yield from self.wait_for(1e-6, 'usb')

	def usb_sync(self):
		'''
		Emit a USB sync onto the bus.

		This puts a pattern of `KJKJKJKK` onto the bus.
		'''

		yield from self.usb_emit_bits(0x100, 9)

	def usb_assert_sync(self):
		''' Assert that a USB sync has been emitted onto the bus. '''

		yield from self.usb_wait_k()
		for _ in range(3):
			yield
			yield from self.usb_assert_j()
			yield
			yield from self.usb_assert_k()
		yield
		yield from self.usb_assert_k()
		yield


	def usb_eop(self):
		'''
		Emit a USB End-of-packet onto the bus.

		This puts 2 USB 0's followed by a J symbols and then a USB 1 onto the bus.
		'''

		yield from self.usb_single_zero()
		yield from self.usb_single_zero()
		yield from self.usb_j()
		yield from self.usb_single_one()
		self._last_state = None

	def usb_sof(self, frame_number: int | None = None):
		'''
		Emit a USB Start-of-Frame.

		Parameters
		----------
		frame_number : int | None
			The frame number to use.
		'''

		yield from self.usb_sync()
		yield from self.usb_emit_bits(USBPacketID.SOF.byte())

		if frame_number is not None:
			self._last_frame = frame_number

		yield from self.usb_emit_bits(self._last_frame, 11)
		yield from self.usb_emit_bits(self.crc5(self._last_frame, 11), 5)
		yield from self.usb_eop()

		self._last_frame += 1

	def usb_in(self, addr: int, ep: int):
		'''
		Emit a USB IN packet.

		Parameters
		----------
		addr : int
			The address of the device.

		ep : int
			The endpoint for the IN packet.
		'''

		yield from self.usb_solicit(addr, ep, USBPacketID.IN)

	def usb_out(self, addr: int, ep: int):
		'''
		Emit a USB OUT packet.

		Parameters
		----------
		addr : int
			The address of the device.

		ep : int
			The endpoint for the OUT packet.
		'''

		yield from self.usb_solicit(addr, ep, USBPacketID.OUT)

	def usb_setup(self, addr: int):
		'''
		Emit a USB Setup packet.

		Parameters
		----------
		addr : int
			The address of the device.
		'''

		self._last_data = None
		yield from self.usb_solicit(addr, 0, USBPacketID.SETUP)

	def usb_send_ack(self):
		''' Send a USB ACK '''

		yield from self.usb_sync()
		yield from self.usb_emit_bits(USBPacketID.ACK.byte())
		yield from self.usb_eop()

	def usb_get_ack(self):
		''' Get a USB ACK '''
		yield from self.usb_consume_response((USBPacketID.ACK.byte(),))

	def usb_get_stall(self):
		''' Get a USB Stall '''

		yield from self.usb_consume_response((USBPacketID.STALL.byte(),))

	def usb_solicit(self, addr: int, ep: int, pid: USBPacketID):
		'''
		Solicit a USB packet.

		Parameters
		----------
		addr : int
			The address of the device.

		ep : int
			The device endpoint.

		pid : USBPacketID
			The ID of the packet.

		'''

		yield from self.usb_sync()
		yield from self.usb_emit_bits(pid.byte())
		yield from self.usb_emit_bits(addr, 7)
		yield from self.usb_emit_bits(ep, 4)
		yield from self.usb_emit_bits(self.crc5((addr | (ep << 7)), 11), 5)
		yield from self.usb_eop()

	def usb_data(self, data: Iterable[int]):
		'''
		Emit a USB DATA packet.

		Parameters
		----------
		data : Iterable[int]
			The date in the packet.
		'''

		if self._last_data is None or self._last_data == USBPacketID.DATA1:
			self._last_data = USBPacketID.DATA0
		else:
			self._last_data = USBPacketID.DATA1

		yield from self.usb_sync()
		yield from self.usb_emit_bits(self._last_data.byte())
		crc = 0
		for byte in data:
			crc = self.crc16(byte, 8, crc)
			yield from self.usb_emit_bits(byte)
		yield from self.usb_emit_bits(crc, 16)
		yield from self.usb_eop()

	def usb_get_zlp(self):
		''' Assert that the USB bus has a ZLP emitted. '''
		yield from self.usb_consume_response((USBPacketID.DATA1.byte(), 0x00, 0x00))

	def usb_send_zlp(self):
		''' Emit a USB Zero-length-packet. '''

		yield from self.usb_data(())

	def usb_send_setup_pkt(self, addr: int, data: Iterable[int]):
		'''
		Emit a USB Setup packet.

		Parameters
		----------
		addr : int
			The target device address.

		data : Iterable[int]
			The data in the setup packet.
		'''

		yield from self.usb_setup(addr)
		yield from self.usb_data(data)
		yield from self.usb_get_ack()
		yield from self.step(10)


	def usb_set_addr(self, addr: int):
		'''
		Emit a USB Set Address packet.

		Parameters
		----------
		addr : int
			The address to set the device to.
		'''

		yield from self.usb_send_setup_pkt(0, (
			0x00, USBStandardRequests.SET_ADDRESS,
			*addr.to_bytes(2, byteorder = 'little'), 0x00, 0x00, 0x00, 0x00
		))
		yield from self.usb_in(0x00, 0x00)
		yield from self.usb_get_zlp()
		yield from self.usb_send_ack()

	def usb_set_interface(self, addr: int, interface: int, alt: int):
		'''
		Emit a USB Set Interface packet.

		Parameters
		----------
		addr : int
			The address of the device.

		interface : int
			The interface to set active.

		alt : int
			The alternate mode of the interface to use.
		'''

		yield from self.usb_send_setup_pkt(addr, (
			0x01, USBStandardRequests.SET_INTERFACE,
			*alt.to_bytes(2, byteorder = 'little'),
			*interface.to_bytes(2, byteorder = 'little'),
			0x00, 0x00
		))
		yield from self.usb_in(addr, 0)
		yield from self.usb_get_zlp()
		yield from self.usb_send_ack()

	def usb_set_config(self, addr: int, cfg: int):
		'''
		Emit a USB Set Configuration packet.

		Parameters
		----------
		addr : int
			The address of the device.

		cfg : int
			The configuration to set active.
		'''

		yield from self.usb_send_setup_pkt(addr, (
			0x00, USBStandardRequests.SET_CONFIGURATION,
			*cfg.to_bytes(2, byteorder = 'little'), 0x00, 0x00, 0x00, 0x00
		))
		yield from self.usb_in(addr, 0x00)
		yield from self.usb_get_zlp()
		yield from self.usb_send_ack()

	def usb_get_config(self, addr: int, cfg: int):
		'''
		Emit a USB Get Configuration packet and assert it's correct.

		Parameters
		----------
		addr : int
			The address of the device.

		cfg : int
			The configuration to assert against.
		'''

		crc = self.crc16_buff((cfg, ))

		yield from self.usb_send_setup_pkt(addr, (
			0x80, USBStandardRequests.GET_CONFIGURATION,
			0x00, 0x00, 0x00, 0x00, *(1).to_bytes(2, byteorder = 'little')
		))
		yield from self.usb_in(addr, 0x00)
		yield from self.usb_consume_response((
			USBPacketID.DATA1.byte(), cfg, *crc.to_bytes(2, byteorder = 'little')
		))
		yield from self.usb_send_ack()
		yield from self.step(20)
		yield from self.usb_out(addr, 0)
		yield from self.usb_send_zlp()
		yield from self.usb_get_ack()

	def usb_get_string(self, addr: int, string_idx: int, string: str):
		'''
		Emit a USB Get String packet and assert it matches the expected value.

		Parameters
		----------
		addr : int
			The address of the device.

		string_idx : int
			The index of the string descriptor to get.

		string : str
			The expected string.
		'''

		string_bytes = string.encode(encoding = 'utf-16le')
		data = (len(string_bytes) + 2, StandardDescriptorNumbers.STRING, *string_bytes)

		yield from self.usb_send_setup_pkt(addr, (
			0x80, USBStandardRequests.GET_DESCRIPTOR, string_idx, StandardDescriptorNumbers.STRING,
			*LanguageIDs.ENGLISH_US.to_bytes(2, byteorder = 'little'), *(255).to_bytes(2, byteorder = 'little')
		))
		last_data = USBPacketID.DATA0
		for offset in range(0, len(data), 64):
			chunk = data[offset : offset + 64]
			crc = self.crc16_buff(chunk)
			match last_data:
				case USBPacketID.DATA0:
					last_data = USBPacketID.DATA1
				case USBPacketID.DATA1:
					last_data = USBPacketID.DATA0

			yield from self.usb_in(addr, 0x00)
			yield from self.usb_consume_response((
				last_data.byte(), *chunk, *crc.to_bytes(2, byteorder = 'little')
			))
			yield from self.usb_send_ack()
			yield from self.step(20)
		yield from self.usb_out(addr, 0)
		yield from self.usb_send_zlp()
		yield from self.usb_get_ack()

	def usb_get_state(self):
		''' Return the state of the USB bus outgoing side. '''

		dp = yield self._USB_DP_RECORD.d_p.o
		dn = yield self._USB_DP_RECORD.d_n.o
		yield
		match (dp, dn):
			case (0, 1):
				return 'k'
			case (1, 0):
				return 'j'
			case (0, 0):
				return '0'
			case (1, 1):
				return '1'

	def usb_consume_byte(self):
		'''
		Read a byte off the USB bus.

		Returns
		-------
		int
			The byte read.
		'''

		res = 0
		for bit in range(8):
			res >>= 1
			state = yield from self.usb_get_state()
			if self._last_state != state:
				self._last_trans = 0
				res |= 0x00
			else:
				self._last_trans += 1
				if self._last_trans == 6:
					state = yield from self.usb_get_state()
					self.assertNotEqual(state, self._last_state)
					self._last_trans = 0
				res |= 0x80

			self._last_state = state
		return res

	def usb_consume_response(self, data: Iterable[int]):
		'''
		Consume bytes of off the USB bus and assert it matches `data`.

		Parameters
		----------
		data : Iterable[int]
			The collection of bytes to assert against.
		'''


		yield from self.usb_assert_sync()
		self._last_state = 'k'

		for byte in data:
			self.assertEqual((yield from self.usb_consume_byte()), byte)

		self.assertEqual((yield from self.usb_get_state()), '0')
		self.assertEqual((yield from self.usb_get_state()), '0')
		self.assertEqual((yield from self.usb_get_state()), 'j')

		self._last_state = None


class USBGatewareTest(SquishyGatewareTest):
	'''
	Unlike :py:class:`USBGatewarePHYTest`, this class relies on access to a Torii-USB interface exposed in the DUT
	or DUT wrapper.

	Most of the USB tests in Squishy use this type of helpers, as the :py:class:`USBGatewarePHYTest` is only
	used for full end-to-end USB integration validation if absolutely needed.
	'''

	def __init__(self, *args, **kwargs):
		self.domains = (('usb', 60e6), *self.domains)
		super().__init__(*args, **kwargs)


	def setup_received(self):
		''' Trigger a setup received event on the USB interface. '''

		yield self.dut.interface.setup.received.eq(1)
		yield Settle()
		yield
		yield self.dut.interface.setup.received.eq(0)
		yield Settle()
		yield
		yield

	def send_setup(
		self, *, type: USBRequestType, retrieve: bool, req, value: tuple[int, int] | int, index: tuple[int, int] | int,
		length: int, recipient: USBRequestRecipient = USBRequestRecipient.INTERFACE
	):
		'''
		Inject a setup packet into the USB interface.

		Parameters
		----------
		type : USBRequestType
			The type of this USB request.

		retrieve : bool
			If this is an IN request or not.

		req
			The request.

		value : tuple[int, int] | int
			The one or two byte value of the setup packet.

		index : tuple[int, int] | int
			The one or two byte index of the setup packet.

		length : int
			The length of the setup packet.

		recipient : USBRequestRecipient
			The recipient for this setup packet. (default: USBRequestRecipient.INTERFACE)
		'''

		yield self.dut.interface.setup.recipient.eq(recipient)
		yield self.dut.interface.setup.type.eq(type)
		yield self.dut.interface.setup.is_in_request.eq(1 if retrieve else 0)
		yield self.dut.interface.setup.request.eq(req)
		if isinstance(value, int):
			yield self.dut.interface.setup.value.eq(value)
		else:
			yield self.dut.interface.setup.value[0:8].eq(value[0])
			yield self.dut.interface.setup.value[8:16].eq(value[1])
		if isinstance(index, int):
			yield self.dut.interface.setup.index.eq(index)
		else:
			yield self.dut.interface.setup.index[0:8].eq(index[0])
			yield self.dut.interface.setup.index[8:16].eq(index[1])
		yield self.dut.interface.setup.length.eq(length)
		yield from self.setup_received()

	def send_setup_set_interface(self, *, interface: int = 0, alt_mode: int = 0):
		'''
		Inject a Set Interface packet into the USB interface.

		Parameters
		----------
		interface : int
			The interface to set. (default: 0)

		alt_mode : int
			The alternate mode of the interface. (default: 0)
		'''

		yield from self.send_setup(
			type     = USBRequestType.STANDARD,
			retrieve = False,
			req      = USBStandardRequests.SET_INTERFACE,
			value    = alt_mode,
			index    = interface,
			length   = 0
		)

	def receive_data(self, *, data: tuple[int, ...] | bytes, check: bool = True):
		'''
		Assert that the USB interface sends the expected data.

		Parameters
		----------
		data : tuple[int, ...] | bytes
			The data we expect from the interface.

		check : bool
			Enable the assert on the data send back from the interface. (default: true)
		'''

		result = True
		yield self.dut.interface.tx.ready.eq(1)
		yield self.dut.interface.data_requested.eq(1)
		yield Settle()
		yield
		yield self.dut.interface.data_requested.eq(0)
		self.assertEqual((yield self.dut.interface.tx.valid), 0)
		self.assertEqual((yield self.dut.interface.tx.data), 0)
		while (yield self.dut.interface.tx.first) == 0:
			yield Settle()
			yield
		for idx, val in enumerate(data):
			self.assertEqual((yield self.dut.interface.tx.first), (1 if idx == 0 else 0))
			self.assertEqual((yield self.dut.interface.tx.last), (1 if idx == len(data) - 1 else 0))
			self.assertEqual((yield self.dut.interface.tx.valid), 1)
			if check:
				self.assertEqual((yield self.dut.interface.tx.data), val)
			if (yield self.dut.interface.tx.data) != val:
				result = False
			self.assertEqual((yield self.dut.interface.handshakes_out.ack), 0)
			if idx == len(data) - 1:
				yield self.dut.interface.tx.ready.eq(0)
				yield self.dut.interface.status_requested.eq(1)
			yield Settle()
			yield
		self.assertEqual((yield self.dut.interface.tx.valid), 0)
		self.assertEqual((yield self.dut.interface.tx.data), 0)
		self.assertEqual((yield self.dut.interface.handshakes_out.ack), 1)
		yield self.dut.interface.status_requested.eq(0)
		yield Settle()
		yield
		self.assertEqual((yield self.dut.interface.handshakes_out.ack), 0)
		return result

	def receive_zlp(self):
		''' Assert that the USB interface emits a ZLP '''

		self.assertEqual((yield self.dut.interface.tx.valid), 0)
		self.assertEqual((yield self.dut.interface.tx.last), 0)
		yield self.dut.interface.status_requested.eq(1)
		yield Settle()
		yield
		self.assertEqual((yield self.dut.interface.tx.valid), 1)
		self.assertEqual((yield self.dut.interface.tx.last), 1)
		yield self.dut.interface.status_requested.eq(0)
		yield self.dut.interface.handshakes_in.ack.eq(1)
		yield Settle()
		yield
		self.assertEqual((yield self.dut.interface.tx.valid), 0)
		self.assertEqual((yield self.dut.interface.tx.last), 0)
		yield self.dut.interface.handshakes_in.ack.eq(0)
		yield Settle()
		yield

	def send_data(self, *, data: tuple[int, ...] | bytes):
		'''
		Inject data into the USB interface.

		Parameters
		----------
		data : tuple[int, ...] | bytes
			The data to inject.
		'''

		yield self.dut.interface.rx.valid.eq(1)
		for val in data:
			yield Settle()
			yield
			yield self.dut.interface.rx.data.eq(val)
			yield self.dut.interface.rx.next.eq(1)
			yield Settle()
			yield
			yield self.dut.interface.rx.next.eq(0)
		yield self.dut.interface.rx.valid.eq(0)
		yield self.dut.interface.rx_ready_for_response.eq(1)
		yield Settle()
		yield
		yield self.dut.interface.rx_ready_for_response.eq(0)
		yield self.dut.interface.status_requested.eq(1)
		yield Settle()
		yield
		yield self.dut.interface.status_requested.eq(0)
		yield self.dut.interface.handshakes_in.ack.eq(1)
		yield Settle()
		yield
		yield self.dut.interface.handshakes_in.ack.eq(0)
		yield Settle()
		yield

	def ensure_stall(self):
		''' Assert that the USB interface emits a stall. '''

		yield self.dut.interface.tx.ready.eq(1)
		yield self.dut.interface.data_requested.eq(1)
		yield Settle()
		yield
		yield self.dut.interface.data_requested.eq(0)
		attempts = 0

		while (yield self.dut.interface.handshakes_out.stall) == 0:
			self.assertEqual((yield self.dut.interface.tx.valid), 0)
			attempts += 1
			if attempts > 10:
				self.fail('Stall took too long')
			yield Settle()
			yield
		yield Settle()
		yield


	def send_get_desc(self, *, vendor_code, length, index):
		'''
		Inject a Get Descriptor request into the USB interface.

		Parameters
		----------
		vendor_code
			The vendor code for the descriptor.

		length
			The length of the descriptor.

		index
			The index of the descriptor.
		'''

		yield from self.send_setup(
			type = USBRequestType.VENDOR, retrieve = True,
			req = vendor_code, value = 0, index = index,
			length = length, recipient = USBRequestRecipient.DEVICE
		)

class DFUGatewareTest(SquishyGatewareTest):
	'''
	Provides helper wrappers for USB-DFU related test driving with the :py:class:`USBGatewareTest` class.
	'''

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)


	def send_dfu_detach(self):
		''' Inject a DFU Detach into the USB interface. '''

		yield from self.send_setup(
			type = USBRequestType.CLASS, retrieve = False, req = DFURequests.DETACH, value = 1000, index = 0, length = 0
		)

	def send_dfu_download(self, *, length: int = 256):
		'''
		Inject a DFU download of the given length into the USB interface.

		Parameters
		----------
		length : int
			The size of the DFU download. (default: 256)
		'''

		yield from self.send_setup(
			type = USBRequestType.CLASS, retrieve = False, req = DFURequests.DOWNLOAD, value = 0, index = 0, length = length
		)

	def send_dfu_get_status(self):
		''' Inject a DFU Get Status into the USB interface. '''

		yield from self.send_setup(
			type = USBRequestType.CLASS, retrieve = True, req = DFURequests.GET_STATUS, value = 0, index = 0, length = 6
		)

	def send_dfu_get_state(self):
		''' Inject a DFU Get State into the USB interface. '''

		yield from self.send_setup(
			type = USBRequestType.CLASS, retrieve = True, req = DFURequests.GET_STATE, value = 0, index = 0, length = 1
		)

class SPIGatewareTest(SquishyGatewareTest):
	'''

	'''

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)



class SCSIGatewareTest(SquishyGatewareTest):
	''' '''

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
