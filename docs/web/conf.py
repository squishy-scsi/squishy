# SPDX-License-Identifier: BSD-3-Clause
import os, sys
sys.path.insert(0, os.path.abspath('.'))

try:
	import squishy
	version = squishy.__version__

except ImportError:
	version = ':nya_confused:' # :nocov:

project = 'Squishy'
release = version.split('+')[0]
copyright = '2021, Aki "lethalbit" Van Ness, et. al.'

extensions = [
	'sphinx.ext.intersphinx',
	'sphinx.ext.doctest',
	'sphinx.ext.todo',
	'sphinx.ext.githubpages',
	'sphinx.ext.graphviz',
	'sphinxcontrib.platformpicker',
	'sphinx_rtd_theme',
	'myst_parser',
]

source_suffix = {
	'.rst': 'restructuredtext',
	'.md': 'markdown',
}

graphviz_output_format = 'svg'
todo_include_todos = True

import sphinx_rtd_theme

html_theme = 'sphinx_rtd_theme'
html_theme_options = {
	'collapse_navigation' : False
}

html_static_path = [
	'_static'
]
html_css_files = [
	'styles.css'
]

autosectionlabel_prefix_document = True
