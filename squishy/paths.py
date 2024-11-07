# SPDX-License-Identifier: BSD-3-Clause

'''
This module is just to declare the path constants for Squishy.

These generally follows the XDG Base Directory Specification or any
other appropriate places depending on the OS thanks to platformdirs.


The following base directories are defined:

* ``SQUISHY_CACHE`` - Used for bitstream builds and any needed cached info that can be ignored in backcups
* ``SQUISHY_DATA``  - Used for user-defined or third-party external applets and any other runtime deps
* ``SQUISHY_CONFIG`` - Used for any host-side configuration and/or settings for Squishy and related

Within the ``SQUISHY_CACHE`` directory there are two sub-directories:

* ``SQUISHY_ASSET_CACHE`` - The built-gateware cache directory, see the cache mechanism for more details
* ``SQUISHY_BUILD_DIR`` - The last-built/in-progress builds for Squishy gateware/bootloader bitstreams.
* ``SQUISHY_BUILD_BOOT`` - The last-built/in-progress builds for Squishy the bootloader.
* ``SQUISHY_BUILD_APPLET`` - The last-built/in-progress builds for Squishy applet bitstreams.

Both of these can be safely deleted with no side-effects other than every applet/bootloader build hitting a
cache miss after when first ran/built.

Within ``SQUISHY_DATA`` there is one directory, that being `applets`, it is used for out-of-tree and user
defined applets.

'''

__all__ = (
	# Root directories
	'SQUISHY_CACHE',
	'SQUISHY_DATA',
	'SQUISHY_CONFIG',
	# Cache Subdirs/Files
	'SQUISHY_ASSET_CACHE',
	'SQUISHY_BUILD_DIR',
	'SQUISHY_BUILD_BOOT',
	'SQUISHY_BUILD_APPLET',
	# Data Subdirs/Files
	'SQUISHY_APPLETS',
	# Config Subdirs/Files
	'SQUISHY_SETTINGS',
	# Helpers
	'initialize_dirs',
)

from platformdirs import user_data_path, user_config_path, user_cache_path

# Squishy-specific base directories
SQUISHY_CACHE  = user_cache_path('squishy',  False)
SQUISHY_DATA   = user_data_path('squishy',   False)
SQUISHY_CONFIG = user_config_path('squishy', False)

# SQUISHY_CACHE subdirectories/files
SQUISHY_ASSET_CACHE  = (SQUISHY_CACHE / 'assets')
''' Squishy built applet gateware cache (``$SQUISHY_CACHE/assets``) '''
SQUISHY_BUILD_DIR    = (SQUISHY_CACHE / 'build')
''' Squishy build directory (``$SQUISHY_CACHE/build``) '''
SQUISHY_BUILD_BOOT   = (SQUISHY_BUILD_DIR / 'boot')
''' Squishy bootloader build directory (``$SQUISHY_BUILD_DIR/boot``) '''
SQUISHY_BUILD_APPLET = (SQUISHY_BUILD_DIR / 'applet')
''' Squishy applet build directory (``$SQUISHY_BUILD_DIR/applet``) '''

# SQUISHY_DATA subdirectories/files
SQUISHY_APPLETS      = (SQUISHY_DATA  / 'applets')
''' Squishy out-of-tree/third-party applets (``$SQUISHY_DATA/applets``) '''

# SQUISHY_CONFIG subdirectories/files
SQUISHY_SETTINGS = (SQUISHY_CONFIG / 'config.json')
''' Squishy settings file (``$SQUISHY_CONFIG/config.json``) '''

def initialize_dirs() -> None:
	'''
	Initialize Squishy application directories.
	'''
	_dirs = (
		# Root directories
		SQUISHY_CACHE,
		SQUISHY_DATA,
		SQUISHY_CONFIG,
		# Cache Subdirs
		SQUISHY_ASSET_CACHE,
		SQUISHY_BUILD_DIR,
		SQUISHY_BUILD_BOOT,
		SQUISHY_BUILD_APPLET,
		# Data Subdirs
		SQUISHY_APPLETS,
	)

	# TODO(aki): This is likely not very performant, oops
	for directory in _dirs:
		directory.mkdir(parents = True, exist_ok = True)
