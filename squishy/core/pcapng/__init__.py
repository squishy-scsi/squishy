# SPDX-License-Identifier: BSD-3-Clause

'''
This modules contains a surprisingly complete implementation of the PCAPNG file format
for use with the Squishy SCSI Analyzer applet to generate traffic captures.

'''


from datetime  import timedelta
from enum      import IntEnum
from io        import SEEK_END, SEEK_SET, BytesIO
from pathlib   import Path
from typing    import BinaryIO, Final, Iterable, Self

from arrow     import Arrow, now
from construct import (
	Aligned, BitsInteger, BitStruct, Bytes, Check, Computed, Const, CString, Default, Enum, Flag, GreedyRange,
	Hex, HexDump, If, Int8ul, Int16ul, Int32ul, Int64ul, PaddedString, Pass, Rebuild, RepeatUntil, Struct,
	Switch, len_, this
)

from .linktype import (
	SCSIDataRate, SCSISpeed, SCSIType, SCSIWidth, SCSIFrameType, linktype_parallel_scsi, scsi_bus_opt
)

__all__ = (
	'PCAPNGStream',
)


TS_EPOCH: Final = Arrow(1970, 1, 1)

# Convert a raw PCAPNG timestamp to an Arrow datetime
def _timestamp_from_raw(this):
	timestamp = (this.raw.high << 32) + this.raw.low
	return TS_EPOCH.shift(seconds = timestamp * 1e-6)

# Convert a datetime/Arrow timestamp to a PCAPNG raw timestamp for construct
def _timestamp_to_raw(this):
	timestamp = this.value
	# For now, assume that if the object is not an Arrow datetime, it's a standard library one
	if not isinstance(timestamp, Arrow):
		timestamp = Arrow.fromdatetime(timestamp)
	value: timedelta = timestamp - TS_EPOCH
	value = int(value.total_seconds() * 1e6)
	return { 'low': value & 0xffffffff, 'high': value >> 32 }

timestamp = 'Timestamp' / Struct(
	'raw' / Rebuild(Struct(
		'high' / Hex(Int32ul),
		'low'  / Hex(Int32ul),
	), _timestamp_to_raw),
	'value' / Computed(_timestamp_from_raw),
)

class LinkType(IntEnum):
	''' PCAPNG LinkType '''

	# User DLTs
	USER00 = 0x0093
	''' DLT_USER00 '''
	USER01 = 0x0094
	''' DLT_USER01 '''
	USER02 = 0x0095
	''' DLT_USER02 '''
	USER03 = 0x0096
	''' DLT_USER03 '''
	USER04 = 0x0097
	''' DLT_USER04 '''
	USER05 = 0x0098
	''' DLT_USER05 '''
	USER06 = 0x0099
	''' DLT_USER06 '''
	USER07 = 0x009A
	''' DLT_USER07 '''
	USER08 = 0x009B
	''' DLT_USER08 '''
	USER09 = 0x009C
	''' DLT_USER09 '''
	USER10 = 0x009D
	''' DLT_USER10 '''
	USER11 = 0x009E
	''' DLT_USER11 '''
	USER12 = 0x009F
	''' DLT_USER12 '''
	USER13 = 0x00A0
	''' DLT_USER13 '''
	USER14 = 0x00A1
	''' DLT_USER14 '''
	USER15 = 0x00A2
	''' DLT_USER15 '''

	# NOTE(aki): Temporary:tm:
	PARALLEL_SCSI = USER07

link_type = 'Link Type' / Enum(Int16ul, LinkType)


class BlockType(IntEnum):
	''' PCAPNG Block Type '''

	SECTION_HEADER        = 0x0A0D0D0A
	''' PCAPNG capture header '''
	INTERFACE_DESCRIPTION = 0x00000001
	''' Capture interface description '''
	SIMPLE_PACKET         = 0x00000003
	''' Simple capture storage block '''
	NAME_RESOLUTION       = 0x00000004
	''' Name <-> Address mapping block '''
	INTERFACE_STATISTICS  = 0x00000005
	''' Capture interface statistics '''
	ENHANCED_PACKET       = 0x00000006
	''' Enhanced capture storage block '''
	DECRYPTION_SECRETS    = 0x0000000A
	''' Capture session token/secret storage for decryption '''

	CUSTOM0 = 0x00000BAD
	''' Vendor defined block '''
	CUSTOM1 = 0x00004BAD
	''' Like CUSTOM0, but not copied '''

block_type = 'Block Type' / Enum(Int32ul, BlockType)


class OptionType(IntEnum):
	''' PCAPNG Option Types '''

	# "Bare" Option Types
	END     = 0x0000
	''' End of list of block Options '''
	COMMENT = 0x0001
	''' UTF-8 String: Block comment '''

	CUSTOM0 = 0x0BAC
	''' Arbitrary UTF-8 String option '''
	CUSTOM1 = 0x0BAD
	''' Arbitrary binary data option '''
	CUSTOM2 = 0x4BAC
	''' Non-copyable version of ``CUSTOM0`` '''
	CUSTOM3 = 0x4BAD
	''' Non-copyable version of ``CUSTOM1`` '''

	# Section Header Block Options
	SHB_HARDWARE = 0x0002
	''' UTF-8 String: Hardware on which this PCAPNG file was generated (not the interface) '''
	SHB_OS       = 0x0003
	''' UTF-8 String: Operating System on which this PCAPNG file was generated '''
	SHB_USERAPPL = 0x0004
	''' UTF-8 String: Application that generated this PCAPNG file '''

	# Interface Description Block Options
	IF_NAME        = 0x0002
	''' UTF-8 String: The interface name '''
	IF_DESCRIPTION = 0x0003
	''' UTF-8 String: The interface description '''
	IF_IPV4ADDR    = 0x0004
	''' Bytes ( 8): IPv4 Address and Netmask '''
	IF_IPV6ADDR    = 0x0005
	''' Bytes (17): IPv6 Address and Prefix Length '''
	IF_MACADDR     = 0x0006
	''' Bytes ( 6): Interface EUI MAC Address '''
	IF_EUIADDR     = 0x0007
	''' Bytes ( 8): Interface EUI Address '''
	IF_SPEED       = 0x0008
	''' uint64: Interface speed in bits-per-second (bps) '''
	IF_TSRESOL     = 0x0009
	''' uint8: interface timestamp resolution '''
	IF_TZONE       = 0x000A
	''' uint32: Unused/Do-not-use '''
	IF_FILTER      = 0x000B
	''' UTF-8 String: Filter used to generate capture for this interface if any '''
	IF_OS          = 0x000C
	''' UTF-8 String: Operating System this interface was installed on '''
	IF_FCSLEN      = 0x000D
	''' uint8: Frame-check-sequence length in bits '''
	IF_TSOFFSET    = 0x000E
	''' uint64: Offset adjustment to apply to capture block timestamps, omit or 0 for absolute '''
	IF_HARDWARE    = 0x000F
	''' UTF-8 String: Interface hardware description '''
	IF_TXSPEED     = 0x0010
	''' uint64: Interface transmit speed in bits-per-second '''
	IF_RXSPEED     = 0x0011
	''' uint64: Interface receive speed in bits-per-second '''
	IF_IANA_TZNAME = 0x0012
	''' UTF-8 String: Timezone in which the interface was when capture occurred '''

	# Enhanced Packet Block Options
	EPB_FLAGS     = 0x0002
	''' ehb_flags: Enhanced Packet Block flags structure '''
	EPB_HASH      = 0x0003
	''' bytes (1, N): packet contents hash, first byte is type followed by N digest bytes '''
	EPB_DROPCOUNT = 0x0004
	'''  uint64: Number of packets lost by the interface and OS between this packet and the preceding '''
	EPB_PACKETID  = 0x0005
	''' uint64: Packet unique identifier '''
	EPB_QUEUE     = 0x0006
	''' uint32: Interface queue ID '''
	EPB_VERDICT   = 0x0007
	''' bytes (1, N): packet verdict, first byte is type, followed by N bytes of the verdict data '''
	EPB_PID_TID   = 0x0008
	''' uint32,uint32: Process ID and Thread ID pair of the process that originated this packet '''

	# Name Resolution Block Options

	NRB_DNSNAME    = 0x0002
	''' UTF-8 String: Name of the DNS server used to resolve names '''
	NRB_DNSIP4ADDR = 0x0003
	''' bytes ( 4): IPv4 Address of the DNS server used to resolve names '''
	NRB_DNSIP6ADDR = 0x0004
	''' bytes (16): IPv6 Address of the DNS server used to resolve names '''

	# Interface Statistics Block Options
	ISB_STARTTIME    = 0x0002
	''' timestamp: Start of capture on given interface '''
	ISB_ENDTIME      = 0x0003
	''' timestamp: End of capture on given interface '''
	ISB_IFRECV       = 0x0004
	''' uint64: Total number of packets received on the interface from start of capture '''
	ISB_IFDROP       = 0x0005
	''' uint64: Total number of dropped packets on the interface from the start of capture '''
	ISB_FILTERACCEPT = 0x0006
	''' uint64: Number of packets accepted by the filter from start of capture '''
	ISB_OSDROP       = 0x0007
	''' uint64: Number of packets dropped by the OS from the start of capture '''
	ISB_USERDELIV    = 0x0008
	''' uint64: Number of packets delivered to the user from the start of the capture '''

option_type = 'Option Type' / Enum(Int16ul, OptionType)


class SecretType(IntEnum):
	''' PCAPNG Decryption Secrets Block Type '''

	SSH_KEY_LOG       = 0x5353484B
	''' SSH Key Log '''
	TLS_KEY_LOG       = 0x544C534B
	''' TLS Key Log '''
	OPC_UA_KEY_LOG    = 0x55414B4C
	''' OPC UA Key Log '''
	WIREGAURD_KEY_LOG = 0x57474B4C
	''' WireGuard Key Log '''
	ZIGBEE_NWK_KEY    = 0x5A4E574B
	''' ZigBee NWK Key and ZigBee PANID '''
	ZIGBEE_APS_KEY    = 0x5A415053
	''' ZigBee APS Key '''

secret_type = 'Secrete Type' / Enum(Int32ul, SecretType)

# Enhanced Packed Block flags Option
epb_flags = 'EPB Flags' / BitStruct(
	'dir'     / BitsInteger(2), # Packet Direction: 01 in; 10 out; 00 unk
	'rcpt'    / BitsInteger(3), # Reception type: 001 unicast; 010 multi; 011 broad; 100 promiscuous
	'fcs'     / BitsInteger(4), # FCS Length:
	'chk_rdy' / Flag,           # Checksum not ready
	'chk_vld' / Flag,           # Checksum valid
	'tcp_off' / Flag,           # TCP Segmentation Offloaded
	'rsvd'    / BitsInteger(4), # Reserved
	'errors'  / BitsInteger(16) # Link-Layer dependant errors
)

# This uses PaddedString because the strings encoded are not guaranteed to be NUL terminated
# which means, if one were to use CString, it would reading past the intended EOS and into the
# next control block structure. CString has no way to length limit the read.
option_value = Aligned(4, Switch(
	lambda this: int(this.type), {
		OptionType.END: Pass,
		OptionType.COMMENT: PaddedString(this.length, 'utf8'),

		OptionType.CUSTOM0: PaddedString(this.length, 'utf8'),
		OptionType.CUSTOM1: Switch(lambda this: int(this._.type), {
			BlockType.INTERFACE_DESCRIPTION: scsi_bus_opt # For LINKTYPE_PARALLEL_SCSI
		}, HexDump(Bytes(this.length))),
		OptionType.CUSTOM2: PaddedString(this.length, 'utf8'),
		OptionType.CUSTOM3: HexDump(Bytes(this.length)),

		# Deal with the overlapping option types
		0x0002: Switch(lambda this: int(this._.type), {
			BlockType.SECTION_HEADER:        PaddedString(this.length, 'utf8'), # SHB_HARDWARE
			BlockType.INTERFACE_DESCRIPTION: PaddedString(this.length, 'utf8'), # IF_NAME
			BlockType.ENHANCED_PACKET:       epb_flags,                         # EPB_FLAGS
			BlockType.NAME_RESOLUTION:       PaddedString(this.length, 'utf8'), # NRB_DNSNAME
			BlockType.INTERFACE_STATISTICS:  timestamp,                         # ISB_STARTTIME
		}, HexDump(Bytes(this.length))),
		0x0003: Switch(lambda this: int(this._.type), {
			BlockType.SECTION_HEADER:        PaddedString(this.length, 'utf8'), # SHB_OS
			BlockType.INTERFACE_DESCRIPTION: PaddedString(this.length, 'utf8'), # IF_DESCRIPTION
			BlockType.ENHANCED_PACKET:       Bytes(this.length),                # HPB_HASH
			BlockType.NAME_RESOLUTION:       Bytes(this.length),                # NRB_DNSIP4ADDR
			BlockType.INTERFACE_STATISTICS:  timestamp,                         # ISB_ENDTIME
		}, HexDump(Bytes(this.length))),
		0x0004: Switch(lambda this: int(this._.type), {
			BlockType.SECTION_HEADER:        PaddedString(this.length, 'utf8'),            # SHB_USERAPPL
			BlockType.INTERFACE_DESCRIPTION: Struct('addr' / Bytes(4), 'mask' / Bytes(4)), # IF_IPV4ADDR
			BlockType.ENHANCED_PACKET:       Int64ul,                                      # EPB_DROPCOUNT
			BlockType.NAME_RESOLUTION:       Bytes(this.length),                           # NRB_DNSIP6ADDR
			BlockType.INTERFACE_STATISTICS:  Int64ul,                                      # ISB_IFRECV
		}, HexDump(Bytes(this.length))),
		0x0005: Switch(lambda this: int(this._.type), {
			BlockType.INTERFACE_DESCRIPTION: Struct('addr' / Bytes(16), 'prefix' / Bytes(1)), # IF_IPV6ADDR
			BlockType.ENHANCED_PACKET:       Int64ul,                                         # EPB_PACKETID
			BlockType.INTERFACE_STATISTICS:  Int64ul,                                         # ISB_IFDROP
		}, HexDump(Bytes(this.length))),
		0x0006: Switch(lambda this: int(this._.type), {
			BlockType.INTERFACE_DESCRIPTION: Bytes(this.length), # IF_MACADDR
			BlockType.ENHANCED_PACKET:       Int32ul,            # EPB_QUEUE
			BlockType.INTERFACE_STATISTICS:  Int64ul,            # ISB_FILTERACCEPT
		}, HexDump(Bytes(this.length))),
		0x0007: Switch(lambda this: int(this._.type), {
			BlockType.INTERFACE_DESCRIPTION: Bytes(this.length), # IF_EUIADDR
			BlockType.ENHANCED_PACKET:       Bytes(this.length), # EPB_VERDICT
			BlockType.INTERFACE_STATISTICS:  Int64ul,            # ISB_OSDROP
		}, HexDump(Bytes(this.length))),
		0x0008: Switch(lambda this: int(this._.type), {
			BlockType.INTERFACE_DESCRIPTION: Int64ul,                                  # IF_SPEED
			BlockType.ENHANCED_PACKET:       Struct('pid' / Int32ul, 'tid' / Int32ul), # EPB_PID_TID
			BlockType.INTERFACE_STATISTICS:  Int64ul,                                  # ISB_USERDELIV
		}, HexDump(Bytes(this.length))),
		0x0009: Switch(lambda this: int(this._.type), {
			BlockType.INTERFACE_DESCRIPTION: Int8ul, # IF_TSRESOL
		}, HexDump(Bytes(this.length))),
		0x000A: Switch(lambda this: int(this._.type), {
			BlockType.INTERFACE_DESCRIPTION: Int32ul, # IF_TZONE
		}, HexDump(Bytes(this.length))),
		0x000B: Switch(lambda this: int(this._.type), {
			BlockType.INTERFACE_DESCRIPTION: PaddedString(this.length, 'utf8'), # IF_FILTER
		}, HexDump(Bytes(this.length))),
		0x000C: Switch(lambda this: int(this._.type), {
			BlockType.INTERFACE_DESCRIPTION: PaddedString(this.length, 'utf8'), # IF_OS
		}, HexDump(Bytes(this.length))),
		0x000D: Switch(lambda this: int(this._.type), {
			BlockType.INTERFACE_DESCRIPTION: Int8ul, # IF_FCSLEN
		}, HexDump(Bytes(this.length))),
		0x000E: Switch(lambda this: int(this._.type), {
			BlockType.INTERFACE_DESCRIPTION: Int64ul, # IF_TSOFFSET
		}, HexDump(Bytes(this.length))),
		0x000F: Switch(lambda this: int(this._.type), {
			BlockType.INTERFACE_DESCRIPTION: PaddedString(this.length, 'utf8'), # IF_HARDWARE
		}, HexDump(Bytes(this.length))),
		0x0010: Switch(lambda this: int(this._.type), {
			BlockType.INTERFACE_DESCRIPTION: Int64ul, # IF_TXSPEED
		}, HexDump(Bytes(this.length))),
		0x0011: Switch(lambda this: int(this._.type), {
			BlockType.INTERFACE_DESCRIPTION: Int64ul, # IF_TXSPEED
		}, HexDump(Bytes(this.length))),
		0x0012: Switch(lambda this: int(this._.type), {
			BlockType.INTERFACE_DESCRIPTION: PaddedString(this.length, 'utf8'), # IF_IANA_TZNAME
		}, HexDump(Bytes(this.length))),
	},
	HexDump(Bytes(this.length)),
))

def _option_len(this) -> int:
	if isinstance(this.value, str):
		value = CString('utf8').build(this.value, **this)[:-1]
	else:
		value = option_value.build(this.value, **this)
	return len(value)

option = 'Option' / Struct(
	'type'   / Hex(option_type),
	'length' / Rebuild(Int16ul, _option_len),
	'value'  / If(
		this.length > 0,
		option_value
	),
)

_SHB_BYTE_ORDER_MAGIC = 0x1A2B3C4D

section_header_block = 'Section Header Block' / Struct(
	'bom'     / Const(_SHB_BYTE_ORDER_MAGIC, Int32ul),
	'version' / Struct(
		'major' / Const(1, Int16ul),
		'minor' / Const(0, Int16ul),
	),
	'section_len' / Default(Int64ul, 0xFFFF_FFFF_FFFF_FFFF),
)

interface_description_block = 'Interface Description Block' / Struct(
	'type'     / Hex(link_type),
	'reserved' / Const(0, Int16ul),
	'snap_len' / Default(Int32ul, 0),
)

def _packet_data_len(this):
	if hasattr(this, 'captured_len'):
		return this.captured_len
	# Handle sizeof() calculation phase
	elif hasattr(this._.data, 'captured_len'):
		return this._.data.captured_len
	# Handle build phase
	return len(this._.data['packet_data'])

enhanced_packet_block = 'Enhanced Packet Block' / Aligned(4, Struct(
	'interface_id' / Default(Int32ul, 0),
	'timestamp'    / timestamp,
	'captured_len' / Rebuild(Int32ul, len_(this.packet_data)),
	'actual_len'   / Default(Int32ul, this.captured_len),
	'packet_data'  / HexDump(Bytes(lambda this: _packet_data_len(this))),
))

simple_packed_block = 'Simple Packet Block' / Aligned(4, Struct(
	'original_len' / Hex(Int32ul),
	'packet_data'  / HexDump(Bytes(lambda this: _packet_data_len(this)))
))

name_resolution_block = 'Name Resolution Block' / Struct(

)

interface_statistics_block = 'Interface Statistics Block' / Struct(
	'interface_id' / Hex(Int32ul),
	'timestamp'    / timestamp,
)

decryption_secrets_block = 'Decryption Secrets Block' / Aligned(4, Struct(
	'type' / Hex(secret_type),
	'len'  / Int32ul,
	'data' / HexDump(Bytes(this.len))
))

options_block = RepeatUntil(
	lambda obj, _, __: int(obj['type']) == OptionType.END,
	option
)

def _block_len(this) -> int:
	if not this._building:
		options_len = len(options_block.block(this.options, **this))
	else:
		# Special case to handle the building phase *grumbles*
		if this.options is None:
			options_len = 0
		else:
			options_len = len(options_block.build(this.options, **this))

	return (
		this._subcons.type.sizeof(**this) +
		this._subcons.data.sizeof(**this) +
		options_len +
		Int32ul.sizeof() * 2
	)

def _options_len(this) -> int:
	return this.len1 - (
		this._subcons.type.sizeof(**this) +
		this._subcons.data.sizeof(**this) +
		Int32ul.sizeof() * 2
	)

pcapng_block = 'Block' / Struct(
	'type' / Hex(block_type),
	'len1' / Rebuild(Int32ul, _block_len),
	'data' / Switch(lambda this: int(this.type), {
			BlockType.SECTION_HEADER:        section_header_block,
			BlockType.INTERFACE_DESCRIPTION: interface_description_block,
			BlockType.SIMPLE_PACKET:         simple_packed_block,
			# BlockType.NAME_RESOLUTION:       name_resolution_block,
			BlockType.INTERFACE_STATISTICS:  interface_statistics_block,
			BlockType.ENHANCED_PACKET:       enhanced_packet_block,
			# BlockType.DECRYPTION_SECRETS:    decryption_secrets_block,
			# BlockType.CUSTOM0: Pass,
			# BlockType.CUSTOM1: Pass,
		},
		HexDump(Bytes(this.len1))
	),
	'size'    / Computed(lambda this: this._subcons.data.sizeof(**this)),
	'options' / If(
		lambda this: _options_len(this) > 0,
		options_block
	),
	'len2' / Rebuild(Int32ul, this.len1),
	Check(this.len1 == this.len2),
)


pcapng = 'PCAPNG' / GreedyRange(pcapng_block)

# NOTE(aki): We can't use `build_stream` here because construct wants to seek around,
def write_shb(
	stream: BinaryIO, /, hardware: str | None = None, os: str | None = None, writer: str | None = None,
	*, options: Iterable = ()
) -> int:
	'''
	Write a PCAPNG Section Header Block


	Parameters
	----------
	stream : BinaryIO
		The output stream to write to.

	hardware : str | None
		The hardware string this capture was done on.

	os : str | None
		The os this capture was done on.

	writer : str | None
		The software writing this capture.

	options : Iterable
		Any extra options to attach to the block. (default: [])
	'''


	_options = [
		*options,
	]

	# Populate options
	if hardware is not None:
		_options.append({ 'type': OptionType.SHB_HARDWARE, 'value': hardware })

	if os is not None:
		_options.append({ 'type': OptionType.SHB_OS, 'value': os })

	if writer is not None:
		_options.append({ 'type': OptionType.SHB_USERAPPL, 'value': writer })
	else:
		# We always populate at least the writer
		_options.append({ 'type': OptionType.SHB_USERAPPL, 'value': 'Squishy PCAPNG Generator' })
	# Terminate the block options
	_options.append({ 'type': OptionType.END, 'value': None })

	# Write out the actual block
	return stream.write(pcapng_block.build({
		'type': BlockType.SECTION_HEADER,
		'data': None,
		'options': _options
	}))


def write_idb(
	stream: BinaryIO, /, link_type: LinkType, snap_len: int, name: str, *, options: Iterable = ()
) -> int:
	'''
	Write an Interface Description Block


	Parameters
	----------
	stream : BinaryIO
		The output stream to write to.

	link_type : LinkType
		The LINKTYPE/DLT output from this interface.

	snap_len : int
		The maximum number of bytes captured from each packet, 0 for no limit.

	name : str
		The name of this interface.

	options : Iterable
		Any extra options to attach to the block. (default: [])
	'''

	_options = [
		*options,
		{ 'type': OptionType.IF_NAME,    'value': name },
		{ 'type': OptionType.END,        'value': None }
	]

	return stream.write(pcapng_block.build({
		'type': BlockType.INTERFACE_DESCRIPTION,
		'data': {
			'type': link_type,
			'snap_len': snap_len
		},
		'options': _options
	}))

def write_epb(
	stream: BinaryIO, /, interface: int, data: BinaryIO | bytes | bytearray, ts: Arrow | None = None,
	*, options: Iterable = ()
) -> int:
	'''
	Write an Extended Packet block


	Parameters
	----------
	stream : BinaryIO
		The output stream to write to.

	interface : int
		The interface this packet came from.

	data : BinaryIO | bytes | bytearray
		The raw data to write into the packet.

	ts : Arrow | None
		The capture timestamp of this packet.

	options : Iterable
		Any extra options to attach to the block. (default: [])
	'''

	if len(options) > 0:
		_options = [
			*options,
			{ 'type': OptionType.END, 'value': None }
		]
	else:
		_options = None

	if isinstance(data, (bytearray, bytes)):
		data_len = len(data)
	else:
		_data_offset = data.tell()
		data.seek(0, SEEK_END)
		_data_end  = data.tell()
		data_len = _data_end - _data_offset
		data.seek(_data_offset, SEEK_SET)

	return stream.write(pcapng_block.build({
		'type': BlockType.ENHANCED_PACKET,
		'data': {
			'inteface_id': interface,
			'timestamp': { 'value': ts if ts is not None else now('UTC') },
			'captured_len': data_len,
			'packet_data': data
		},
		'options': _options
	}))

def write_spb(
	stream: BinaryIO, /, data: BinaryIO | bytes | bytearray, *, options: Iterable = ()
) -> int:
	'''
	Write a Simple Packet Block

	Warning
	-------
	It is highly advised to not make use of Simple Packet Blocks, the general lack of timestamps
	and other such metadata is not worth the very small space savings that may be achieved by using
	them.

	This is only included for completeness sake.

	Parameters
	----------
	stream : BinaryIO
		The output stream to write to.

	data : BinaryIO | bytes | bytearray
		The raw data to write into the packet.

	options : Iterable
		Any extra options to attach to the block. (default: [])
	'''

	if len(options) > 0:
		_options = [
			*options,
			{ 'type': OptionType.END, 'value': None }
		]
	else:
		_options = None

	if isinstance(data, (bytearray, bytes)):
		data_len = len(data)
	else:
		_data_offset = data.tell()
		data.seek(0, SEEK_END)
		_data_end  = data.tell()
		data_len = _data_end - _data_offset
		data.seek(_data_offset, SEEK_SET)

	return stream.write(pcapng_block.build({
		'type': BlockType.SIMPLE_PACKET,
		'data': {
			'original_len': data_len,
			'packet_data': data
		},
		'options': _options
	}))

def write_nrb(
	stream: BinaryIO, /, *, options: Iterable = ()
) -> int:
	'''
	Write a Name Resolution Block

	Parameters
	----------
	stream : BinaryIO
		The output stream to write to.

	options : Iterable
		Any extra options to attach to the block. (default: [])
	'''
	if len(options) > 0:
		_options = [
			*options,
			{ 'type': OptionType.END, 'value': None }
		]
	else:
		_options = None

	return stream.write(pcapng_block.build({
		'type': BlockType.NAME_RESOLUTION,
		'data': {

		},
		'options': _options
	}))


def write_isb(
	stream: BinaryIO, /, interface: int , ts: Arrow | None = None, *, options: Iterable = ()
) -> int:
	'''
	Write an Interface Statistics Block


	Parameters
	----------
	stream : BinaryIO
		The output stream to write to.

	interface : int
		The interface these statistics belong to.

	ts : Arrow | None
		The timestamp these statistics were taken.

	options : Iterable
		Any extra options to attach to the block. (default: [])
	'''

	if len(options) > 0:
		_options = [
			*options,
			{ 'type': OptionType.END, 'value': None }
		]
	else:
		_options = None

	return stream.write(pcapng_block.build({
		'type': BlockType.INTERFACE_STATISTICS,
		'data': {
			'interface_id': interface,
			'timestamp': { 'value': ts if ts is not None else now('UTC') },
		},
		'options': _options
	}))


def write_dsb(
	stream: BinaryIO, /, *, options: Iterable = ()
) -> int:
	'''
	Write a Description Secrets Block

	Parameters
	----------
	stream : BinaryIO
		The output stream to write to.

	options : Iterable
		Any extra options to attach to the block. (default: [])
	'''
	if len(options) > 0:
		_options = [
			*options,
			{ 'type': OptionType.END, 'value': None }
		]
	else:
		_options = None

	return stream.write(pcapng_block.build({
		'type': BlockType.DECRYPTION_SECRETS,
		'data': {

		},
		'options': _options
	}))


def write_psf(
	stream: BinaryIO, /, interface: int, data: BinaryIO | bytes | bytearray, type: SCSIFrameType,
	orig: int, dest: int,
	ts: Arrow | None = None,
	*, options: Iterable = ()
) -> int:
	'''
	Write a Parallel SCSI Frame wrapped in an Extended Packet Block to
	the stream.

	Parameters
	----------
	stream : BinaryIO
		The output stream to write to.

	interface : int
		The interface this packet came from.

	data : BinaryIO | bytes | bytearray
		The raw data to write into the packet.

	type : SCSIFrameType
		The type of Parallel SCSI Frame we're writing.

	orig : int

	dest : int

	ts : Arrow | None
		The capture timestamp of this packet.

	options : Iterable
		Any extra options to attach to the block. (default: [])
	'''

	if isinstance(data, (bytearray, bytes)):
		data_len = len(data)
	else:
		_data_offset = data.tell()
		data.seek(0, SEEK_END)
		_data_end  = data.tell()
		data_len = _data_end - _data_offset
		data.seek(_data_offset, SEEK_SET)

	frame_data = linktype_parallel_scsi.build({
		'len': 0,
		'type': type,
		'orig_id': orig,
		'dest_id': dest,
		'data_len': data_len,
		'data': data
	})

	return write_epb(stream, interface, frame_data, ts, options = options)

class _PCAPNGInterface:
	'''
	This is a wrapper that allows you to treat a PCAPNG interface as an object and write packets
	and statistics with it.

	Warning
	-------
	This class should not be manually created, instead it should be from the result of a `emit_interface`
	from a PCAPNGStream object.
	'''

	@property
	def id(self) -> int:
		''' Get the interface ID '''
		return self._id

	@property
	def name(self) -> str:
		''' Get the interface name '''
		return self._name

	@property
	def link_type(self) -> LinkType:
		return self._link_type

	def __init__(self, *, _id: int, _name: str, _type: LinkType, _data: BinaryIO) -> None:
		self._id        = _id
		self._name      = _name
		self._link_type = _type
		self._data      = _data

	def emit_packet(
		self, data: BinaryIO | bytes | bytearray, ts: Arrow | None = None, *, options: Iterable = ()
	) -> None:
		'''
		Emit a packet associated to this interface

		Parameters
		----------
		data : BinaryIO | bytes | bytearray
			The raw data to write into the packet.

		ts : Arrow | None
			The capture timestamp of this packet.

		options : Iterable
			Any extra options to attach to the block. (default: [])
		'''

		if self._data.closed:
			raise RuntimeError('PCAPNG Stream closed, unable to emit packet')

		write_epb(self._data, self._id, data, ts, options = options)

class PCAPNGStream:
	'''
	A PCAPNG stream-based emitter

	Some example usage is as follows:

	.. code-block:: python

		with PCAPNGStream('/tmp/garbage.pcapng') as stream:
			stream.emit_header(hardware = 'trash-can')
			iface = stream.emit_interface(LinkType.USER00, 'trash')
			for _ in range(128):
				iface.emit_packet(randbytes(randint(128, 4096)))

	'''

	def emit_header(
		self, *, hardware: str, writer: str | None = None, os: str | None = None, options: Iterable = ()
	):
		'''
		Emit a Section Header Block.

		This should be done at the very start of the PCAPNG stream.

		Parameters
		----------
		hardware : str | None
			The hardware being used to do the capture.


		options : Iterable
			Any extra options to attach to the block. (default: [])
		'''

		# If there is no writer set, give it some generic name
		if writer is None:
			writer = 'Squishy PCAPNG Stream'

		# If the OS isn't set, give us a rough approximation
		if os is None:
			import platform
			uname = platform.uname()

			os = f'{uname.system} {uname.release}'

		# Emit the Section Header Block to the stream and flush
		write_shb(self._data, hardware, os, writer, options = options)
		self._data.flush()

	def emit_interface(self, type: LinkType, name: str, *, options: Iterable = ()) -> _PCAPNGInterface:
		'''
		Create a new Interface Description Block and obtain a proxy object to
		use to add packets to the PCAPNG Stream.

		Parameters
		----------
		type : LinkType
			The link-layer type of this interface.

		name : str
			The name of this interface.

		options : Iterable
			Any extra options to attach to the block. (default: [])

		Returns
		-------
		_PCAPNGInterface
			A PCAPNGStream proxy object for interacting with the newly added interface
		'''

		write_idb(self._data, type, 0, name, options = options)
		self._data.flush()
		self._last_interface += 1
		return _PCAPNGInterface(_id = self._last_interface, _name = name, _type = type, _data = self._data)

	def flush(self) -> None:
		if not self._data.closed:
			self._data.flush()

	def __init__(self, file: str | Path | BinaryIO | bytes | bytearray, /) -> None:

		if isinstance(file, (str, Path)):
			# This is fine as `PurePath` will just flatten the path
			self._file = Path(file).resolve()
			self._data = self._file.open('wb')
		elif isinstance(file, (bytes, bytearray)):
			# Convert a `bytes` or `bytearray` into a buffered thing
			self._data = BytesIO(file)
		elif isinstance(file, BinaryIO):
			self._data = file
		else:
			raise TypeError(f'`file` must be either a string, path, bytes, bytearray, or BinaryIO, not {file!r}')

		self._last_interface = -1


	def close(self) -> None:
		if not self._data.closed:
			self._data.flush()
			self._data.close()

	def __enter__(self) -> Self:
		return self

	def __exit__(self, type: type | None, *_) -> bool | None:
		if type is None:
			self.close()
		else:
			# There was an exception, bubble it up
			return False


if __name__ == '__main__':
	from random import randbytes, randint


	test_file = Path('/tmp/test.pcapng').resolve()

	with PCAPNGStream(test_file) as stream:
		stream.emit_header(hardware = 'Test')
		iface = stream.emit_interface(LinkType.USER00, 'test0')
		for _ in range(128):
			iface.emit_packet(randbytes(randint(128, 4096)))
