# SPDX-License-Identifier: BSD-3-Clause

from pkg_resources import resource_stream, resource_string, resource_filename

from enum          import Enum, unique

__all__ = (
	'get_resource',
	'ResourceType',
	'ResourceCategory',
)

@unique
class ResourceCategory(Enum):
	FONT  = 0
	ICON  = 1
	IMAGE = 2
	THEME = 3

	def __str__(self):
		if self == ResourceCategory.FONT:
			return 'fonts'
		elif self == ResourceCategory.ICON:
			return 'icons'
		elif self == ResourceCategory.IMAGE:
			return 'images'
		elif self == ResourceCategory.THEME:
			return 'themes'
		else:
			return ''

@unique
class ResourceType(Enum):
	STREAM = resource_stream
	BYTES  = resource_string
	PATH   = resource_filename

def get_resource(name, res_category, res_type):
	return res_type(__name__, f'{res_category!s}/{name}')
