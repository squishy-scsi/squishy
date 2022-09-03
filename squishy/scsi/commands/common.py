# SPDX-License-Identifier: BSD-3-Clause

from ..command import (
	SCSICommand6, SCSICommand10,
	SCSICommandField
)

__doc__ = '''
This module contains common commands, that other device classes
can support.
'''

__all__ = (
	'TestUnitReady',
	'RequestSense',
	'Inquiry',
	'Copy',
	'ReceiveDiagnosticResults',
	'SendDiagnostic',
	'Compare',
	'CopyAndVerify',
)

TestUnitReady = SCSICommand6(0x00,
	'LUN'      / SCSICommandField('Logical Unit Number', default = 0, length = 3),
	'Reserved' / SCSICommandField(default = 0, length = 29),
)
'''Test Unit Ready

This command provides the means to check if the logical
unit is ready.

It does not trigger an internal self test on the target.

If the logical unit would accept an appropriate medium-access command
without returning a ``CHECK CONDITION`` status this command shall
return a ``GOOD`` status.

'''

RequestSense = SCSICommand6(0x03,
	'LUN'      / SCSICommandField('Logical Unit Number', default = 0, length = 3),
	'Reserved' / SCSICommandField(default = 0, length = 21),
	'AllocLen' / SCSICommandField('Receive buffer size allocation', length = 8)
)
'''Request Sense

This command requests that the target transfers :ref:`sense data` to the initiator.

The sense data shall be valid for a ``CHECK CONDITION`` status returned on the prior
command. It will also be preserved by the target for the initiator until it is retrieved
by the ``REQUEST SENSE`` command, or until the receipt of any other command for the same LUN
from the initiator that issues the command resulting in the ``CHECK CONDITION`` status.

Sense data shall be cleared upon receipt of any subsequent command to the LUN from the initiator
receiving the ``CHECK CONDITION`` status. In the case of a single initiator the target must assume
that the ``REQUEST SENSES`` command is from the same initiator.


The ``AllocLen`` field specifies the number of bytes that the initiator has allocated for the returned
sense data. An allocation length of zero indicates that four bytes of sense data will be transferred. Any
other value indicates the maximum number of bytes to be transferred. The target must terminate the :ref:`DATA IN`
phase when ``AllocLen`` bytes  have been sent to the initiator or when all sense data has been exhausted, whichever
is less.

The ``REQUEST SENSE`` command shall return the ``CHECK CONDITION`` status only to report fatal errors for the command.
for example:

1. The target receives a non-zero reserved bit in the command descriptor block.
2. An unrecovered parity error occurs on the data bus.
3. A target malfunction prevents the return of sense data.

If any non-fatal error occurs during the execution of the ``REQUEST SENSE`` command
then the target shall return the sense data with a ``GOOD`` status. On fatal errors sense
data may be invalid.

A target may implement the non-extended, the extended, or both sense data formats.


.. note::

	Targets that implement both sense data formats may select the non-extended
	sense data format in response to an allocation length of zero, other methods
	of selection are also feasible.


The format of the sense data is determined by the error class. Error classes
``0`` through ``6`` use the non-extended sense data, error class ``7`` uses the extended sense
data.

The non-extended sense data is depicted below:

+---------+-----------+----+----+---+---+---+---+---+
| .. centered:: Non-extended Sense Data             |
+---------+-----------+----+----+---+---+---+---+---+
| Byte    | 7         | 6  | 5  | 4 | 3 | 2 | 1 | 0 |
+=========+===========+====+====+===+===+===+===+===+
| ``0``   | AddrValid | Error Class | Error Code    |
+---------+-----------+----+----+---+---+---+---+---+
| ``1``   |   Vendor Unique     | LBA (MSB)         |
+---------+-----------+----+----+---+---+---+---+---+
| ``2``   | LBA                                     |
+---------+-----------+----+----+---+---+---+---+---+
| ``3``   | LBA (LSB)                               |
+---------+-----------+----+----+---+---+---+---+---+

The ``AddrValid`` flag indicates that the LBA field contains valid information related
to the error code.

The error class specified the class of errors, classes ``0`` through ``6`` are all vender unique,
the error code for the class is also vendor unique.



For extended sense data, the error class is fixed to ``7``, but extended sense data will only be
returned if the error code is ``0``. Error code ``15`` specifies a vendor unique data format for the
extended sense data. Error codes ``1`` tough ``14`` are reserved.

The extended sense data format is depicted below:

+---------+-----------+----+----+-----+---+---+---+---+
| .. centered:: Extended Sense Data                   |
+---------+-----------+----+----+-----+---+---+---+---+
| Byte    | 7         | 6  | 5  |  4  | 3 | 2 | 1 | 0 |
+=========+===========+====+====+=====+===+===+===+===+
| ``0``   | Valid     |  1 | 1  |  1  | 0 | 0 | 0 | 0 |
+---------+-----------+----+----+-----+---+---+---+---+
| ``1``   | Segment Number                            |
+---------+-----------+----+----+-----+---+---+---+---+
| ``2``   | File Mark | EOM| ILI| Res |  Sense Key    |
+---------+-----------+----+----+-----+---+---+---+---+
| ``3``   | Information Byte                          |
+---------+-----------+----+----+-----+---+---+---+---+
| ``4``   | Information Byte                          |
+---------+-----------+----+----+-----+---+---+---+---+
| ``5``   | Information Byte                          |
+---------+-----------+----+----+-----+---+---+---+---+
| ``6``   | Information Byte (LSB)                    |
+---------+-----------+----+----+-----+---+---+---+---+
| ``7``   | Additional Sense Length (``n``)           |
+---------+-----------+----+----+-----+---+---+---+---+
| ``8``   | Additional Sense Bytes                    |
+         +                                           +
|   to    |                                           |
+         +                                           +
| ``n+7`` |                                           |
+---------+-----------+----+----+-----+---+---+---+---+

If ``Valid`` is not set, then the data in ``Information Byte`` is undefined, otherwise it
is defined as follows:

1. The unsigned LBA associated with the sense key, for type 0, type 4 and type 5 devices.
2. The difference of the requested length minus the actual length in bytes or blocks. As determined by the
   command, for type 1, type 2, and type 3 devices.
3. The difference of the requested number of blocks minus the actual number of blocks copied or compared
   for the current segment descriptor of a :py:data:`Copy`, :py:data:`Compare`, or :py:data:`CopyAndVerify`
   command.

The ``Segment Number`` field contains the number of the current segment descriptor if the extended sens is
in response to a :py:data:`Copy`, :py:data:`Compare`, or :py:data:`CopyAndVerify` command. Up to ``256`` segments
are supported.

The ``File Mark`` flag indicates that the current command has read a file mark, and is only used on sequential-access
devices.

The ``EOM`` or End of Medium flag indicates that an end-of-medium condition (EOT, BOT, Out of paper, etc) exists on
a sequential access or printer device. For sequential access devices, this flag indicates that the unit is at or past
the early-warning EOT if the direction was forward or that the command could not be completed due to a BOT being
encountered if the direction was reverse. Direct access devices must not use this flag, instead they must report
attempts to access beyond EOM as an ``ILLEGAL REQUEST`` sense key.

The ``ILI`` or Incorrect Length Indicator flag indicates that the requested logical block length did not match the
logical block length of the data on the medium.

The value of the ``Sense Key`` field is described as follows:

.. todo:: Move this to an enum in command.py

+-----------+---------------------------------------------------+
| Sense Key | Description                                       |
+===========+===================================================+
| ``0x0``   | **No Sense**. Indicates that there is no specific |
+           + sense key information to be reported for the      +
|           | designated logical unit. This would be the case   |
+           + for a successful command or a command that        +
|           | received a ``CHECK CONDITION`` status due to one  |
+           + of the ``File Mark``, ``EOM``, or ``ILI`` flags   +
|           | being set.                                        |
+-----------+---------------------------------------------------+
| ``0x1``   | **Recovered Error**. Indicates that the last      |
+           + command completed successfully with some recovery +
|           | action performed by the target. Details may be    |
+           + determined by examining the additional sense      +
|           | bytes and information bytes.                      |
+-----------+---------------------------------------------------+
| ``0x2``   | **Not Ready**. Indicates that the logical unit    |
+           + addressed cannot be accessed. Operator            +
|           | intervention may be required to correct this.     |
+-----------+---------------------------------------------------+
| ``0x3``   | **Medium Error**. Indicates that the command      |
+           + terminated with a non-recovered error condition   +
|           | that was likely caused by a flaw in the medium.   |
+-----------+---------------------------------------------------+
| ``0x4``   | **Hardware Error**. Indicates that the target     |
+           + detected a non-recoverable hardware failure while +
|           | performing the command or during a self-test.     |
+-----------+---------------------------------------------------+
| ``0x5``   | **Illegal Request**. Indicates that there was an  |
+           + illegal parameter in the command descriptor block +
|           | or in the additional parameters supplied as data  |
+           + for some commands. If the target detects an       +
|           | invalid parameter in the command descriptor block |
+           + then it must terminate the command without        +
|           | altering the medium. If the target detects an     |
+           + invalid parameter in the additional parameters    +
|           | supplied as data, then it may alter the medium    |
+-----------+---------------------------------------------------+
| ``0x6``   | **Unit Attention**. Indicates that the removable  |
+           + medium may have been changed or the target has    +
|           | been reset.                                       |
+-----------+---------------------------------------------------+
| ``0x7``   | **Data Protect**. Indicates that a command that   |
+           + reads or writes the medium was attempted on a     +
|           | block that is protected, and the op was not done. |
+-----------+---------------------------------------------------+
| ``0x8``   | **Blank Check**. Indicates that a WORM device or  |
+           + a sequential-access device encountered a blank    +
|           | block while reading, or a WORM device encountered |
+           + a non-blank block while writing.                  +
|           |                                                   |
+-----------+---------------------------------------------------+
| ``0x9``   | **Vendor Unique**. This sense key is available    |
+           + for reporting vendor unique conditions.           +
|           |                                                   |
+-----------+---------------------------------------------------+
| ``0xA``   | **Copy Aborted**. Indicates a :py:data:`Copy`,    |
+           + :py:data:`Compare`, or :py:data:`CopyAndVerify`   +
|           | command was aborted due to an error condition on  |
+           + the source device, destination device, or both.   +
|           |                                                   |
+-----------+---------------------------------------------------+
| ``0xB``   | **Aborted Command**. Indicates that the target    |
+           + aborted the command. The initiator may be able to +
|           | recover by trying the command again.              |
+-----------+---------------------------------------------------+
| ``0xC``   | **Equal**. Indicates tha a :py:data:`SearchData`  |
+           + command has satisfied an equal comparison.        +
|           |                                                   |
+-----------+---------------------------------------------------+
| ``0xD``   | **Volume Overflow**. Indicates that a buffered    |
+           + peripheral device has reached the end-of-medium   +
|           | and data remains in the buffer that has not been  |
+           + written to the medium. A                          +
|           | :py:data:`RecoverBufferedData` command(s) may be  |
+           + issued to read the unwritten data from the buffer +
|           |                                                   |
+-----------+---------------------------------------------------+
| ``0xE``   | **Miscompare**. Indicates that the source data    |
+           + did not match teh data read from the medium.      +
|           |                                                   |
+-----------+---------------------------------------------------+
| ``0xF``   | .. centered:: **Reserved**                        |
+-----------+---------------------------------------------------+


The ``Additional Sense Length`` specifies how many additional bytes of sense data are to follow. If the allocation length
of the command descriptor block is too small to transfer all of the additional data, the ``Additional Sense Length`` is **NOT**
adjusted to reflect the truncation.

The ``Additional Sense Bytes`` contains data that is command-specific, peripheral-device-specific, or both the further
define the nature of the ``CHECK CONDITION`` status. The :py:data:`Copy`, :py:data:`Compare`, :py:data:`CopyAndVerify`,
and :py:data:`SearchData` commands define a standard purpose for some of the bytes. Unless described in said commands,
all additional sense bytes are vendor unique.

''' # noqa: E101

Inquiry = SCSICommand6(0x12,
	'LUN'      / SCSICommandField('Logical Unit Number', default = 0, length = 3),
	'Reserved' / SCSICommandField(default = 0, length = 21),
	'AllocLen' / SCSICommandField('Receive buffer size allocation', length = 8)
)
'''Inquiry

This command requests that information regarding parameters of the target and its attached peripheral devices
be sent to the initiator.

The ``AllocLen`` field specifies the number of bytes that the initiator has allocated for the returned ``INQUIRY`` data.
An ``AllocLen`` of zero indicates that no ``INQUIRY`` data shall be transferred to the Initiator, and shall not be
considered an error. Any other value indicates the maximum number of bytes that shall be transferred. The target must
terminate the ``DATA IN`` phase when ``AllocLen`` bytes have been transferred or when all available ``INQUIRY`` data
as been exhausted, which ever is less.

The ``INQUIRY`` command must return a ``CHECK CONDITION`` status only when the target can not return the requested
``INQUIRY`` data.

.. note::

	It is recommended that the ``INQUIRY`` data be returned even though the peripheral device may not
	be ready for other commands.

If an ``INQUIRY`` command is received from an initiator with a pending unit attention condition, the
target shall perform the ``INQUIRY`` command and shall not clear the unit attention condition.

The data returned from the ``INQUIRY`` command is described below:

+---------+-----------+----+----+-----+---+---+---+---+
| .. centered:: ``INQUIRY`` Data                      |
+---------+-----------+----+----+-----+---+---+---+---+
| Byte    | 7         | 6  | 5  |  4  | 3 | 2 | 1 | 0 |
+=========+===========+====+====+=====+===+===+===+===+
| ``0``   | Peripheral Device Type                    |
+---------+-----------+----+----+-----+---+---+---+---+
| ``1``   | RMB       | Device-Type Qualifier         |
+---------+-----------+----+----+-----+---+---+---+---+
| ``2``   | ISO Ver        | ECMA Ver     | ANSI Ver  |
+---------+-----------+----+----+-----+---+---+---+---+
| ``3``   | Reserved                                  |
+---------+-----------+----+----+-----+---+---+---+---+
| ``4``   | Additional Length                         |
+---------+-----------+----+----+-----+---+---+---+---+
| ``5``   | Vendor Unique                             |
+ to      +                                           +
| ``n+4`` |                                           |
+---------+-----------+----+----+-----+---+---+---+---+

The ``Peripheral Device Type`` is one of the values in :py:class:`squishy.scsi.device.PeripheralDeviceType`

The ``RMB`` flag indicates that the medium is removable or not.

The ``Device-Type Qualifier`` iss a seven-bit user specified value. This value may be set with
any means on the target or peripheral device. SCSI devices that do not support this feature must
set it to all zeros *(i.e. ``0b0000000``)*. This feature allows each user to assign a unique value
to each specific type of peripheral device that is supported on the system being used. These
values may then be used by the self-configuring software to determine what specific peripheral device
is at each LUN.

The ``ISO Ver``, and ``ECMA Ver`` fields describe to which version of the respective
specifications the device compiles to. A zero value in the ``ISO Ver`` and/or ``ECMA Ver`` fields
indicates that the target does not claim compliance to ISO or ECMA Versions of SCSI.

.. note:: It is possible to claim compliance to more than one standard.

The ``ANSI Ver`` field indicates the implemented version of the ANSI SCSI standard with the following values:

+---------+-----------------------------------------+
| Value   | Description                             |
+=========+=========================================+
| ``0x0`` | Version is unspecified                  |
+---------+-----------------------------------------+
| ``0x1`` | Complies with ``X3.313:1986``           |
+---------+-----------------------------------------+
| ``0x2`` | Reserved                                |
+ to      +                                         +
| ``0x7`` |                                         |
+---------+-----------------------------------------+

The ``Additional Length`` field specifies the length in bytes of the vendor unique
parameters. If the ``AllocLen`` iss tool small to transfer all of the vendor unique
data, the additional length is **NOT** adjusted to reflect the truncation.

'''

Copy = SCSICommand6(0x18,
	'LUN'      / SCSICommandField('Logical Unit Number', default = 0, length = 3),
	'Reserved' / SCSICommandField(default = 0, length = 5),
	'ParamLen' / SCSICommandField('Length of the parameter list in bytes', length = 24)
)
'''Copy

This command provides a means to copy data from one logical unit to itself or another.
The logical units may reside on the same SCSI device or different SCSI devices.

.. note::

	Some SCSI devices that implement this command may not support copying to or from
	another SCSI device, or copies where both logical units reside on another SCSI device.

The ``ParamLen`` field specifies the length in bytes of the parameters that are to be sent
during the ``DATA OUT`` phase of the command. A ``ParamLen`` of zero indicates that no data
will be transferred, and must not be considered an error.

The ``COPY`` parameter list is structured as follows:

+---------+-----------+----+----+-----+---+---+---+---+
| .. centered:: ``COPY`` Parameter List               |
+---------+-----------+----+----+-----+---+---+---+---+
| Byte    | 7         | 6  | 5  |  4  | 3 | 2 | 1 | 0 |
+=========+===========+====+====+=====+===+===+===+===+
| ``0``   | Function Code             | Priority      |
+---------+-----------+----+----+-----+---+---+---+---+
| ``1``   | Vendor Unique                             |
+---------+-----------+----+----+-----+---+---+---+---+
| ``2``   | Reserved                                  |
+---------+-----------+----+----+-----+---+---+---+---+
| ``3``   | Reserved                                  |
+---------+-----------+----+----+-----+---+---+---+---+
| ``N``   | Segment descriptors...                    |
+---------+-----------+----+----+-----+---+---+---+---+

The ``Function Code`` field defines the specific format for the segment descriptors, they are
as follows:

The ``Priority`` field establishes the relative priority of the ``COPY`` command to other commands
being executed by the same target. All other commands are assumed to have a priority of ``1``, with
``0`` being the highest priority, the larger the value the lower the priority of the command.

The segment descriptor formats are designated by the ``Function Code``

'''

ReceiveDiagnosticResults = SCSICommand6(0x1C,
	'LUN'      / SCSICommandField('Logical Unit Number', default = 0, length = 3),
	'Reserved' / SCSICommandField(default = 0, length = 13),
	'AllocLen' / SCSICommandField('Length of the receiving buffer', length = 16)
)
'''Receive Diagnostic Results

.. todo:: Document this

'''

SendDiagnostic = SCSICommand6(0x1D,
	'LUN'      / SCSICommandField('Logical Unit Number', default = 0, length = 3),
	'Reserved' / SCSICommandField(default = 0, length = 2),
	'SelfTest' / SCSICommandField('', default = 0, length = 1),
	'DevOfL'   / SCSICommandField('', default = 0, length = 1),
	'UnitOfL'  / SCSICommandField('', default = 0, length = 1),
	'Reserved' / SCSICommandField(default = 0, length = 8),
	'ParamLen' / SCSICommandField('Length of the parameter list in bytes', length = 16)
)
'''Send Diagnostic

.. todo:: Document this

'''

Compare = SCSICommand10(0x19,
	'LUN'      / SCSICommandField('Logical Unit Number', default = 0, length = 3),
	'Reserved' / SCSICommandField(default = 0, length = 13),
	'ParamLen' / SCSICommandField('Length of the parameter list in bytes', length = 24),
	'Reserved' / SCSICommandField(default = 0, length = 24)
)
'''Compare

.. todo:: Document this

'''

CopyAndVerify = SCSICommand10(0x1A,
	'LUN'      / SCSICommandField('Logical Unit Number', default = 0, length = 3),
	'Reserved' / SCSICommandField(default = 0, length = 3),
	'BytChk'   / SCSICommandField('', default = 0, length = 1),
	'Reserved' / SCSICommandField('', default = 0, length = 1),
	'ParamLen' / SCSICommandField('Length of the parameter list in bytes', length = 24),
	'Reserved' / SCSICommandField(default = 0, length = 24)
)
'''Copy and Verify

.. todo:: Document this

'''
