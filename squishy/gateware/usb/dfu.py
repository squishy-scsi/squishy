# SPDX-License-Identifier: BSD-3-Clause

'''

'''

from torii.hdl                           import Cat, Module, Signal
from torii.hdl.ast                       import Operator
from torii.lib.fifo                      import AsyncFIFO
from torii_usb.stream.generator          import StreamSerializer
from torii_usb.usb.stream                import USBInStreamInterface, USBOutStreamInterface
from torii_usb.usb.usb2.request          import SetupPacket, USBRequestHandler
from usb_construct.types                 import USBRequestRecipient, USBRequestType, USBStandardRequests
from usb_construct.types.descriptors.dfu import DFURequests

from ...core.dfu                         import DFUState, DFUStatus
from ..platform                          import SquishyPlatformType

__all__ = (
	'DFURequestHandler',
)

class DFUConfig:
	'''

	Attributes
	----------

	status : Signal(4)
		DFU Status

	state : Signal(4)
		DFU State

	'''

	def __init__(self) -> None:
		self.status = Signal(DFUStatus)
		self.state  = Signal(DFUState)

class DFURequestHandler(USBRequestHandler):
	'''
	USB DFU Request handler.

	This implements both a fully DFU capable endpoint for firmware flashing as well
	as a simple DFU stub that is used to reboot the device into bootloader mode.

	Parameters
	----------
	configuration : int
		The configuration ID for this DFU endpoint

	interface : int
		The interface ID for this DFU endpoint

	boot_stub : bool
		If True, only the bare minimum for triggering a DFU reboot will be
		generated, otherwise if False a full DFU implementation will be
		generated.

	fifo : AsyncFIFO | None
		The storage FIFO.

	Attributes
	----------
	trigger_reboot : Signal
		Output: driven high when the DFU handler wants to reboot the device

	slot_selection : Signal(2)
		Output: the flash slot address

	dl_start : Signal
		Output: Start of a DFU transfer.

	dl_finish : Signal
		Output: An acknowledgement of the `dl_done` signal

	dl_ready : Signal
		Input: If the backing storage is ready for data.

	dl_done : Signal
		Input: When the backing storage is done storing the data.

	dl_completed : Signal
		Output: Raised when the DFU state machine has completed a download to a slot.

	dl_size : Signal(16)
		Output: The size of the DFU transfer into the the FIFO

	slot_changed : Signal
		Output: Raised when the DFU alt-mode is changed.

	slot_ack : Signal
		Input: When the `slot_changed` signal was acted on.

	Note
	----
	All of the signals for this module are expected to be on the 'USB' clock domain,
	meaning you need an FFSynchronizer for any other domain.

	Raises
	------
	ValueError
		If fifo is `None` when `boot_stub` is False.

	'''

	def __init__(self, configuration: int, interface: int, boot_stub: bool, *, fifo: AsyncFIFO | None = None) -> None:
		super().__init__()

		# DFU interface
		self._interface_id = interface
		self._config_id    = configuration

		# Used to alter gateware synth if we're just a DFU reboot stub or a full impl
		self._is_stub  = boot_stub

		if not self._is_stub:
			if fifo is None:
				raise ValueError('fifo parameter must not be None for non-stub DFU implementations')

			self._bit_fifo  = fifo

			self.dl_start      = Signal()
			self.dl_finish     = Signal()
			self.dl_ready      = Signal()
			self.dl_done       = Signal()
			self.dl_completed  = Signal()
			self.dl_size       = Signal(16)

			self.slot_changed = Signal()
			self.slot_ack     = Signal()

		self.trigger_reboot = Signal()
		self.slot_selection = Signal(2)

	def elaborate(self, platform: SquishyPlatformType) -> Module:
		m = Module()

		# DFU Stub

		interface = self.interface
		setup_pkt = interface.setup

		if not self._is_stub:
			rx_trig   = Signal()
			rx_stream = USBOutStreamInterface(data_width = 8)

			recv_start    = Signal()
			recv_count    = Signal.like(setup_pkt.length)
			recv_consumed = Signal.like(setup_pkt.length)

			dfu_cfg = DFUConfig()

			m.d.comb += [
				self.dl_start.eq(0),
				self.dl_finish.eq(0),
				self.slot_changed.eq(0),
			]

		m.submodules.transmitter = transmitter = StreamSerializer(
			data_length = 6, domain = 'usb', stream_type = USBInStreamInterface, max_length_width = 3
		)

		with m.FSM(domain = 'usb', name = 'dfu'):
			if not self._is_stub:
				with m.State('RESET'):
					m.d.usb += [
						dfu_cfg.status.eq(DFUStatus.Okay),
						dfu_cfg.state.eq(DFUState.DFUIdle),
						self.slot_selection.eq(0),
					]

					with m.If(self.dl_ready):
						m.next = 'IDLE'

			with m.State('IDLE'):
				with m.If(setup_pkt.received & self.handler_condition(setup_pkt)):
					with m.If(setup_pkt.type == USBRequestType.CLASS):
						with m.Switch(setup_pkt.request):
							with m.Case(DFURequests.DETACH):
								m.next = 'HANDLE_DETACH'
							with m.Case(DFURequests.GET_STATUS):
								m.next = 'HANDLE_GET_STATUS'
							with m.Case(DFURequests.GET_STATE):
								m.next = 'HANDLE_GET_STATE'
							if not self._is_stub:
								with m.Case(DFURequests.DOWNLOAD):
									m.next = 'HANDLE_DOWNLOAD'
								with m.Case(DFURequests.CLR_STATUS):
									m.next = 'HANDLE_CLR_STATUS'
							with m.Default():
								m.next = 'UNHANDLED'
					with m.Elif(setup_pkt.type == USBRequestType.STANDARD):
						with m.Switch(setup_pkt.request):
							with m.Case(USBStandardRequests.GET_INTERFACE):
								m.next = 'GET_INTERFACE'
							with m.Case(USBStandardRequests.SET_INTERFACE):
								m.next = 'SET_INTERFACE'
							with m.Default():
								m.next = 'UNHANDLED'
				if not self._is_stub:
					with m.If(self.dl_done):
						m.d.comb += [ self.dl_finish.eq(1), ]
						m.d.usb  += [ dfu_cfg.state.eq(DFUState.DlSync), ]

			with m.State('HANDLE_DETACH'):
				with m.If(interface.status_requested):
					m.d.comb += [ self.send_zlp(), ]
				with m.If(interface.handshakes_in.ack):
					m.d.usb += [ self.trigger_reboot.eq(1), ]

			with m.State('HANDLE_GET_STATUS'):
				m.d.comb += [
					transmitter.stream.attach(interface.tx),
					transmitter.max_length.eq(6),
					transmitter.data[0].eq(DFUStatus.Okay if self._is_stub else dfu_cfg.status),
					Cat(transmitter.data[1:4]).eq(0),
					transmitter.data[4].eq(DFUState.AppIdle if self._is_stub else Cat(dfu_cfg.state, 0)),
					transmitter.data[5].eq(0),
				]

				with m.If(interface.data_requested):
					with m.If(setup_pkt.length == 6):
						m.d.comb += [ transmitter.start.eq(1), ]
					with m.Else():
						m.d.comb += [ interface.handshakes_out.stall.eq(1), ]
						m.next = 'IDLE'

				with m.If(interface.status_requested):
					m.d.comb += [ interface.handshakes_out.ack.eq(1), ]

					if not self._is_stub:
						with m.If(dfu_cfg.state == DFUState.DlSync):
							m.d.usb += [ dfu_cfg.state.eq(DFUState.DlIdle), ]

					m.next = 'IDLE'

			with m.State('HANDLE_GET_STATE'):
				m.d.comb += [
					transmitter.stream.attach(interface.tx),
					transmitter.max_length.eq(1),
				]

				if self._is_stub:
					m.d.comb += [ transmitter.data[0].eq(DFUState.AppIdle), ]
				else:
					m.d.comb += [ transmitter.data[0].eq(Cat(dfu_cfg.state, 0)), ]

				with m.If(interface.data_requested):
					with m.If(setup_pkt.length == 1):
						m.d.comb += [ transmitter.start.eq(1), ]
					with m.Else():
						m.d.comb += [ interface.handshakes_out.stall.eq(1), ]
						m.next = 'IDLE'

				with m.If(interface.status_requested):
					m.d.comb += [ interface.handshakes_out.ack.eq(1), ]
					m.next = 'IDLE'

			if not self._is_stub:
				with m.State('HANDLE_DOWNLOAD'):
					with m.If(setup_pkt.is_in_request | (setup_pkt.length > platform.flash.geometry.erase_size)):
						m.next = 'UNHANDLED'
					with m.Elif(setup_pkt.length):
						m.d.comb += [
							self.dl_start.eq(1),
							self.dl_size.eq(setup_pkt.length),
						]
						m.d.usb += [ dfu_cfg.state.eq(DFUState.DlBusy) ]

						m.next = 'HANDLE_DOWNLOAD_DATA'
					with m.Else():
						m.d.comb += [ self.dl_completed.eq(1), ]
						m.next = 'HANDLE_DOWNLOAD_COMPLETE'

				with m.State('HANDLE_DOWNLOAD_DATA'):
					m.d.comb += [ interface.rx.connect(rx_stream), ]

					with m.If(~rx_trig):
						m.d.comb += [ recv_start.eq(1), ]
						m.d.usb  += [ rx_trig.eq(1), ]

					with m.If(interface.rx_ready_for_response):
						m.d.comb += [ interface.handshakes_out.ack.eq(1), ]

					with m.If(interface.status_requested):
						m.d.comb += [ self.send_zlp(), ]

					with m.If(interface.handshakes_in.ack):
						m.d.usb += [ rx_trig.eq(0), ]
						m.next = 'IDLE'

				with m.State('HANDLE_DOWNLOAD_COMPLETE'):
					with m.If(interface.status_requested):
						m.d.usb  += [ dfu_cfg.state.eq(DFUState.DFUIdle), ]
						m.d.comb += [ self.send_zlp(), ]

					with m.If(interface.handshakes_in.ack):
						m.next = 'IDLE'

				with m.State('HANDLE_CLR_STATUS'):
					with m.If(setup_pkt.length == 0):
						with m.If(dfu_cfg.state == DFUState.Error):
							m.d.usb += [
								dfu_cfg.status.eq(DFUStatus.Okay),
								dfu_cfg.state.eq(DFUState.AppIdle),
							]
					with m.Else():
						m.d.comb += [ interface.handshakes_out.stall.eq(1), ]
						m.next = 'IDLE'

					with m.If(interface.status_requested):
						m.d.comb += [ self.send_zlp(), ]
					with m.If(interface.handshakes_in.ack):
						m.next = 'IDLE'

				with m.State('SLOT_WAIT'):
					with m.If(self.slot_ack):
						m.next = 'IDLE'

			with m.State('GET_INTERFACE'):
				m.d.comb += [
					transmitter.stream.attach(interface.tx),
					transmitter.max_length.eq(1),
					# TODO(aki): This inline if might blow up
					transmitter.data[0].eq(0 if self._is_stub else self.slot_selection),
				]

				with m.If(self.interface.data_requested):
					with m.If(setup_pkt.length == 1):
						m.d.comb += [ transmitter.start.eq(1), ]
					with m.Else():
						m.d.comb += [ interface.handshakes_out.stall.eq(1), ]
						m.next = 'IDLE'

				with m.If(interface.status_requested):
					m.d.comb += [ interface.handshakes_out.ack.eq(1), ]
					m.next = 'IDLE'

			with m.State('SET_INTERFACE'):
				with m.If(interface.status_requested):
					m.d.comb += [ self.send_zlp(), ]
				with m.If(interface.handshakes_in.ack):
					if self._is_stub:
						m.next = 'IDLE'
					else:
						m.d.usb += [ self.slot_selection.eq(setup_pkt.value[0:8]), ]
						m.d.comb += [ self.slot_changed.eq(1), ]
						m.next = 'SLOT_WAIT'

			with m.State('UNHANDLED'):
				with m.If(interface.data_requested | interface.status_requested):
					m.d.comb += [ interface.handshakes_out.stall.eq(1), ]
					m.next = 'IDLE'

		if not self._is_stub:
			m.d.comb += [
				self._bit_fifo.w_en.eq(0),
				self._bit_fifo.w_data.eq(rx_stream.data),
			]

			recv_cont = (recv_consumed < recv_count)

			with m.FSM(domain = 'usb', name = 'download'):
				with m.State('IDLE'):
					m.d.usb += [ recv_consumed.eq(0), ]

					with m.If(recv_start):
						m.d.usb += [ recv_count.eq(setup_pkt.length - 1), ]
						m.next = 'STREAMING'

				with m.State('STREAMING'):
					with m.If(rx_stream.valid & rx_stream.next):
						m.d.comb += [ self._bit_fifo.w_en.eq(1), ]

						with m.If(recv_cont):
							m.d.usb += [ recv_consumed.eq(recv_consumed + 1), ]
						with m.Else():
							m.next = 'IDLE'

		return m

	def handler_condition(self, setup: SetupPacket) -> Operator:
		return (
			(self.interface.active_config == self._config_id) &
			((setup.type     == USBRequestType.CLASS) | (setup.type == USBRequestType.STANDARD)) &
			(setup.recipient == USBRequestRecipient.INTERFACE) &
			(setup.index     == self._interface_id)
		)
