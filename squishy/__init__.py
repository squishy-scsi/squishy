# SPDX-License-Identifier: BSD-3-Clause
try:
	from importlib import metadata as importlib_metadata
	__version__ = importlib_metadata.version(__package__)
except ImportError:
	__version__ = ':nya_confused:' # :nocov:

__all__ = (

)

'''\
+=====================================+
|                                     |
|           !!! WARNING !!!           |
|                                     |
|     THIS MACHINE KNOWS NOT THE      |
| DIFFERENCE BETWEEN METAL AND FLESH, |
|          NOR DOES IT CARE.          |
|                                     |
+=====================================+
'''
