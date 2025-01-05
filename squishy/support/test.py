# SPDX-License-Identifier: BSD-3-Clause

'''

This module contains support infrastructure for gateware testing.

There are two test harnesses, the first being :py:class:`SquishyUSBGatewareTest` which is
specialized for testing gateware that runs in the USB clock domain and/or has USB specific
functionality. The second is :py:class:`SquishySCSIGatewareTest` which is like the harness
for USB, but directed at SCSI instead.

'''

from typing                              import Literal, Iterable

from torii.sim                           import Settle
from torii.test                          import ToriiTestCase

from usb_construct.types                 import USBRequestRecipient, USBRequestType, USBStandardRequests, USBPacketID
from usb_construct.types.descriptors.dfu import DFURequests

__all__ = (
	'SquishyGatewareTest',
	'USBGatewarePHYTestHelpers',
	'USBGatewareTestHelpers',
	'DFUGatewareTestHelpers',
	'SPIGatewareTestHelpers',
	'SCSIGatewareTestHelpers',
)

class USBGatewarePHYTestHelpers:
	'''
	Unlike :py:class:`USBGatewareTestHelpers`, this mixin is used for end-to-end USB tests where we emulate a physical USB
	bus, this helps test end-to-end integration.

	To use this, the DUT platform rather than returning a ULPI or UTMI resource should return a DirectUSB resource, this
	will cause SOL to use it's gateware PHY and we can then manually drive D+ and D- for tests.
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
		crc = int(f'{crc_in ^ 0xFFFF:016b}'[::-1], base = 2)

		for bit_idx in range(bit_len):
			bit = (data >> bit_idx) & 1
			crc <<= 1

			if bit != (crc >> 16):
				crc ^= 0x18005
			crc &= 0xFFFF

		crc ^= 0xFFFF
		return int(f'{crc:016b}'[::-1], base = 2)

	def usb_emit_bits(self, bits: int, count: int = 8):
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
		yield self._USB_DP_RECORD.d_p.i.eq(0)
		yield self._USB_DP_RECORD.d_n.i.eq(0)
		yield Settle()
		yield

	def usb_single_one(self):
		yield self._USB_DP_RECORD.d_p.i.eq(1)
		yield self._USB_DP_RECORD.d_n.i.eq(1)
		yield Settle()
		yield

	def usb_j(self):
		yield self._USB_DP_RECORD.d_p.i.eq(1)
		yield self._USB_DP_RECORD.d_n.i.eq(0)
		yield Settle()
		yield

	def usb_wait_j(self):
		yield from self.wait_until_high(self._USB_DP_RECORD.d_p.o, timeout = 1e4)
		yield from self.usb_assert_j()

	def usb_assert_j(self):
		self.assertEqual((yield self._USB_DP_RECORD.d_p.o), 1)
		self.assertEqual((yield self._USB_DP_RECORD.d_n.o), 0)

	def usb_k(self):
		yield self._USB_DP_RECORD.d_p.i.eq(0)
		yield self._USB_DP_RECORD.d_n.i.eq(1)
		yield Settle()
		yield

	def usb_wait_k(self):
		yield from self.wait_until_high(self._USB_DP_RECORD.d_n.o, timeout = 1e4)
		yield from self.usb_assert_k()

	def usb_assert_k(self):
		self.assertEqual((yield self._USB_DP_RECORD.d_n.o), 1)
		self.assertEqual((yield self._USB_DP_RECORD.d_p.o), 0)


	def usb_initialize(self):
		yield from self.usb_single_zero()
		yield from self.wait_for(30e-6, 'usb')
		yield from self.usb_single_one()
		yield from self.wait_for(1e-6, 'usb')

	def usb_sync(self):
		yield from self.usb_emit_bits(0x100, 9)

	def usb_assert_sync(self):
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
		yield from self.usb_single_zero()
		yield from self.usb_single_zero()
		yield from self.usb_j()
		yield from self.usb_single_one()
		self._last_state = None

	def usb_sof(self, frame_number: int | None = None):
		yield from self.usb_sync()
		yield from self.usb_emit_bits(USBPacketID.SOF.byte())

		if frame_number is not None:
			self._last_frame = frame_number

		yield from self.usb_emit_bits(self._last_frame, 11)
		yield from self.usb_emit_bits(self.crc5(self._last_frame, 11), 5)
		yield from self.usb_eop()

		self._last_frame += 1

	def usb_in(self, addr: int, ep: int):
		yield from self.usb_solicit(addr, ep, USBPacketID.IN)

	def usb_out(self, addr: int, ep: int):
		yield from self.usb_solicit(addr, ep, USBPacketID.OUT)

	def usb_setup(self, addr: int):
		self._last_data = None
		yield from self.usb_solicit(addr, 0, USBPacketID.SETUP)

	def usb_send_ack(self):
		yield from self.usb_sync()
		yield from self.usb_emit_bits(USBPacketID.ACK.byte())
		yield from self.usb_eop()

	def usb_get_ack(self):
		yield from self.usb_consume_response((USBPacketID.ACK.byte(),))

	def usb_get_stall(self):
		yield from self.usb_consume_response((USBPacketID.STALL.byte(),))

	def usb_solicit(self, addr: int, ep: int, pid: USBPacketID):
		yield from self.usb_sync()
		yield from self.usb_emit_bits(pid.byte())
		yield from self.usb_emit_bits(addr, 7)
		yield from self.usb_emit_bits(ep, 4)
		yield from self.usb_emit_bits(self.crc5((addr | (ep << 7)), 11), 5)
		yield from self.usb_eop()

	def usb_data(self, data: Iterable[int]):
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
		yield from self.usb_consume_response((USBPacketID.DATA1.byte(), 0x00, 0x00))

	def usb_send_zlp(self):
		yield from self.usb_data(())

	def usb_send_setup_pkt(self, addr: int, data: Iterable[int]):
		yield from self.usb_setup(addr)
		yield from self.usb_data(data)
		yield from self.usb_get_ack()
		yield from self.step(10)


	def usb_set_addr(self, addr: int):
		yield from self.usb_send_setup_pkt(0, (
			0x00, USBStandardRequests.SET_ADDRESS,
			*addr.to_bytes(2, byteorder = 'little'), 0x00, 0x00, 0x00, 0x00
		))
		yield from self.usb_in(0x00, 0x00)
		yield from self.usb_get_zlp()
		yield from self.usb_send_ack()

	def usb_set_interface(self, addr: int, interface: int, alt: int):
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
		yield from self.usb_send_setup_pkt(addr, (
			0x00, USBStandardRequests.SET_CONFIGURATION,
			*cfg.to_bytes(2, byteorder = 'little'), 0x00, 0x00, 0x00, 0x00
		))
		yield from self.usb_in(addr, 0x00)
		yield from self.usb_get_zlp()
		yield from self.usb_send_ack()


	def usb_get_state(self):
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
		yield from self.usb_assert_sync()
		self._last_state = 'k'

		for byte in data:
			self.assertEqual((yield from self.usb_consume_byte()), byte)

		self.assertEqual((yield from self.usb_get_state()), '0')
		self.assertEqual((yield from self.usb_get_state()), '0')
		self.assertEqual((yield from self.usb_get_state()), 'j')

		self._last_state = None


class USBGatewareTestHelpers:
	'''
	Unlike :py:class:`USBGatewarePHYTestHelpers`, this class relies on access to a SOL interface exposed in the DUT
	or DUT wrapper.

	Most of the USB tests in Squishy use this type of helpers, as the :py:class:`USBGatewarePHYTestHelpers` is only
	used for full end-to-end USB integration validation if absolutely needed.
	'''

	def setup_helper(self):
		self.domains = (('usb', 60e6), *self.domains)

	def setup_received(self):
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
		yield from self.send_setup(
			type     = USBRequestType.STANDARD,
			retrieve = False,
			req      = USBStandardRequests.SET_INTERFACE,
			value    = alt_mode,
			index    = interface,
			length   = 0
		)

	def receive_data(self, *, data: tuple[int, ...] | bytes, check: bool = True):
		result = True
		yield self.dut.interface.tx.ready.eq(1)
		yield self.dut.interface.data_requested.eq(1)
		yield Settle()
		yield
		yield self.dut.interface.data_requested.eq(0)
		self.assertEqual((yield self.dut.interface.tx.valid), 0)
		self.assertEqual((yield self.dut.interface.tx.payload), 0)
		while (yield self.dut.interface.tx.first) == 0:
			yield Settle()
			yield
		for idx, val in enumerate(data):
			self.assertEqual((yield self.dut.interface.tx.first), (1 if idx == 0 else 0))
			self.assertEqual((yield self.dut.interface.tx.last), (1 if idx == len(data) - 1 else 0))
			self.assertEqual((yield self.dut.interface.tx.valid), 1)
			if check:
				self.assertEqual((yield self.dut.interface.tx.payload), val)
			if (yield self.dut.interface.tx.payload) != val:
				result = False
			self.assertEqual((yield self.dut.interface.handshakes_out.ack), 0)
			if idx == len(data) - 1:
				yield self.dut.interface.tx.ready.eq(0)
				yield self.dut.interface.status_requested.eq(1)
			yield Settle()
			yield
		self.assertEqual((yield self.dut.interface.tx.valid), 0)
		self.assertEqual((yield self.dut.interface.tx.payload), 0)
		self.assertEqual((yield self.dut.interface.handshakes_out.ack), 1)
		yield self.dut.interface.status_requested.eq(0)
		yield Settle()
		yield
		self.assertEqual((yield self.dut.interface.handshakes_out.ack), 0)
		return result

	def receive_zlp(self):
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
		yield self.dut.interface.rx.valid.eq(1)
		for val in data:
			yield Settle()
			yield
			yield self.dut.interface.rx.payload.eq(val)
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
		yield from self.send_setup(
			type = USBRequestType.VENDOR, retrieve = True,
			req = vendor_code, value = 0, index = index,
			length = length, recipient = USBRequestRecipient.DEVICE
		)

class DFUGatewareTestHelpers:
	'''
	This mixin provides some simple wrappers for sending DFU bits via the :py:class:`USBGatewareTestHelpers` mixin.
	'''

	def send_dfu_detach(self):
		yield from self.send_setup(
			type = USBRequestType.CLASS, retrieve = False, req = DFURequests.DETACH, value = 1000, index = 0, length = 0
		)

	def send_dfu_download(self, *, length: int = 256):
		yield from self.send_setup(
			type = USBRequestType.CLASS, retrieve = False, req = DFURequests.DOWNLOAD, value = 0, index = 0, length = length
		)

	def send_dfu_get_status(self):
		yield from self.send_setup(
			type = USBRequestType.CLASS, retrieve = True, req = DFURequests.GET_STATUS, value = 0, index = 0, length = 6
		)

	def send_dfu_get_state(self):
		yield from self.send_setup(
			type = USBRequestType.CLASS, retrieve = True, req = DFURequests.GET_STATE, value = 0, index = 0, length = 1
		)

class SPIGatewareTestHelpers:
	'''  '''

	def setup_helper(self):
		pass


class SCSIGatewareTestHelpers:
	''' '''

	def setup_helper(self):
		pass

class SquishyGatewareTest(ToriiTestCase):
	''' '''

	domains = ()

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
