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
	'USBGatewareTestHelpers',
	'DFUGatewareTestHelpers',
	'SPIGatewareTestHelpers',
	'SCSIGatewareTestHelpers',
)



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
