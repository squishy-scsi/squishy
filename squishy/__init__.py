# SPDX-License-Identifier: BSD-3-Clause
from sys import version_info

# Bounce out if python is  too old
if version_info < (3, 11):
	raise RuntimeError('Python version 3.11 or newer is required to use Squishy')

try:
	from importlib import metadata
	__version__ = metadata.version(__package__)
except ImportError:
	__version__ = 'unknown' # :nocov:

from .core.warn import install_handler

# Hook the python warnings handler
install_handler()

__all__ = ()

'''
╭─────────────────────────────────────╮
│                                     │
│           !!! WARNING !!!           │
│                                     │
│     THIS MACHINE KNOWS NOT THE      │
│ DIFFERENCE BETWEEN METAL AND FLESH, │
│          NOR DOES IT CARE.          │
│                                     │
╰─────────────────────────────────────╯
'''
