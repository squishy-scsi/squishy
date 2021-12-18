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
	python_requires = '~=3.8',
	zip_safe        = False,

	setup_requires  = [
		'wheel',
		'setuptools',
		'setuptools_scm'
	],

	install_requires = [
		'Jinja2',
		'construct>=2.10.67',
		'pyusb>=1.2.1',
		'tqdm>=4.62.3',
		'prompt_toolkit>=3.0.20',

		'amaranth @ git+https://github.com/amaranth-lang/amaranth.git@main',
		'amaranth-boards @ git+https://github.com/amaranth-lang/amaranth-boards.git@main',
		'amaranth-stdio @ git+https://github.com/amaranth-lang/amaranth-stdio.git@main',
		'luna @ git+https://github.com/shrine-maiden-heavy-industries/luna.git@amaranth#egg=luna-0.1.0.dev0',
	],

	packages = find_packages(),
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
		'squishy.gui.resources.ui': [
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
			'amaranth-yosys',
			'yowasp-yosys',
			'yowasp-nextpnr-ice40-8k',
		],

		'firmware': [
			'meson',
		],

		'gui': [
			'PySide2==5.15.2',
		]
	},

	entry_points = {
		'console_scripts': [
			'squishy = squishy:main',
		],
		'gui_scripts': [
			'squishy-gui = squishy:main_gui [gui]',
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
