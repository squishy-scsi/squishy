# SPDX-License-Identifier: BSD-3-Clause

from .scsi1 import Device as SCSI1Device
from .scsi2 import Device as SCSI2Device
from .scsi3 import Device as SCSI3Device

__all__ = (
	'SCSI1Device',
	'SCSI2Device',
	'SCSI3Device',
)

__doc__ = '''\

This submodule provides wrapper methods to instantiate SCSI Device elaboratables
for :py:mod:`.scsi1`, :py:mod:`.scsi2`, and :py:mod:`.scsi3`. For more details
on the differences between them and the inner workings, see the documentation for
each particular SCSI version in its module.

'''
