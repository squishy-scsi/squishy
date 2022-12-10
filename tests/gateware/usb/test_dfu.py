# SPDX-License-Identifier: BSD-3-Clause
from torii.sim                           import (
	Settle
)
from usb_construct.types                 import (
	USBRequestType
)
from usb_construct.types.descriptors.dfu import (
	DFURequests
)
from gateware_test                       import (
	SquishyUSBGatewareTestCase, sim_test
)
from squishy.gateware.usb.dfu            import (
	DFURequestHandler,
	DFUState
)


class DFURequestHandlerStubTests(SquishyUSBGatewareTestCase):
	dut: DFURequestHandler = DFURequestHandler
	dut_args = {
		'configuration_num': 1,
		'interface_num': 0
	}


	def sendDFUDetach(self):
		yield from self.sendSetup(
			type = USBRequestType.CLASS, retrieve = False,
			req = DFURequests.DETACH, value = 1000,
			index = 0, length = 0
		)

	def sendDFUGetStatus(self):
		yield from self.sendSetup(
			type = USBRequestType.CLASS, retrieve = True,
			req = DFURequests.GET_STATUS, value = 0,
			index = 0, length = 6
		)

	@sim_test(domain = 'usb')
	def test_dfu_stub(self):
		self.assertEqual((yield self.dut._slot_select), 0)
		yield self.dut.interface.active_config.eq(1)
		yield Settle()
		yield
		yield from self.sendSetupSetInterface()
		yield from self.receiveZLP()
		yield
		yield
		yield
		yield from self.sendDFUGetStatus()
		yield from self.receiveData(data = (0, 0, 0, 0, DFUState.APP_IDLE, 0))
		yield from self.sendDFUDetach()
		yield from self.receiveZLP()
		self.assertEqual((yield self.dut._trigger_reboot), 1)
		self.assertEqual((yield self.dut._slot_select), 0)
