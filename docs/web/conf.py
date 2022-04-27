# SPDX-License-Identifier: BSD-3-Clause
import os, sys, datetime
sys.path.insert(0, os.path.abspath('.'))

try:
	import squishy
	version = squishy.__version__

except ImportError:
	version = ':nya_confused:' # :nocov:

project   = 'Squishy'
release   = version.split('+')[0]
copyright = f'{datetime.date.today().year}, Aki "lethalbit" Van Ness, et. al.'
language  = 'en'

extensions = [
	'sphinx.ext.autodoc',
	'sphinx.ext.doctest',
	'sphinx.ext.githubpages',
	'sphinx.ext.graphviz',
	'sphinx.ext.intersphinx',
	'sphinx.ext.napoleon',
	'sphinx.ext.todo',
	'sphinxcontrib.mermaid',
	'sphinxcontrib.platformpicker',
	'myst_parser',
	'sphinx_construct',
	'sphinx_rtd_theme',
]

source_suffix = {
	'.rst': 'restructuredtext',
	'.md': 'markdown',
}

pygments_style         = 'monokai'
autodoc_member_order   = 'bysource'
graphviz_output_format = 'svg'
todo_include_todos     = True

intersphinx_mapping = {
	'python'   : ('https://docs.python.org/3', None),
	'luna'     : ('https://luna.readthedocs.io/en/latest', None),
	'amaranth' : ('https://amaranth-lang.org/docs/amaranth/latest', None),
	'construct': ('https://construct.readthedocs.io/en/latest', None),
}

napoleon_google_docstring = False
napoleon_numpy_docstring  = True
napoleon_use_ivar         = True
napoleon_custom_sections  = ["Platform overrides"]



html_baseurl     = 'https://docs.scsi.moe'
html_theme       = 'sphinx_rtd_theme'
html_copy_source = False

html_theme_options = {
	'collapse_navigation' : False,
	'style_external_links': True,
}

html_static_path = [
	'_static'
]

html_css_files = [
	'css/styles.css'
]

html_js_files = [
	'js/mermaid.min.js'
]

html_style = 'css/styles.css'

autosectionlabel_prefix_document = True
# Disable CDN so we use the local copy
mermaid_version = ''
