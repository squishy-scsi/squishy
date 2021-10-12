# SPDX-License-Identifier: BSD-3-Clause

from os import path, environ

SQUISHY_NAME = 'squishy'

# XDG directories
XDG_CACHE_DIR   = path.join(path.expanduser('~'), '.cache') if 'XDG_CACHE_HOME' not in environ else environ['XDG_CACHE_HOME']
XDG_DATA_HOME   = path.join(path.expanduser('~'), '.local/share') if 'XDG_DATA_HOME' not in environ else environ['XDG_DATA_HOME']
XDG_CONFIG_HOME = path.join(path.expanduser('~'), '.config') if 'XDG_CONFIG_HOME' not in environ else environ['XDG_CONFIG_HOME']

# Squishy-specific sub dirs
SQUISHY_CACHE   = path.join(XDG_CACHE_DIR, SQUISHY_NAME)
SQUISHY_DATA    = path.join(XDG_DATA_HOME, SQUISHY_NAME)
SQUISHY_CONFIG  = path.join(XDG_CONFIG_HOME, SQUISHY_NAME)

SQUISHY_APPLETS = path.join(SQUISHY_DATA, 'applets')

# File path constants
SQUISHY_SETTINGS_FILE = path.join(SQUISHY_CONFIG, 'settings.json')



# Defaults
DEFAULT_SETTINGS = {
	'gui': {
		'appearance': {
			'theme'          : 'system',
			'language'       : 'en_US',
			'font': {
				'name': 'Noto Sans',
				'size': 12,
			},

			'toolbar_style': 'icon_only',

			'hex_view': {
				'byte_format': 'hex',
				'font': {
					'name': 'Fira Code',
					'size': 12
				},

				'color_map': {
					'zero'     : '#494A50',
					'low'      : '#00994D',
					'high'     : '#CD427E',
					'ones'     : '#6C2DBE',
					'printable': '#FFB45B',
				}
			}
		},
		'hotkeys': {

		},
	},
	'capture': {

	},
	'device': {

	},

}
