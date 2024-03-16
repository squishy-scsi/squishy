# SPDX-License-Identifier: BSD-3-Clause

import platform
from pathlib import Path
from os      import environ

SQUISHY_NAME = 'squishy'

_os = platform.system()

if _os == 'Linux':
	def _get_xdg_dir(name: str, default: Path) -> Path:
		if name in environ:
			return Path(environ[name])
		return default

	HOME_DIR   = _get_xdg_dir('XDG_HOME',        Path.home()                )
	CACHE_DIR  = _get_xdg_dir('XDG_CACHE_HOME',  (HOME_DIR / '.cache')      )
	DATA_DIR   = _get_xdg_dir('XDG_DATA_HOME',   (HOME_DIR / '.local/share'))
	CONFIG_DIR = _get_xdg_dir('XDG_CONFIG_HOME', (HOME_DIR / '.config')     )

	del _get_xdg_dir
elif _os == 'Windows':
	HOME_DIR   = Path.home()
	CACHE_DIR  = (HOME_DIR / r'AppData\Local\Temp')
	DATA_DIR   = (HOME_DIR / r'AppData\Roaming'   )
	CONFIG_DIR = DATA_DIR
elif _os == 'Darwin':
	HOME_DIR   = Path.home()
	CACHE_DIR  = (HOME_DIR / 'Library/Caches'             )
	DATA_DIR   = (HOME_DIR / 'Library/Application Support')
	CONFIG_DIR = DATA_DIR
else:
	HOME_DIR   = Path.home()
	CACHE_DIR  = (HOME_DIR / '.cache'      )
	DATA_DIR   = (HOME_DIR / '.local/share')
	CONFIG_DIR = (HOME_DIR / '.config'     )

del _os

# Squishy-specific sub dirs
SQUISHY_CACHE   = (CACHE_DIR  / SQUISHY_NAME)
SQUISHY_DATA    = (DATA_DIR   / SQUISHY_NAME)
SQUISHY_CONFIG  = (CONFIG_DIR / SQUISHY_NAME)

SQUISHY_APPLETS      = (SQUISHY_DATA  / 'applets')
SQUISHY_APPLET_CACHE = (SQUISHY_CACHE / 'applets')

SQUISHY_BUILD_DIR    = (SQUISHY_CACHE / 'build')

# File path constants
SQUISHY_HISTORY_FILE  = (SQUISHY_CACHE  / '.repl-history')

# Hardware Metadata, etc
USB_VID             = 0x1209
USB_PID_BOOTLOADER  = 0xCA71
USB_PID_APPLICATION = 0xCA70
USB_MANUFACTURER    = 'Shrine Maiden Heavy Industries'
USB_PRODUCT         = {
	USB_PID_BOOTLOADER : 'Squishy Bootloader',
	USB_PID_APPLICATION: 'Squishy',
}

SCSI_VID            = 'Shrine-0'
