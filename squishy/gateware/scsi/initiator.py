# SPDX-License-Identifier: BSD-3-Clause

from .scsi1 import Initiator as SCSI1Initiator
from .scsi2 import Initiator as SCSI2Initiator
from .scsi3 import Initiator as SCSI3Initiator

__all__ = (
	'SCSI1Initiator',
	'SCSI2Initiator',
	'SCSI3Initiator',
)

__doc__ = '''\

This submodule provides wrapper methods to instantiate SCSI Initiator elaboratables
for :py:mod:`.scsi1`, :py:mod:`.scsi2`, and :py:mod:`.scsi3`. For more details
on the differences between them and the inner workings, see the documentation for
each particular SCSI version in its module.

'''
