# SPDX-License-Identifier: BSD-3-Clause

from enum                                import (
	IntEnum, unique
)

from torii                            import (
	Module, Signal, Cat, Instance
)
from torii.hdl.ast                    import (
	Operator
)

from usb_construct.types                 import (
	USBRequestType, USBRequestRecipient,
	USBStandardRequests
)
from usb_construct.types.descriptors.dfu import (
	DFURequests
)

from sol.gateware.usb.usb2.request      import (
	USBRequestHandler, SetupPacket
)
from sol.gateware.usb.stream            import (
	USBInStreamInterface
)
from sol.gateware.stream.generator      import (
	StreamSerializer
)


__doc__ = '''\
	DFU Stub
'''

__all__ = (
	'DFURequestHandler',
)


@unique
class DFUState(IntEnum):
	APP_IDLE = 0

@unique
class DFUStatus(IntEnum):
	OKAY = 0

class DFURequestHandler(USBRequestHandler):
	'''  '''

	def __init__(self, configuration_num: int, interface_num: int):
		super().__init__()
		self._configuration  = configuration_num
		self._interface_num  = interface_num
		self._trigger_reboot = Signal(name = 'trigger_reboot')
		self._slot_select    = Signal(2, name = 'slot_select')

	def elaborate(self, platform) -> Module:
		m = Module()

		interface          = self.interface
		setup: SetupPacket = interface.setup

		m.submodules.transmitter = transmitter = StreamSerializer(
			data_length = 6, domain = 'usb', stream_type = USBInStreamInterface, max_length_width = 3
		)

		trigger_reboot = self._trigger_reboot
		slot_select    = self._slot_select

		with m.FSM(domain = 'usb', name = 'dfu'):
			with m.State('IDLE'):
				with m.If(setup.received & self.handlerCondition(setup)):
					with m.If(setup.type == USBRequestType.CLASS):
						with m.Switch(setup.request):
							with m.Case(DFURequests.DETACH):
								m.next = 'HANDLE_DETACH'
							with m.Case(DFURequests.GET_STATUS):
								m.next = 'HANDLE_GET_STATUS'
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

			with m.State('HANDLE_DETACH'):
				with m.If(interface.status_requested):
					m.d.comb += [
						self.send_zlp(),
					]
				with m.If(interface.handshakes_in.ack):
					m.d.usb += [
						trigger_reboot.eq(1),
					]

			with m.State('HANDLE_GET_STATUS'):
				m.d.comb += [
					transmitter.stream.connect(interface.tx),
					transmitter.max_length.eq(6),
					transmitter.data[0].eq(DFUStatus.OKAY),
					Cat(transmitter.data[1:4]).eq(0),
					transmitter.data[4].eq(DFUState.APP_IDLE),
					transmitter.data[5].eq(0),
				]

				with m.If(interface.data_requested):
					with m.If(setup.length == 6):
						m.d.comb += [
							transmitter.start.eq(1)
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

			with m.State('HANDLE_GET_STATE'):
				m.d.comb += [
					transmitter.stream.connect(interface.tx),
					transmitter.max_length.eq(1),
					transmitter.data[0].eq(DFUState.APP_IDLE),
				]

				with m.If(interface.data_requested):
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
					transmitter.data[0].eq(0),
				]
				with m.If(self.interface.data_requested):
					with m.If(setup.length == 1):
						m.d.comb += [
							transmitter.start.eq(1),
						]
					with m.Else():
						m.d.comb += [
							interface.handshakes_out.stall.eq(1)
						]
						m.next = 'IDLE'

				with m.If(interface.status_requested):
					m.d.comb += [
						interface.handshakes_out.ack.eq(1),
					]
					m.next = 'IDLE'

			with m.State('SET_INTERFACE'):
				with m.If(interface.status_requested):
					m.d.comb += [
						self.send_zlp(),
					]
				with m.If(interface.handshakes_in.ack):
					m.next = 'IDLE'

			with m.State('UNHANDLED'):
				with m.If(interface.data_requested | interface.status_requested):
					m.d.comb += [
						interface.handshakes_out.stall.eq(1),
					]
					m.next = 'IDLE'

		m.submodules += Instance(
			'SB_WARMBOOT',
			i_BOOT  = trigger_reboot,
			i_S0    = slot_select[0],
			i_S1    = slot_select[1],
		)

		m.d.comb += [
			slot_select.eq(0b00),
		]

		return m

	def handlerCondition(self, setup: SetupPacket) -> Operator:
		return (
			(self.interface.active_config == self._configuration) &
			((setup.type      == USBRequestType.CLASS) | (setup.type == USBRequestType.STANDARD)) &
			(setup.recipient == USBRequestRecipient.INTERFACE) &
			(setup.index     == self._interface_num)
		)
