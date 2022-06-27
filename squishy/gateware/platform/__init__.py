# SPDX-License-Identifier: BSD-3-Clause
from .rev1 import SquishyRev1
from .rev2 import SquishyRev2

__all__ = (
	'SquishyRev1',
	'SquishyRev2',

	'AVAILABLE_PLATFORMS',
)

__doc__ = '''\

.. todo:: Flesh this section out



''' # noqa: E101

AVAILABLE_PLATFORMS = {
	'rev1': SquishyRev1,
}
