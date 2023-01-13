# SPDX-License-Identifier: BSD-3-Clause

from pathlib import Path
from os      import environ

SQUISHY_NAME = 'squishy'

# XDG directories
XDG_HOME        = Path.home()                 if 'XDG_HOME'        not in environ else Path(environ['XDG_HOME'])
XDG_CACHE_DIR   = (XDG_HOME / '.cache')       if 'XDG_CACHE_HOME'  not in environ else Path(environ['XDG_CACHE_HOME'])
XDG_DATA_HOME   = (XDG_HOME / '.local/share') if 'XDG_DATA_HOME'   not in environ else Path(environ['XDG_DATA_HOME'])
XDG_CONFIG_HOME = (XDG_HOME / '.config')      if 'XDG_CONFIG_HOME' not in environ else Path(environ['XDG_CONFIG_HOME'])

# Squishy-specific sub dirs
SQUISHY_CACHE   = (XDG_CACHE_DIR   / SQUISHY_NAME)
SQUISHY_DATA    = (XDG_DATA_HOME   / SQUISHY_NAME)
SQUISHY_CONFIG  = (XDG_CONFIG_HOME / SQUISHY_NAME)

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
