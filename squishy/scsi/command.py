# SPDX-License-Identifier: BSD-3-Clause

from enum      import IntEnum, Enum, auto, unique
from itertools import takewhile
from typing    import Any

from construct import (
	Struct, Subconstruct, Const, Default,
	Int8ul, Int16ul, Int24ul, Int32ul, Int64ul,
	Int8sl, Int16sl, Int24sl, Int32sl, Int64sl,
	Int8ub, Int16ub, Int24ub, Int32ub, Int64ub,
	Int8sb, Int16sb, Int24sb, Int32sb, Int64sb,
	BytesInteger, Bytewise,
	BitStruct, BitsInteger, Bitwise
)

__all__ = (
	'DeviceType',
	'GroupCode',
	'SCSICommand',
	'SCSICommand6',
	'SCSICommand10',
	'SCSICommand12',
	'SCSICommandField',

	'CommandEmitter',
)

@unique
class DeviceType(Enum):
	'''SCSI Device Type'''

	COMMON            = auto()
	DIRECT_ACCESS     = auto()
	SEQUENTIAL_ACCESS = auto()
	PRINTER           = auto()
	PROCESSOR         = auto()
	WORM              = auto()
	RO_DIRECT_ACCESS  = auto()

@unique
class GroupCode(IntEnum):
	'''SCSI Command Group Code

	Each SCSI command belongs to a group that defines its characteristics. It
	also defines which commands are optional (``o``), mandatory (``m``),
	reserved (``r``), shared (``s``), or vendor specific (``v``).

	If a command is optional (``o``) then the target does not need to implement it. If the command is
	mandatory (``m``) then it must be implemented by the target. If a command is reserved (``r``) then
	it should not be implemented by the target, if a command is shared (``s``) then the opcode depends on
	the target device class, and may have multiple meanings. Finally, if the command is vendor specific (``v``)
	then the command might be implemented depending on the target vendor and its meaning is not standardized.

	Each group code is three-bits long, allowing for a maximum of eight groups, with the
	remaining five-bits in the command opcode for the command identifier itself.

	+-------------+----------------------+
	| Groupe Code | Group Description    |
	+=============+======================+
	| ``0b000``   |   Six-byte Commands  |
	+-------------+----------------------+
	| ``0b001``   |   Ten-byte Commands  |
	+-------------+----------------------+
	| ``0b010``   |                      |
	+-------------+                      +
	| ``0b011``   |   Reserved Groups    |
	+-------------+                      +
	| ``0b100``   |                      |
	+-------------+----------------------+
	| ``0b101``   | Twelve-byte Commands |
	+-------------+----------------------+
	| ``0b110``   |                      |
	+-------------+    Vendor Specific   +
	| ``0b111``   |                      |
	+-------------+----------------------+

	'''

	GROUP0 = 0b000,
	'''Six-byte Commands

	+----------------------+-------+-----------------+
	|  opcode              | Type  | Command         |
	+======================+=======+=================+
	| ``0x00``             | ``o`` | Test Unit Ready |
	+----------------------+-------+-----------------+
	| ``0x01``             | ``s`` |                 |
	+----------------------+-------+-----------------+
	| ``0x02``             | ``v`` |                 |
	+----------------------+-------+-----------------+
	| ``0x03``             | ``m`` | Request Sense   |
	+----------------------+-------+-----------------+
	| ``0x04`` & ``0x05``  | ``s`` |                 |
	+----------------------+-------+-----------------+
	| ``0x06``             | ``v`` |                 |
	+----------------------+-------+-----------------+
	| ``0x07`` & ``0x08``  | ``s`` |                 |
	+----------------------+-------+-----------------+
	| ``0x09``             | ``v`` |                 |
	+----------------------+-------+-----------------+
	| ``0x0A`` & ``0x0B``  | ``s`` |                 |
	+----------------------+-------+-----------------+
	| ``0x0C`` to ``0x0E`` | ``v`` |                 |
	+----------------------+-------+-----------------+
	| ``0x0F`` to ``0x11`` | ``s`` |                 |
	+----------------------+-------+-----------------+
	| ``0x12``             | ``m`` | Inquiry         |
	+----------------------+-------+-----------------+
	| ``0x13`` to ``0x17`` | ``s`` |                 |
	+----------------------+-------+-----------------+
	| ``0x18``             | ``o`` | Copy            |
	+----------------------+-------+-----------------+
	| ``0x19`` to ``0x`B`` | ``s`` |                 |
	+----------------------+-------+-----------------+
	| ``0x1C``             |       | Recv Diagnostic |
	+----------------------+ ``o`` +-----------------+
	| ``0x1D``             |       | Send Diagnostic |
	+----------------------+-------+-----------------+
	| ``0x1E``             | ``s`` |                 |
	+----------------------+-------+-----------------+
	| ``0x1F``             | ``r`` |                 |
	+----------------------+-------+-----------------+

	'''

	GROUP1 = 0b001,
	'''Ten-byte Commands

	+----------------------+-------+-----------------+
	|  opcode              | Type  | Command         |
	+======================+=======+=================+
	| ``0x00`` to ``0x04`` | ``v`` |                 |
	+----------------------+-------+-----------------+
	| ``0x05``             | ``s`` |                 |
	+----------------------+-------+-----------------+
	| ``0x06`` & ``0x07``  | ``v`` |                 |
	+----------------------+-------+-----------------+
	| ``0x08``             | ``s`` |                 |
	+----------------------+-------+-----------------+
	| ``0x09``             | ``v`` |                 |
	+----------------------+-------+-----------------+
	| ``0x0A`` & ``0x0B``  | ``s`` |                 |
	+----------------------+-------+-----------------+
	| ``0x0C`` & ``0x0D``  | ``v`` |                 |
	+----------------------+-------+-----------------+
	| ``0x0E`` to ``0x13`` | ``s`` |                 |
	+----------------------+-------+-----------------+
	| ``0x14`` to ``0x18`` | ``r`` |                 |
	+----------------------+-------+-----------------+
	| ``0x19``             |       | Compare         |
	+----------------------+ ``o`` +-----------------+
	| ``0x1A``             |       | Copy and Verify |
	+----------------------+-------+-----------------+
	| ``0x1B`` to ``0x1F`` | ``r`` |                 |
	+----------------------+-------+-----------------+


	'''
	GROUP2 = 0b010,
	'''Reserved Group

	+----------------------+-------+-----------------+
	|  opcode              | Type  | Command         |
	+======================+=======+=================+
	| ``0x00`` to ``0x0F`` | ``r`` |                 |
	+----------------------+-------+-----------------+

	'''
	GROUP3 = 0b011,
	'''Reserved Group

	+----------------------+-------+-----------------+
	|  opcode              | Type  | Command         |
	+======================+=======+=================+
	| ``0x00`` to ``0x0F`` | ``r`` |                 |
	+----------------------+-------+-----------------+

	'''
	GROUP4 = 0b100,
	'''Reserved Group

	+----------------------+-------+-----------------+
	|  opcode              | Type  | Command         |
	+======================+=======+=================+
	| ``0x00`` to ``0x0F`` | ``r`` |                 |
	+----------------------+-------+-----------------+

	'''

	GROUP5 = 0b101,
	'''Twelve-byte Commands

	+----------------------+-------+-----------------+
	|  opcode              | Type  | Command         |
	+======================+=======+=================+
	| ``0x00`` to ``0x0F`` | ``v`` |                 |
	+----------------------+-------+-----------------+
	| ``0x10`` to ``0x1F`` | ``r`` |                 |
	+----------------------+-------+-----------------+

	'''
	GROUP6 = 0b110,
	'''Vendor Specific Commands

	+----------------------+-------+-----------------+
	|  opcode              | Type  | Command         |
	+======================+=======+=================+
	| ``0x00`` to ``0x1F`` | ``v`` |                 |
	+----------------------+-------+-----------------+

	'''
	GROUP7 = 0b111,
	'''Vendor Specific Commands

	+----------------------+-------+-----------------+
	|  opcode              | Type  | Command         |
	+======================+=======+=================+
	| ``0x00`` to ``0x1F`` | ``v`` |                 |
	+----------------------+-------+-----------------+

	'''


_KNOWN_SIZED_GROUPS = {
	GroupCode.GROUP0: 6,
	GroupCode.GROUP1: 10,
	GroupCode.GROUP5: 12,
}

class SCSICommandField(Subconstruct):
	'''SCSI Command Field

	This is a wrapper :py:class:`construct.Subconstruct` to allow for some metadata and automatic
	type deduction to be preformed based on the field name.

	By default SCSI Command fields don't have any type prefixing in their name, however
	this class allows for names with a prefix to automatically set the size and type.

	The following table lists the field name prefixes and their type information:

	+----------+-----------------------------------+
	| Prefix   | Type                              |
	+==========+===================================+
	| ``u8l``  | :py:class:`construct.Int8ul`      |
	+----------+-----------------------------------+
	| ``u16l`` | :py:class:`construct.Int16ul`     |
	+----------+-----------------------------------+
	| ``u24l`` | :py:class:`construct.Int24ul`     |
	+----------+-----------------------------------+
	| ``u32l`` | :py:class:`construct.Int32ul`     |
	+----------+-----------------------------------+
	| ``u64l`` | :py:class:`construct.Int64ul`     |
	+----------+-----------------------------------+
	| ``s8l``  | :py:class:`construct.Int8sl`      |
	+----------+-----------------------------------+
	| ``s16l`` | :py:class:`construct.Int16sl`     |
	+----------+-----------------------------------+
	| ``s24l`` | :py:class:`construct.Int24sl`     |
	+----------+-----------------------------------+
	| ``s32l`` | :py:class:`construct.Int32sl`     |
	+----------+-----------------------------------+
	| ``s64l`` | :py:class:`construct.Int64sl`     |
	+----------+-----------------------------------+
	| ``u8b``  | :py:class:`construct.Int8ub`      |
	+----------+-----------------------------------+
	| ``u16b`` | :py:class:`construct.Int16ub`     |
	+----------+-----------------------------------+
	| ``u24b`` | :py:class:`construct.Int24ub`     |
	+----------+-----------------------------------+
	| ``u32b`` | :py:class:`construct.Int32ub`     |
	+----------+-----------------------------------+
	| ``u64b`` | :py:class:`construct.Int64ub`     |
	+----------+-----------------------------------+
	| ``s8b``  | :py:class:`construct.Int8sb`      |
	+----------+-----------------------------------+
	| ``s16b`` | :py:class:`construct.Int16sb`     |
	+----------+-----------------------------------+
	| ``s24b`` | :py:class:`construct.Int24bl`     |
	+----------+-----------------------------------+
	| ``s32b`` | :py:class:`construct.Int32sb`     |
	+----------+-----------------------------------+
	| ``s64b`` | :py:class:`construct.Int64sb`     |
	+----------+-----------------------------------+
	| ``b#``   | :py:class:`construct.BitsInteger` |
	+----------+-----------------------------------+

	An example prefixed field name would be ``u8lAllocLen`` which would define an unsigned
	eight-bit unsigned little-endian integer called ``AllocLen``.

	However, if the ``length`` argument is passed, that will override the prefix
	calculated by the name if any is present.

	Parameters
	----------
	description : str
		The description of this field.

	default : Any
		The default value for this field if any.

	Keyword Arguments
	-----------------
	length : int
		The length of the field in bits.

	'''

	TYPE_PREFIXES = {
		'u8l' : Int8ul,
		'u16l': Int16ul,
		'u24l': Int24ul,
		'u32l': Int32ul,
		'u64l': Int64ul,
		's8l' : Int8sl,
		's16l': Int16sl,
		's24l': Int24sl,
		's32l': Int32sl,
		's64l': Int64sl,
		'u8b' : Int8ub,
		'u16b': Int16ub,
		'u24b': Int24ub,
		'u32b': Int32ub,
		'u64b': Int64ub,
		's8b' : Int8sb,
		's16b': Int16sb,
		's24b': Int24sb,
		's32b': Int32sb,
		's64b': Int64sb,
	}

	LENGTH_TYPES = {
		1: Int8ul,
		2: Int16ul,
		3: Int24ul,
		4: Int32ul,
		8: Int64ul,
	}

	@classmethod
	def _type_from_prefix(cls, field_name : str):
		'''Return appropriate :py:class:`construct.Subconstruct` for given name prefix.

		This method looks at the first few characters of the field name and attempts to
		return the appropriate :py:class:`construct.Subconstruct` type that can store that field.

		The mapping is simple, ``s`` denotes signed, ``u`` denotes unsigned, followed by the size
		in bits, and then an ``l`` or ``b`` to signify the endian; or ``b`` followed by the size in bits if the size is
		not one of the common sizes.

		If the ``length`` for this field is set then it overrides the prefix.

		Parameters
		----------
		field_name : str
			The field name to extract type information from.
		'''

		def _get_prefix(name : str) -> str:
			return ''.join(takewhile(lambda c: not c.isupper(), name))

		pfx = _get_prefix(field_name)

		subcon_type = cls.TYPE_PREFIXES.get(pfx, None)

		if subcon_type is None and len(pfx) >= 2:
			if pfx[0] != 'b':
				raise ValueError(f'The prefix {pfx} is invalid.')
			else:
				sz = int(pfx[1:])
				assert sz > 0, f'Invalid size {sz}'
				subcon_type = Bytewise(BitsInteger(sz))

		return subcon_type

	@classmethod
	def _type_from_size(cls, size : int):
		'''Return appropriate :py:class:`construct.Subconstruct` for given size in bits.

		If ``size`` is divisible by a whole number of bytes then an appropriately sized byte
		type is returned, otherwise a :py:class:`construct.BytesInteger` of the requested size
		is returned.

		If ``size`` is not divisible by a whole number of bytes, then a ::py:class:`construct.BitsInteger`
		of the given number of bits wrapped in a :py:class:`construct.Bytewise` is returned.

		Parameters
		----------
		size : int
			The size of the type to get in bits.

		'''
		if size % 8 == 0:
			bc = size // 8
			return Bytewise(cls.LENGTH_TYPES.get(
				bc,
				BytesInteger(bc, signed = False, swapped = True)
			))
		else:
			return BitsInteger(size)


	def __init__(self, description : str = '', default : Any = None, *, length : int = None):
		self.description = description
		self.default = default
		self.len = length

	def __rtruediv__(self, subcon_name : str):
		'''Rename subcon

		This method is overloaded to dynamically construct a :py:class:`construct.Subconstruct`
		for a SCSI command field based on either a name prefix or the specified length.

		Parameters
		----------
		subcon_name : str
			The name of the :py:class:`construct.Subconstruct`

		'''

		if self.len is not None:
			subcon_type = self._type_from_size(self.len)
		else:
			subcon_type = self._type_from_prefix(subcon_name)

		if subcon_type is None:
			raise ValueError(f'Unable to compute type for \'{subcon_name}\', specify a length or prefix name.')

		if self.default is not None:
			subcon_type = Default(subcon_type, self.default)

		return (subcon_name / subcon_type) * self.description

LUN = SCSICommandField('Logical Unit Number', default = 0, length = 3)
'''A :py:class:`SCSICommandField` convenience type for LUNs'''



class SCSICommand(Struct):
	'''SCSI Command Structure

	Creates a :py:class:`construct.Struct` for arbitrary SCSI Commands. This wraps the
	structure and gives it some useful common operations needed to consume and generate
	SCSI commands.

	This class automatically creates the opcode and control sections
	of the command and surrounds the provided ``*subcons`` with them.


	The rough layout of a SCSI command looks like this:

	+---------+---+---+---+---+---+---+---+---+
	| Byte    | 7 | 6 | 5 | 4 | 3 | 2 | 1 | 0 |
	+=========+===+===+===+===+===+===+===+===+
	| ``0``   | .. centered:: ``opcode``      |
	+---------+---+---+---+---+---+---+---+---+
	| ``n``   | .. centered:: ``data``        |
	+---------+---+---+---+---+---+---+---+---+
	| ``n+1`` | .. centered:: ``control``     |
	+---------+---+---+---+---+---+---+---+---+

	Both the ``opcode`` and ``control`` fields of the command
	are fixed size at 8 bits, but the ``data`` section may
	span multiple bytes and is command dependent.

	The size of the command represents the full size of the structure,
	where the size of the command data itself is ``sizeof(data) - 2``
	to account for the ``opcode`` and ``control`` bytes. Therefore a
	Six-byte command has four-bytes of actual command data for example.

	The layout of the ``opcode`` itself is a 'sub structure' which
	describes the group the command is in as well as the command itself.

	+-----+-----+----+---+---+---+---+---+
	|  7  |  6  |  5 | 4 | 3 | 2 | 1 | 0 |
	+=====+=====+====+===+===+===+===+===+
	| ``group code`` | ``command code``  |
	+-----+-----+----+---+---+---+---+---+

	The ``group code`` (:py:class:`GroupCode`) is the top three bits of the opcode, followed by the
	``command code`` which is the remaining seven bits.

	Due to the split between ``group code`` and ``command code`` as well as the different classes that implement
	commans, there is a large re-use of ``opcode``'s, this complicates things, as we need to know ahead of time what
	the device is in order to succesfully dispatch and parse commands.

	The ``control`` byte also has it's own 'sub structure'.

	+------+-----+---+---+---+---+----------+----------+
	|  7   |  6  | 5 | 4 | 3 | 2 |     1    |    0     |
	+======+=====+===+===+===+===+==========+==========+
	| ``vendor`` | ``reserved``  | ``flag`` | ``link`` |
	+------+-----+---+---+---+---+----------+----------+

	The ``vendor`` field makes up the top two bits of the control byte, and is vendor unique.

	The ``reserved`` field follows and is made up of the next four bits.

	The ``flag`` bit can only be set if the ``link`` bit is set. If ``link`` is
	set and the command completes successfully then the target sends a ``LINKED COMMAND COMPLETE``
	message if ``flag`` is zero and a ``LINKED COMMAND COMPLETE WITH FLAG`` message if ``flag`` is set.
	This behavior is commonly used to trigger an interrupt in the initiator.

	The ``link`` bit represents an automatic link to the next command is requested by the initiator if the command
	is successful. Implementation of this is optional, and depending on if it is supported or not, one of the following
	two behaviors is expected if the ``link`` flag is set.

	 * If supported, when a command completes successfully. The target will return
	   a ``INTERMEDIATE`` status and then send a message depending on the state of ``flag``.
	 * If unsupported, the target will return a ``CHECK CONDITION`` status and depending if
	   extended sense is implemented, it will set the sense key to ``ILLEGAL REQUEST`` if either
	   ``flag`` or ``link`` are set.


	Examples
	--------

	You can define a new :py:class:`SCSICommand` like any other construct structure.

	.. code-block:: python

		Command = SCSICommand(
			# Final command opcode is calculated by ``opcode | group_code``
			# And then prefixed prior to the given fields
			0x01,             # Command Opcode
			GroupCode.GROUP0, # Command Group
			'Foo' / construct.Int8ul,
			'Bar' / construct.BitStruct(
				'Nya', construct.BitsInteger(3),
				'UwU', construct.BitsInteger(5)
			)
			# The SCSI 'control' byte is then added after.
		)

	You can also use the special :py:class:`SCSICommandField` class to simply attach defaults, descriptions, and automatically
	compute sizes.

	.. code-block:: python

		Command = SCSICommand(
			0x01,
			GroupCode.GROUP0,
			'Foo' / SCSICommandField('This is a field', default = 0, length = 3),
			'Bar' / SCSICommandField('This is also a field', length = 5)
		)

	Parameters
	----------
	opcode : int
		The operation code (opcode) for the given command.

	group_code : GroupCode
		The specific SCSI group code for this command.

	size : None, int
		The size of the command, if not provided, this is inferred from the ``group_code`` if possible.

	*subcons : list[construct.Subconstruct]
		The collection of `construct <https://construct.readthedocs.io/en/latest/index.html>`_ :py:class:`construct.Subconstruct`
		members representing the command.

	Attributes
	----------

	group_code : GroupCode
		The SCSI commands group code.

	size : int
		The total size of the SCSI command.

	Note
	----

	The result of the ``sizeof()`` call returns the size of the SCSI command in bits. To get
	the size in bytes either call the ``len()`` method or divide the result of the ``sizeof()``
	call by ``8``.

	''' # noqa: E101

	opcode_layout = 'opcode' / BitStruct(
		'group'   / BitsInteger(3),
		'command' / BitsInteger(5)
	)

	control_layout = 'control' / Default(
		BitStruct(
			'vendor'   / BitsInteger(2),
			'reserved' / BitsInteger(4),
			'flag'     / BitsInteger(1),
			'link'     / BitsInteger(1),
		),
		{'vendor': 0, 'reserved': 0, 'flag': 0, 'link': 0}
	)

	def __init__(self, opcode : int, group_code : GroupCode, *subcons, size : int = None, **subconskw):
		self.opcode = opcode
		self.group_code = group_code
		if group_code not in _KNOWN_SIZED_GROUPS:
			if size is None:
				raise ValueError(f'Group {group_code}\'s size is not known, and size was not specified!')

			self.command_size = size
		else:
			self.command_size = _KNOWN_SIZED_GROUPS[group_code]

		super().__init__(*(
			'opcode' / Bytewise(Const({'command': self.opcode, 'group': self.group_code}, self.opcode_layout)),
			*subcons,
			'control' / Bytewise(self.control_layout)
		), **subconskw)

		# if (self.sizeof() // 8) != self.command_size:
		# 	raise RuntimeError(f'Structure is actually {self.sizeof() // 8} bytes long but must be {self.command_size} bytes long.')

	def len(self):
		'''Return strcutrue length in bytes'''

		return self.sizeof() // 8

	def parse(self, data, **ctxkw):

		res = super().parse(bytes(data), **ctxkw)

		res._format = self

		return res

class SCSICommand6(SCSICommand):
	'''Six-byte SCSI Command

	This is a specialization of the :py:class:`SCSICommand` class that deals with
	six-byte SCSI commands. It automatically sets the group code to Group 0.

	The rough layout of the six-byte SCSI commands are the ``opcode`` followed by
	four ``data`` bytes, and then the ``control`` byte.

	+-------+---+---+---+---+---+---+---+---+
	| Byte  | 7 | 6 | 5 | 4 | 3 | 2 | 1 | 0 |
	+=======+===+===+===+===+===+===+===+===+
	| ``0`` | .. centered:: ``opcode``      |
	+-------+---+---+---+---+---+---+---+---+
	| ``1`` |                               |
	+-------+                               +
	| ``2`` |                               |
	+-------+ .. centered:: ``data``        +
	| ``3`` |                               |
	+-------+                               +
	| ``4`` |                               |
	+-------+---+---+---+---+---+---+---+---+
	| ``5`` | .. centered:: ``control``     |
	+-------+---+---+---+---+---+---+---+---+

	Parameters
	----------
	opcode : int
		The operation code (opcode) for the given command.

	*subcons : list[construct.Subconstruct]
		The collection of `construct <https://construct.readthedocs.io/en/latest/index.html>`_ :py:class:`construct.Subconstruct`
		members representing the command.

	Attributes
	----------

	group_code : GroupCode
		The SCSI commands group code.

	size : int
		The total size of the SCSI command.

	Note
	----

	The result of the ``sizeof()`` call returns the size of the SCSI command in bits. To get
	the size in bytes either call the ``len()`` method or divide the result of the ``sizeof()``
	call by ``8``.

	'''

	def __init__(self, opcode : int, *subcons, **subconmskw):
		super().__init__(opcode, GroupCode.GROUP0, *subcons, **subconmskw)

class SCSICommand10(SCSICommand):
	'''Ten-byte SCSI Command

	This is a specialization of the :py:class:`SCSICommand` class that deals with
	ten-byte SCSI commands. It automatically sets the group code to Group 1.

	The rough layout of the ten-byte SCSI commands are the ``opcode`` followed by
	eight ``data`` bytes, and then the ``control`` byte.

	+-------+---+---+---+---+---+---+---+---+
	| Byte  | 7 | 6 | 5 | 4 | 3 | 2 | 1 | 0 |
	+=======+===+===+===+===+===+===+===+===+
	| ``0`` | .. centered:: ``opcode``      |
	+-------+---+---+---+---+---+---+---+---+
	| ``1`` |                               |
	+-------+                               +
	| ``2`` |                               |
	+-------+                               +
	| ``3`` |                               |
	+-------+                               +
	| ``4`` |                               |
	+-------+ .. centered:: ``data``        +
	| ``5`` |                               |
	+-------+                               +
	| ``6`` |                               |
	+-------+                               +
	| ``7`` |                               |
	+-------+                               +
	| ``8`` |                               |
	+-------+---+---+---+---+---+---+---+---+
	| ``9`` | .. centered:: ``control``     |
	+-------+---+---+---+---+---+---+---+---+

	Parameters
	----------
	opcode : int
		The operation code (opcode) for the given command.

	*subcons : list[construct.Subconstruct]
		The collection of `construct <https://construct.readthedocs.io/en/latest/index.html>`_ :py:class:`construct.Subconstruct`
		members representing the command.

	Attributes
	----------

	group_code : GroupCode
		The SCSI commands group code.

	size : int
		The total size of the SCSI command.

	Note
	----

	The result of the ``sizeof()`` call returns the size of the SCSI command in bits. To get
	the size in bytes either call the ``len()`` method or divide the result of the ``sizeof()``
	call by ``8``.

	'''

	def __init__(self, opcode : int, *subcons, **subconmskw):
		super().__init__(opcode, GroupCode.GROUP1, *subcons, **subconmskw)

class SCSICommand12(SCSICommand):
	'''Twelve-byte SCSI Command

	This is a specialization of the :py:class:`SCSICommand` class that deals with
	twelve-byte SCSI commands. It automatically sets the group code to Group 5.

	The rough layout of the ten-byte SCSI commands are the ``opcode`` followed by
	ten ``data`` bytes, and then the ``control`` byte.

	+-------+---+---+---+---+---+---+---+---+
	| Byte  | 7 | 6 | 5 | 4 | 3 | 2 | 1 | 0 |
	+=======+===+===+===+===+===+===+===+===+
	| ``0`` | .. centered:: ``opcode``      |
	+-------+---+---+---+---+---+---+---+---+
	| ``1`` |                               |
	+-------+                               +
	| ``2`` |                               |
	+-------+                               +
	| ``3`` |                               |
	+-------+                               +
	| ``4`` |                               |
	+-------+ .. centered:: ``data``        +
	| ``5`` |                               |
	+-------+                               +
	| ``6`` |                               |
	+-------+                               +
	| ``7`` |                               |
	+-------+                               +
	| ``8`` |                               |
	+-------+                               +
	| ``9`` |                               |
	+-------+                               +
	| ``A`` |                               |
	+-------+---+---+---+---+---+---+---+---+
	| ``B`` | .. centered:: ``control``     |
	+-------+---+---+---+---+---+---+---+---+

	Parameters
	----------
	opcode : int
		The operation code (opcode) for the given command.

	*subcons : list[construct.Subconstruct]
		The collection of `construct <https://construct.readthedocs.io/en/latest/index.html>`_ :py:class:`construct.Subconstruct`
		members representing the command.

	Attributes
	----------

	group_code : GroupCode
		The SCSI commands group code.

	size : int
		The total size of the SCSI command.

	Note
	----

	The result of the ``sizeof()`` call returns the size of the SCSI command in bits. To get
	the size in bytes either call the ``len()`` method or divide the result of the ``sizeof()``
	call by ``8``.

	'''
	def __init__(self, opcode : int, *subcons, **subconmskw):
		super().__init__(opcode, GroupCode.GROUP5, *subcons, **subconmskw)

class CommandEmitter:
	'''Creates an emitter based on the specified SCSI command.

	Given a SCSI command like the following:

	.. code-block:: python

		Command = SCSICommand6(0x00,
			'Foo' / SCSICommandField(default = 0, length = 8),
			'Bar' / SCSICommandField(length = 8)
		)

	You are then able to construct an emitter and use it like so:

	.. code-block:: python

		e = CommandEmitter(Command)
		e.Bar = 0xab

		# b\'\\x00\\xab\'
		data = e.emit()

	It is also possible to use it within a context like the following:

	.. code-block:: python

		with CommandEmitter(Command) as cmd:
			cmd.Bar = 0x15

		# b\'\\x00\\x15\'
		cmd.emit()

	Parameters
	----------
	command : SCSICommand
		The :py:class:`SCSICommand` to wrap.

	'''

	def __init__(self, command : SCSICommand):
		self.__dict__['format'] = command
		self.__dict__['fields'] = {}

	def __enter__(self):
		return self

	def __exit__(self, t, v, tb):
		if not (t is None and v is None and tb is None):
			return

	def __setattr__(self, name : str, value : Any) -> None:
		'''Set value of an attribute by name

		Parameters
		----------
		name : str
			The name of the attribute to set.

		value : Any
			The value of the attribute to set.

		Raises
		------
		AttributeError
			If the attribute being set is not in the command or reserved.
		'''

		if name == 'Reserved':
			raise AttributeError('Setting reserved fields is forbidden')

		if name[0] == '_':
			super().__setattr__(name, value)
			return

		if not any(filter(lambda f: f.name == name, self.format.subcons)):
			raise AttributeError(f'command contains no field called \'{name}\'')

		self.fields[name] = value

	def __getattr__(self, name : str) -> Any:
		'''Get value of an attribute by name

		Parameters
		----------
		name : str
			The name of the attribute to get.

		Returns
		-------
		Any
			The value of the attribute if set.

		Raises
		------
		AttributeError
			If the attribute being set is unknown.

		'''

		if name in self.fields:
			return self.fields[name]
		else:
			raise AttributeError(f'Unknown property \'{name}\'')

	def emit(self) -> bytes:
		'''Emit bytes

		Takes the assigned fields and generates a byte string from the specified format.

		Warning
		-------
		This method wraps the internal :py:class:`construct.Subconstruct` in a :py:func:`construct.Bitwise`
		to serialize the structure to bytes.

		Returns
		-------
		bytes
			The byte string of the serialized command.

		Raises
		------
		KeyError
			If missing a required field for the command.

		'''

		try:
			return Bitwise(self.format).build(self.fields)
		except KeyError as e:
			raise KeyError(f'Missing required field {e}')
