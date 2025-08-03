# SPDX-License-Identifier: BSD-3-Clause

'''

'''

from struct                                       import pack, unpack

from torii.hdl                                    import DomainRenamer, Elaboratable, Memory, Module, Signal
from torii.hdl.ast                                import Operator
from torii_usb.usb.stream                         import USBInStreamInterface
from torii_usb.usb.usb2.request                   import SetupPacket, USBRequestHandler
from usb_construct.emitters.descriptors.microsoft import PlatformDescriptorCollection
from usb_construct.types                          import USBRequestRecipient, USBRequestType
from usb_construct.types.descriptors.microsoft    import MicrosoftRequests

__all__ = (
	'WindowsRequestHandler',
)

class GetDescriptorSetHandler(Elaboratable):
	'''
	Windows ``GET_DESCRIPTOR_SET`` handler.

	Attributes
	----------

	request : Signal(8)
		The request field associated with the ``GET_DESCRIPTOR_SET`` request.
		It contains the descriptor set's vendor code.

	length : Signal(16)
		The length field associated with the ``GET_DESCRIPTOR_SET`` request.
		Determines the maximum allowed size in a response.

	start : Signal()
		Descriptor transmit strobe.

	start_pos : Signal(11)
		Starting position of the descriptor data to transmit.

	tx : USBInStreamInterface()
		The :py:class:`USBInStreamInterface` that streams out the descriptor data.

	stall : Signal()
		Strobed if a STALL should be generated rather than a normal response.

	'''
	element_size = 4

	def __init__(
		self, desc_collection: PlatformDescriptorCollection, max_packet_len: int = 64, domain: str = 'usb'
	) -> None:
		'''
		Parameters
		----------
		desc_collection : PlatformDescriptorCollection
			The :py:class:`PlatformDescriptorCollection` containing the descriptors to use for the Windows responses.

		max_packet_len : int
			The maximum size for the ``EP0`` packets.

		domain : str
			The clock domain this generator should belong to. (defaults to 'usb')

		'''

		self._descriptors    = desc_collection
		self._max_packet_len = max_packet_len
		self._domain         = domain

		self.request   = Signal(8)
		self.length    = Signal(16)
		self.start     = Signal()
		self.start_pos = Signal(11)
		self.tx        = USBInStreamInterface()
		self.stall     = Signal()

	@classmethod
	def _align_to_element_size(cls: type['GetDescriptorSetHandler'], n: int) -> int:
		''' Returns a given number rounded up to the next aligned element size. '''
		return (n + (cls.element_size - 1)) // cls.element_size

	def generate_rom(self) -> tuple[Memory, int, int]:
		'''
		Generate ROM for descriptor sets.

		Notes
		-----
		All data is aligned to 4-byte boundaries.

		This ROM is laid out as follows:

		* Index offsets and descriptor set lengths
			Each index of a descriptor set has an entry consistent of the length
			of the descriptor set (2 bytes) and the address of the first data
			byte (2 bytes).
			+---------+--------------------------------------+
			| Address |                 Data                 |
			+=========+======================================+
			|    0000 | Length of the first descriptor set   |
			+---------+--------------------------------------+
			|    0002 | Address of the first descriptor set  |
			+---------+--------------------------------------+
			|     ... |                                      |
			+---------+--------------------------------------+
		* Data
			Descriptor data for each descriptor set. Padded by 0 to the next 4-byte address.
			+---------+--------------------------------------+
			| Address |                 Data                 |
			+=========+======================================+
			|     ... | Descriptor data                      |
			+---------+--------------------------------------+
		Returns
		-------
		:py:class:`Tuple <tuple>` [ :py:class:`torii.hdl.mem.Memory`, :py:class:`int`, :py:class:`int` ]
			A List containing:
				* A Memory object defining the descriptor data and access information as defined above.
				  The memory object uses 32-bit entries which the descriptor gateware accesses accordingly.
				* The length of the largest held descriptor.
				* The highest Vendor code number used by the descriptors for retrieval.

		''' # noqa: E101

		descriptors = self._descriptors.descriptors

		assert max(descriptors.keys()) == len(descriptors), 'Descriptor sets have a non-contiguous vendor codes'
		assert min(descriptors.keys()) == 1, 'Descriptor sets must start at vendor code 1'

		max_vendor_code        = max(descriptors.keys())
		max_descriptor_size    = 0
		rom_size_table_entries = len(descriptors) * self.element_size
		rom_size_descriptors   = 0

		for desc_set in descriptors.values():
			aligned_size = self._align_to_element_size(len(desc_set))
			rom_size_descriptors += aligned_size * self.element_size
			max_descriptor_size = max(max_descriptor_size, len(desc_set))

		total_size = rom_size_table_entries + rom_size_descriptors
		rom = bytearray(total_size)

		next_free_addr = max_vendor_code * self.element_size

		for vendor_code, desc_set in sorted(descriptors.items()):
			desc_set_len  = len(desc_set)
			pointer_bytes = pack('>HH', desc_set_len, next_free_addr)
			pointer_addr  = (vendor_code - 1) * self.element_size

			rom[pointer_addr:pointer_addr + self.element_size] = pointer_bytes
			rom[next_free_addr:next_free_addr + desc_set_len]  = desc_set

			aligned_size = self._align_to_element_size(desc_set_len)
			next_free_addr += aligned_size * self.element_size

		assert total_size == len(rom)

		element_size = self.element_size
		rom_entries  = (rom[i:i + element_size] for i in range(0, total_size, element_size))
		initializer  = [unpack('>I', rom_entry)[0] for rom_entry in rom_entries]
		return Memory(width = 32, depth = len(initializer), init = initializer), max_descriptor_size, max_vendor_code

	def elaborate(self, platform) -> Memory:
		m = Module()

		rom, max_descriptor_size, max_vendor_code = self.generate_rom()
		m.submodules.read_port = read_port = rom.read_port(transparent = False)

		rom_lower      = read_port.data.word_select(0, 16)
		rom_upper      = read_port.data.word_select(1, 16)
		rom_pointer    = rom_lower.bit_select(2, read_port.addr.width)
		rom_elem_count = rom_upper

		vendor_code = Signal.like(self.request)
		length      = Signal(16)

		words_remaining = self.length - self.start_pos
		with m.If(words_remaining <= self._max_packet_len):
			m.d.sync += [
				length.eq(words_remaining),
			]
		with m.Else():
			m.d.sync += [
				length.eq(self._max_packet_len)
			]

		m.d.sync += [
			vendor_code.eq(self.request - 1)
		]

		pos_in_stream = Signal(range(max_descriptor_size))
		bytes_sent    = Signal.like(length)

		desc_len            = Signal.like(length)
		desc_data_base_addr = Signal(read_port.addr.width)

		on_first_packet = pos_in_stream == self.start_pos
		on_last_packet  = (
			(pos_in_stream == desc_len - 1) |
			(bytes_sent + 1 >= length)
		)

		with m.FSM():
			with m.State('IDLE'):
				m.d.sync += [
					bytes_sent.eq(0),
				]
				m.d.comb += [
					read_port.addr.eq(0),
				]
				with m.If(self.start):
					m.next = 'START'

			with m.State('START'):
				m.d.comb += [
					read_port.addr.eq(vendor_code),
				]
				m.d.sync += [
					pos_in_stream.eq(self.start_pos),
				]
				is_valid = vendor_code < max_vendor_code

				with m.If(is_valid):
					m.next = 'LOOKUP_DESCRIPTOR'
				with m.Else():
					m.d.comb += [
						self.stall.eq(1),
					]
					m.next = 'IDLE'

			with m.State('LOOKUP_DESCRIPTOR'):
				m.d.comb += [
					read_port.addr.eq(
						(rom_lower + pos_in_stream).bit_select(
							2, read_port.addr.width
						)
					),
				]
				m.d.sync += [
					desc_data_base_addr.eq(rom_pointer),
					desc_len.eq(rom_elem_count),
				]
				m.next = 'SEND_DESCRIPTOR'

			with m.State('SEND_DESCRIPTOR'):
				word_in_stream = pos_in_stream.shift_right(2)
				byte_in_stream = pos_in_stream.bit_select(0, 2)

				m.d.comb += [
					self.tx.valid.eq(1),
					read_port.addr.eq(desc_data_base_addr + word_in_stream),
					self.tx.data.eq(read_port.data.word_select((3 - byte_in_stream).as_unsigned(), 8)),
					self.tx.first.eq(on_first_packet),
					self.tx.last.eq(on_last_packet),
				]

				with m.If(self.tx.ready):
					with m.If(~on_last_packet):
						m.d.sync += [
							pos_in_stream.eq(pos_in_stream + 1),
							bytes_sent.eq(bytes_sent + 1),
						]
						m.d.comb += [
							read_port.addr.eq(
								desc_data_base_addr + (pos_in_stream + 1).bit_select(2, pos_in_stream.width - 2)
							),
						]
					with m.Else():
						m.d.sync += [
							desc_len.eq(0),
							desc_data_base_addr.eq(0),
						]
						m.next = 'IDLE'
		if self._domain != 'sync':
			m = DomainRenamer(sync = self._domain)(m)
		return m

class WindowsRequestHandler(USBRequestHandler):
	'''
	The Windows-specific handler for Windows requests.

	Notes
	-----
	The handler operates by reacting to incoming setup packets targeted directly to the device with the
	request type set to vendor-specific. It handles this and responds in accordance with the
	`Microsoft OS 2.0 Descriptors Specification <https://docs.microsoft.com/en-us/windows-hardware/drivers/usbcon/microsoft-os-2-0-descriptors-specification>`_.

	The main thing this handler has to deal with are the vendor requests to the device as the
	:py:class:`usb_construct.emitters.descriptors.microsoft.PlatformDescriptorCollection` and
	descriptor system deals with the the rest of the spec.

	To this end, when triggered, the handler works as follows:

	* The state machine does switches from ``IDLE`` into the ``CHECK_GET_DESCRIPTOR_SET`` state,
	* In the following cycle, we validate the request parameters and if they check out
	  we enter the ``GET_DESCRIPTOR_SET`` state,
	* In the ``GET_DESCRIPTOR_SET`` state, when the data phase begins, we set our instance of the
	  :py:class:`GetDescriptorSetHandler` running,
	* While the requested descriptor has not yet been delivered in full, we track data phase acks and:

		* When each complete packet is acked, update state in the
		  :py:class:`GetDescriptorSetHandler` to keep the data flowing.
		* Keep the transmit ``DATA0``/``DATA1`` packet ID value correct.

	* Once the data phase concludes and the status phase begins, we then respond to the host with an all-clear ACK
	* If either the :py:class:`GetDescriptorSetHandler` or the status phase
	  concludes, we return to ``IDLE``.

	''' # noqa: E101, E501

	def __init__(self, descriptors: PlatformDescriptorCollection, max_packet_size: int = 64):
		self.descriptors      = descriptors
		self._max_packet_size = max_packet_size

		super().__init__()

	def elaborate(self, platform) -> Module:
		m = Module()

		interface                = self.interface
		setup: SetupPacket       = interface.setup
		tx: USBInStreamInterface = interface.tx

		m.submodules.get_desc_set = desc_set_handler = GetDescriptorSetHandler(self.descriptors)
		m.d.comb += [
			desc_set_handler.request.eq(setup.request),
			desc_set_handler.length.eq(setup.length),
		]

		with m.If(self.handler_condition(setup)):
			with m.FSM(domain = 'usb'):
				with m.State('IDLE'):
					with m.If(setup.received):
						with m.Switch(setup.index):
							with m.Case(MicrosoftRequests.GET_DESCRIPTOR_SET):
								m.next = 'CHECK_GET_DESCRIPTOR_SET'
							with m.Default():
								m.next = 'UNHANDLED'
				with m.State('CHECK_GET_DESCRIPTOR_SET'):
					with m.If(setup.is_in_request  & (setup.value == 0)):
						m.next = 'GET_DESCRIPTOR_SET'
					with m.Else():
						m.next = 'UNHANDLED'
				with m.State('GET_DESCRIPTOR_SET'):
					expecting_ack = Signal()

					m.d.comb += [
						desc_set_handler.tx.attach(tx),
						interface.handshakes_out.stall.eq(desc_set_handler.stall),
					]

					with m.If(interface.data_requested):
						m.d.comb += [
							desc_set_handler.start.eq(1),
						]
						m.d.usb += [
							expecting_ack.eq(1),
						]

					with m.If(interface.handshakes_in.ack & expecting_ack):
						next_start_pos = desc_set_handler.start_pos + self._max_packet_size

						m.d.usb += [
							desc_set_handler.start_pos.eq(next_start_pos),
							self.interface.tx_data_pid.eq(~self.interface.tx_data_pid),
							expecting_ack.eq(0)
						]

					with m.If(interface.status_requested):
						m.d.comb += [
							interface.handshakes_out.ack.eq(1),
						]
						m.next = 'IDLE'
					with m.Elif(desc_set_handler.stall):
						m.next = 'IDLE'

				with m.State('UNHANDLED'):
					with m.If(interface.data_requested | interface.status_requested):
						m.d.comb += [
							interface.handshakes_out.stall.eq(1),
						]
						m.next = 'IDLE'

		return m

	def handler_condition(self, setup: SetupPacket) -> Operator:
		'''
		Defines the setup packet conditions under which the request handler will operate.

		This is used to gate the handler's operation and forms part of the condition under which
		the stall-only handler will be triggered.

		Parameters
		----------
		setup
			A grouping of signals used to describe the most recent setup packet the control interface has seen.

		Returns
		-------
		:py:class:`amranth.hdl.ast.Operator`
			A combinatorial operation defining the sum conditions under which this handler will operate.

		Notes
		-----
		The condition for the operation of this handler is defined as being:

		* A Vendor request directly to the device.
		* for either index value ``0x07`` or ``0x08``, respectively meaning:

			* ``GET_DESCRIPTOR_SET``, and
			* ``SET_ALTERNATE_ENUM``

		The latter has not been given support as we don't currently allow swapping out the device
		descriptors in this manner.

		'''
		return (
			(setup.type      == USBRequestType.VENDOR)      &
			(setup.recipient == USBRequestRecipient.DEVICE) & (
				(setup.index == MicrosoftRequests.GET_DESCRIPTOR_SET) |
				(setup.index == MicrosoftRequests.SET_ALTERNATE_ENUM)
			)
		)
