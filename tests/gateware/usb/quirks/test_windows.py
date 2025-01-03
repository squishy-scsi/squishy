# SPDX-License-Identifier: BSD-3-Clause

from torii.sim                                    import Settle
from torii.test                                   import ToriiTestCase

from usb_construct.emitters.descriptors.microsoft import PlatformDescriptorCollection, SetHeaderDescriptorEmitter
from usb_construct.types                          import USBRequestRecipient, USBRequestType
from usb_construct.types.descriptors.microsoft    import MicrosoftRequests

from squishy.support.test                         import SquishyGatewareTest, USBGatewareTestHelpers
from squishy.gateware.usb.quirks.windows          import GetDescriptorSetHandler, WindowsRequestHandler

def _make_platform_descriptors():
	desc_collection = PlatformDescriptorCollection()

	set_header = SetHeaderDescriptorEmitter()
	with set_header.SubsetHeaderConfiguration() as sub_cfg:
		sub_cfg.bConfigurationValue = 1

		with sub_cfg.SubsetHeaderFunction() as sub_func:
			sub_func.bFirstInterface = 0

			with sub_func.FeatureCompatibleID() as feat_id:
				feat_id.CompatibleID    = 'WINUSB'
				feat_id.SubCompatibleID = ''

	desc_collection.add_descriptor(set_header, 1)

	return (desc_collection, desc_collection.descriptors)


class GetDescriptorSetHandlerTests(SquishyGatewareTest, USBGatewareTestHelpers):
	_desc_collection, _descriptors = _make_platform_descriptors()
	dut: GetDescriptorSetHandler = GetDescriptorSetHandler
	dut_args = {
		'desc_collection': _desc_collection
	}

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		USBGatewareTestHelpers.setup_helper(self)


	@ToriiTestCase.simulation
	@ToriiTestCase.sync_domain(domain = 'usb')
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

class WindowsRequestHandlerTests(SquishyGatewareTest, USBGatewareTestHelpers):
	_desc_collection, _descriptors = _make_platform_descriptors()
	dut: WindowsRequestHandler = WindowsRequestHandler
	dut_args = {
		'descriptors': _desc_collection
	}

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		USBGatewareTestHelpers.setup_helper(self)

	@ToriiTestCase.simulation
	@ToriiTestCase.sync_domain(domain = 'usb')
	def test_windows_request(self):
		yield
		yield from self.send_get_desc(vendor_code = 1, length = 46, index = MicrosoftRequests.GET_DESCRIPTOR_SET)
		yield from self.receive_data(data = self._descriptors[1])
		yield from self.send_get_desc(vendor_code = 0, length = 46, index = MicrosoftRequests.GET_DESCRIPTOR_SET)
		yield from self.ensure_stall()
		yield from self.send_get_desc(vendor_code = 2, length = 46, index = MicrosoftRequests.GET_DESCRIPTOR_SET)
		yield from self.ensure_stall()
		yield from self.send_setup(
			type = USBRequestType.VENDOR, retrieve = False, req = 1,
			value = 0, index = MicrosoftRequests.GET_DESCRIPTOR_SET,
			length = 0, recipient = USBRequestRecipient.DEVICE
		)
		yield from self.ensure_stall()
		yield from self.send_setup(
			type = USBRequestType.VENDOR, retrieve = True, req = 1,
			value = 1, index = MicrosoftRequests.GET_DESCRIPTOR_SET,
			length = 0, recipient = USBRequestRecipient.DEVICE
		)
		yield from self.ensure_stall()
