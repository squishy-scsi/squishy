# SPDX-License-Identifier: BSD-3-Clause

from platformdirs import user_data_path, user_config_path, user_cache_path

SQUISHY_NAME = 'squishy'

# Squishy-specific sub dirs
SQUISHY_CACHE   = user_cache_path(SQUISHY_NAME,  False)
SQUISHY_DATA    = user_data_path(SQUISHY_NAME,   False)
SQUISHY_CONFIG  = user_config_path(SQUISHY_NAME, False)


SQUISHY_APPLETS      = (SQUISHY_DATA  / 'applets')
SQUISHY_APPLET_CACHE = (SQUISHY_CACHE / 'applets')

SQUISHY_BUILD_DIR    = (SQUISHY_CACHE / 'build')

# File path constants

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
