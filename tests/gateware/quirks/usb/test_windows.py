# SPDX-License-Identifier: BSD-3-Clause
from typing                                      import (
	Union, Tuple
)
from amaranth.sim                                import (
	Settle
)
from usb_protocol.types                          import (
	USBRequestType, USBRequestRecipient
)
from usb_protocol.types.descriptors.microsoft    import (
	MicrosoftRequests
)
from usb_protocol.emitters.descriptors.microsoft import (
	SetHeaderDescriptorEmitter, PlatformDescriptorCollection
)
from squishy.gateware.quirks.usb.windows         import (
	WindowsRequestHandler, GetDescriptorSetHandler
)
from gateware_test                               import (
	SquishyGatewareTestCase, sim_test
)


def _make_platform_descriptors():
	desc_collection = PlatformDescriptorCollection()

	set_header = SetHeaderDescriptorEmitter()
	with set_header.SubsetHeaderConfiguration() as sub_cfg: # 👉👈🥺
		sub_cfg.bConfigurationValue = 1

		with sub_cfg.SubsetHeaderFunction() as sub_func:
			sub_func.bFirstInterface = 0

			with sub_func.FeatureCompatibleID() as feat_id:
				feat_id.CompatibleID    = 'WINUSB'
				feat_id.SubCompatibleID = ''

	desc_collection.add_descriptor(set_header, 1)

	return (desc_collection, desc_collection.descriptors)


class GetDescriptorSetHandlerTests(SquishyGatewareTestCase):
	_desc_collection, _descriptors = _make_platform_descriptors()
	dut: GetDescriptorSetHandler = GetDescriptorSetHandler
	dut_args = {
		'desc_collection': _desc_collection
	}
	domains = (('usb', 60e8),)


	@sim_test()
	def test_get_desc_set(self):
		# Set known state
		yield self.dut.tx.ready.eq(1)
		yield Settle()
		yield
		# Setup request
		yield self.dut.request.eq(1)
		yield self.dut.length.eq(46)
		yield self.dut.start_pos.eq(0)
		yield self.dut.tx.ready.eq(1)
		yield self.dut.start.eq(1)
		yield Settle()
		yield
		yield self.dut.start.eq(0)
		while (yield self.dut.tx.valid) == 0:
			yield
			yield Settle()

		desc      = self._descriptors[1]
		bytes     = len(desc)
		last_byte = bytes - 1

		for byte in range(bytes):
			self.assertEqual((yield self.dut.tx.first), (1 if byte == 0 else 0))
			self.assertEqual((yield self.dut.tx.last), (1 if byte == last_byte else 0))
			self.assertEqual((yield self.dut.tx.valid), 1)
			self.assertEqual((yield self.dut.tx.payload), desc[byte])
			self.assertEqual((yield self.dut.stall), 0)
			yield
			yield Settle()
		self.assertEqual((yield self.dut.tx.valid), 0)
		yield

		# Test the first stallable condition
		yield self.dut.tx.ready.eq(0)
		yield Settle()
		yield
		yield self.dut.request.eq(0)
		yield self.dut.length.eq(0)
		yield self.dut.start_pos.eq(0)
		yield self.dut.tx.ready.eq(1)
		yield self.dut.start.eq(1)
		yield Settle()
		yield
		yield self.dut.start.eq(0)
		yield Settle()

		attempts = 0
		while not (yield self.dut.stall):
			self.assertEqual((yield self.dut.tx.valid), 0)
			attempts += 1
			if attempts > 10:
				self.fail('Stall took too long')
			yield
			yield Settle()
		yield

		# ... And the second
		yield self.dut.tx.ready.eq(0)
		yield Settle()
		yield
		yield self.dut.request.eq(2)
		yield self.dut.length.eq(1)
		yield self.dut.start_pos.eq(0)
		yield self.dut.tx.ready.eq(1)
		yield self.dut.start.eq(1)
		yield Settle()
		yield
		yield self.dut.start.eq(0)
		yield Settle()

		attempts = 0
		while not (yield self.dut.stall):
			self.assertEqual((yield self.dut.tx.valid), 0)
			attempts += 1
			if attempts > 10:
				self.fail('Stall took too long')
			yield
			yield Settle()
		yield

		# Cleanup
		yield self.dut.tx.ready.eq(0)
		yield Settle()
		yield
		yield Settle()
		yield


class WindowsRequestHandlerTests(SquishyGatewareTestCase):
	_desc_collection, _descriptors = _make_platform_descriptors()
	dut: WindowsRequestHandler = WindowsRequestHandler
	dut_args = {
		'descriptors': _desc_collection
	}
	domains = (('usb', 60e8),)

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

	def recv_data(self, *, data: Union[Tuple[int], bytes]):
		yield self.dut.interface.tx.ready.eq(1)
		yield self.dut.interface.data_requested.eq(1)
		yield Settle()
		yield
		yield self.dut.interface.data_requested.eq(0)
		self.assertEqual((yield self.dut.interface.tx.valid),   0)
		self.assertEqual((yield self.dut.interface.tx.payload), 0)
		while (yield self.dut.interface.tx.first) == 0:
			yield Settle()
			yield

		for idx, val in enumerate(data):
			self.assertEqual((yield self.dut.interface.tx.first), (1 if idx == 0 else 0))
			self.assertEqual((yield self.dut.interface.tx.last),  (1 if idx == len(data) - 1 else 0))
			self.assertEqual((yield self.dut.interface.tx.valid), 1)
			self.assertEqual((yield self.dut.interface.tx.payload), val)
			self.assertEqual((yield self.dut.interface.handshakes_out.ack), 0)

			if idx == len(data) - 1:
				yield self.dut.interface.tx.ready.eq(0)
				yield self.dut.interface.status_requested.eq(1)

			yield Settle()
			yield

		self.assertEqual((yield self.dut.interface.tx.valid),   0)
		self.assertEqual((yield self.dut.interface.tx.payload), 0)
		self.assertEqual((yield self.dut.interface.handshakes_out.ack), 1)
		yield self.dut.interface.status_requested.eq(0)
		yield Settle()
		yield
		self.assertEqual((yield self.dut.interface.handshakes_out.ack), 0)

	def send_get_desc(self, *, vendor_code, length):
		yield from self.send_setup(
			type = USBRequestType.VENDOR, retrieve = True,
			req = vendor_code, val = 0, idx = MicrosoftRequests.GET_DESCRIPTOR_SET,
			length = length
		)

	def send_setup(self, *, type: USBRequestType, retrieve: bool, req, val, idx, length):
		yield self.dut.interface.setup.recipient.eq(USBRequestRecipient.DEVICE)
		yield self.dut.interface.setup.type.eq(type)
		yield self.dut.interface.setup.is_in_request.eq(1 if retrieve else 0)
		yield self.dut.interface.setup.request.eq(req)

		if isinstance(val, int):
			yield self.dut.interface.setup.value.eq(val)
		else:
			yield self.dut.interface.setup.value[0:8].eq(val[0])
			yield self.dut.interface.setup.value[8:16].eq(val[1])

		if isinstance(idx, int):
			yield self.dut.interface.setup.index.eq(idx)
		else:
			yield self.dut.interface.setup.index[0:8].eq(idx[0])
			yield self.dut.interface.setup.index[8:16].eq(idx[1])

		yield self.dut.interface.setup.length.eq(length)
		yield from self.setup_received()

	def setup_received(self):
		yield self.dut.interface.setup.received.eq(1)
		yield Settle()
		yield
		yield self.dut.interface.setup.received.eq(0)
		yield Settle()
		yield
		yield


	@sim_test()
	def test_windows_request(self):
		yield
		yield from self.send_get_desc(vendor_code = 1, length = 46)
		yield from self.recv_data(data = self._descriptors[1])
		yield from self.send_get_desc(vendor_code = 0, length = 46)
		yield from self.ensure_stall()
		yield from self.send_get_desc(vendor_code = 2, length = 46)
		yield from self.ensure_stall()
		yield from self.send_setup(
			type = USBRequestType.VENDOR, retrieve = False, req = 1,
			val = 0, idx = MicrosoftRequests.GET_DESCRIPTOR_SET, length = 0
		)
		yield from self.ensure_stall()
		yield from self.send_setup(
			type = USBRequestType.VENDOR, retrieve = True, req = 1,
			val = 1, idx = MicrosoftRequests.GET_DESCRIPTOR_SET, length = 0
		)
		yield from self.ensure_stall()
