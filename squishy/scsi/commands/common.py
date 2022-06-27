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

'''

RequestSense = SCSICommand6(0x03,
	'LUN'      / SCSICommandField('Logical Unit Number', default = 0, length = 3),
	'Reserved' / SCSICommandField(default = 0, length = 21),
	'AllocLen' / SCSICommandField('Receive buffer size allocation', length = 8)
)
'''Request Sense

.. todo:: Document this, it's long ;~;

'''

Inquiry = SCSICommand6(0x12,
	'LUN'      / SCSICommandField('Logical Unit Number', default = 0, length = 3),
	'Reserved' / SCSICommandField(default = 0, length = 21),
	'AllocLen' / SCSICommandField('Receive buffer size allocation', length = 8)
)
'''Inquiry


'''

Copy = SCSICommand6(0x18,
	'LUN'      / SCSICommandField('Logical Unit Number', default = 0, length = 3),
	'Reserved' / SCSICommandField(default = 0, length = 5),
	'ParamLen' / SCSICommandField('Length of the parameter list in bytes', length = 24)
)
'''Copy

.. todo:: Document this

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
