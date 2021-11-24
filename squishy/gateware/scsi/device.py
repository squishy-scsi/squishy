# SPDX-License-Identifier: BSD-3-Clause

from .scsi1 import Device as SCSI1Device
from .scsi2 import Device as SCSI2Device
from .scsi3 import Device as SCSI3Device

__all__ = (
	'SCSI1Device',
	'SCSI2Device',
	'SCSI3Device',
)
