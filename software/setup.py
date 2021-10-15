# SPDX-License-Identifier: BSD-3-Clause

from setuptools import setup, find_packages

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
	use_scm_version = vcs_ver(),
	author          = 'Aki \'lethalbit\' Van Ness',
	author_email    = 'nya@catgirl.link',
	description     = 'SCSI Multi-tool',
	license         = 'BSD-3-Clause',
	python_requires = '>=3.6',

	setup_requires  = [
		'wheel',
		'setuptools',
		'setuptools_scm'
	],

	install_requires = [
		'git+https://github.com/nmigen/nmigen.git@master#egg=nmigen',
		'git+https://github.com/nmigen/nmigen-boards.git@master#egg=nmigen-boards',
		'git+https://github.com/nmigen/nmigen-stdio.git@master#egg=nmigen-stdio',
		'git+https://github.com/lethalbit/luna.git@master#egg=luna',

		'Jinja2',
		'construct',
		'pyusb',
		'tqdm',
		'prompt_toolkit',
	],

	packages = find_packages(
		exclude = [
			'tests*'
		]
	),
	package_data = {
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

		],
		'squishy.gui.resources.themes': [

		],
		'squishy.gui': [
			'about_window.ui',
			'bus_topology_window.ui',
			'devices_window.ui',
			'filters_window.ui',
			'main_window.ui',
			'preferences_window.ui',
			'triggers_window.ui',
		],
	},

	extras_require = {
		'toolchain': [
			'nmigen-yosys',
			'yowasp-yosys',
			'yowasp-nextpnr-ice40-8k',
		],

		'firmware': [
			'meson',
		],

		'gui': [
			'PySide2',
		]
	},

	entry_points = {
		'console_scripts': [
			'squishy = squishy:main',
		],
		'gui_scripts': [
			'squishy-gui = squishy:main_gui',
		]
	},

	classifiers = [
		'Development Status :: 3 - Alpha',
		'License :: OSI Approved :: BSD License',

		'Intended Audience :: Developers',
		'Intended Audience :: Information Technology',
		'Intended Audience :: System Administrators',

		'Topic :: Software Development',
		'Topic :: System :: Hardware',

	],

	project_urls = {
		'Documentation': 'https://lethalbit.github.io/squishy/',
		'Source Code'  : 'https://github.com/lethalbit/squishy',
		'Bug Tracker'  : 'https://github.com/lethalbit/squishy/issues',
	}
)
