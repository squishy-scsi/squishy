# SPDX-License-Identifier: BSD-3-Clause
import os, sys, datetime
sys.path.insert(0, os.path.abspath('.'))

from squishy import __version__ as squishy_version


project   = 'Squishy'
version   = squishy_version
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
	'sphinxcontrib.wavedrom',
	'myst_parser',
	'sphinx_inline_tabs',
	'sphinxext.opengraph',
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
	'sol'      : ('https://sol.shmdn.link/', None),
	'torii'    : ('https://torii.shmdn.link/', None),
	'construct': ('https://construct.readthedocs.io/en/latest', None),
}

napoleon_google_docstring = False
napoleon_numpy_docstring  = True
napoleon_use_ivar         = True
napoleon_custom_sections  = [
	'Platform overrides'
]

myst_heading_anchors = 3

html_baseurl     = 'https://docs.scsi.moe'
html_theme       = 'furo'
html_copy_source = False

html_theme_options = {
	'top_of_page_buttons': [],
}

html_static_path = [
	'_static'
]

html_css_files = [
	'css/styles.css'
]

html_js_files = [
	'js/mermaid.min.js',
	'js/wavedrom.min.js',
	'js/wavedrom.skin.js',
]

# OpenGraph config bits
ogp_site_url = html_baseurl
ogp_image    = f'{html_baseurl}/_images/og-image.png'

autosectionlabel_prefix_document = True
# Disable CDN so we use the local copy
mermaid_version = ''

offline_skin_js_path = '_static/js/wavedrom.skin.js'
offline_wavedrom_js_path = '_static/js/wavedrom.min.js'

linkcheck_anchors_ignore_for_url = [
	r'^https://web\.libera\.chat/',
]

linkcheck_ignore = [
	r'https://www\.codesrc\.com/.*', # SSL is broken
]
