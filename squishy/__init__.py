# SPDX-License-Identifier: BSD-3-Clause

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
