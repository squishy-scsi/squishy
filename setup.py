#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-3-Clause

from setuptools import setup, find_packages
from pathlib    import Path

REPO_ROOT   = Path(__file__).parent
README_FILE = (REPO_ROOT / 'README.md')

def vcs_ver():
	def scheme(version):
		if version.tag and not version.distance:
			return version.format_with("")
		else:
			return version.format_choice("+{node}", "+{node}.dirty")
	return {
		"relative_to": __file__,
		"version_scheme": "guess-next-dev",
		"local_scheme": scheme
	}

def doc_ver():
	try:
		from setuptools_scm.git import parse as parse_git
	except ImportError:
		return ""

	git = parse_git(".")
	if not git:
		return ""
	elif git.exact:
		return git.format_with("{tag}")
	else:
		return "latest"

setup(
	name = 'Squishy',
	use_scm_version  = vcs_ver(),
	author           = 'Aki \'lethalbit\' Van Ness',
	author_email     = 'nya@catgirl.link',
	description      = 'SCSI Multitool and Torii HDL Library',
	license          = 'BSD-3-Clause',
	python_requires  = '~=3.9',
	zip_safe         = True,
	url              = 'https://github.com/lethalbit/squishy',

	long_description = README_FILE.read_text(),
	long_description_content_type = 'text/markdown',

	setup_requires   = [
		'wheel',
		'setuptools',
		'setuptools_scm'
	],

	install_requires  = [
		'Jinja2',
		'construct>=2.10.67',
		'arrow',
		'libusb1>=1.8.1',
		'rich~=12.6.0',
		'torii<1.0',
		'usb-construct<1.0',
		'sol-usb<1.0',
	],

	packages          = find_packages(
		where = '.'
	),
	package_data      = {
		# GUI Resources
		'squishy.gui.resources.fonts': [
			'FiraCode-Regular.ttf',
			'NotoSans-Regular.ttf',
		],
		'squishy.gui.resources.icons': [
			'computer.svg',
			'cpu.svg',
			'drive-harddisk.svg',
			'drive-multidisk.svg',
			'drive-partition.svg',
			'media-optical.svg',
			'media-tape.svg',
			'printer.svg',
		],
		'squishy.gui.resources.images': [
			'about.png',
			'splash.png',
		],
		'squishy.gui.resources.themes': [

		],
		'squishy.gui.resources.ui': [
			'about_window.ui',
			'bus_topology_window.ui',
			'devices_window.ui',
			'filters_window.ui',
			'main_window.ui',
			'preferences_window.ui',
			'triggers_window.ui',
		],
		# localization bits
		'squishy.i18n.locales.en.LC_MESSAGES': [

		]
	},

	extras_require    = {
		# yowasp-nextpnr is broken atm
		# 'toolchain': [
		# 	'yowasp-yosys',
		# 	# For rev1
		# 	'yowasp-nextpnr-ice40-8k',
		# 	# For rev2
		# 	'yowasp-nextpnr-ecp5-45k'
		# ],

		'firmware': [
			'meson',
			'ninja',
		],

		'gui': [
			'PySide2~=5.15.2',
		],
		'dev': [
			'nox',
			'setuptools_scm'
		]
	},

	entry_points       = {
		'console_scripts': [
			'squishy = squishy.main:cli_main',
		],
		'gui_scripts': [
			'squishy-gui = squishy.main:gui_main [gui]',
		]
	},

	classifiers       = [
		'Development Status :: 4 - Beta',

		'Environment :: Console',

		'Intended Audience :: Developers',
		'Intended Audience :: Information Technology',
		'Intended Audience :: System Administrators',

		'License :: OSI Approved :: BSD License',

		'Operating System :: MacOS :: MacOS X',
		'Operating System :: Microsoft :: Windows',
		'Operating System :: POSIX :: Linux',

		'Programming Language :: Python :: 3.9',
		'Programming Language :: Python :: 3.10',
		'Programming Language :: Python :: 3.11',


		'Topic :: Software Development',
		'Topic :: System :: Hardware',

	],

	project_urls      = {
		'Documentation': 'https://docs.scsi.moe/',
		'Source Code'  : 'https://github.com/lethalbit/squishy',
		'Bug Tracker'  : 'https://github.com/lethalbit/squishy/issues',
	}
)
