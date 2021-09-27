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
		'wheel', 'setuptools', 'setuptools_scm'
	],
	install_requires = [
		'git+https://github.com/nmigen/nmigen.git@master',
		'git+https://github.com/nmigen/nmigen-boards.git@master',
		'git+https://github.com/nmigen/nmigen-stdio.git@master',
		'git+https://github.com/lethalbit/luna.git@master',
		'Jinja2',
		'construct',
		'pyusb',
		'tqdm',
	],
	packages = find_packages(
		exclude = [
			'tests*'
		]
	),

	entry_points = {
		'console_scripts': [
			'squishy = squishy:main',
		]
	},

	project_urls = {
		'Documentation': 'https://lethalbit.github.io/squishy/',
		'Source Code'  : 'https://github.com/lethalbit/squishy',
		'Bug Tracker'  : 'https://github.com/lethalbit/squishy/issues',
	}
)