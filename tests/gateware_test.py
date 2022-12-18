# SPDX-License-Identifier: BSD-3-Clause

from typing              import Tuple, Union

from torii.sim           import Settle
from torii.test          import ToriiTestCase, sim_test
from usb_construct.types import USBRequestRecipient, USBRequestType, USBStandardRequests

__all__ = (
	'SquishyUSBGatewareTestCase',
	'SquishySCSIGatewareTestCase',
	'sim_test',
)

class SquishyUSBGatewareTestCase(ToriiTestCase):
	domains = (('usb', 60e6), )

	def setupReceived(self):
		yield self.dut.interface.setup.received.eq(1)
		yield Settle()
		yield
		yield self.dut.interface.setup.received.eq(0)
		yield Settle()
		yield
		yield

	def sendSetupSetInterface(self):
		yield from self.sendSetup(
			type = USBRequestType.STANDARD, retrieve = False,
			req = USBStandardRequests.SET_INTERFACE, value = (0, 1),
			index = (0, 0), length = 0
		)

	def sendSetup(self, *,
		type: USBRequestType, retrieve: bool, req,
		value: Union[Tuple[int, int], int], index: Union[Tuple[int, int], int],
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
		yield from self.setupReceived()

	def receiveData(self, *,
		data: Union[Tuple[int], bytes],
		check: bool = True
	):
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
			self.assertEqual(
				(yield self.dut.interface.tx.first),
				(1 if idx == 0 else 0)
			)
			self.assertEqual(
				(yield self.dut.interface.tx.last),
				(1 if idx == len(data) - 1 else 0)
			)
			self.assertEqual(
				(yield self.dut.interface.tx.valid),
				1
			)
			if check:
				self.assertEqual(
					(yield self.dut.interface.tx.payload),
					val
				)
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

	def receiveZLP(self):
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

	def sendData(self, *,
		data: Union[Tuple[int], bytes]
	):
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

class SquishySCSIGatewareTestCase(ToriiTestCase):
	domains = (('scsi', 100e6), )
