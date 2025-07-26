# SPDX-License-Identifier: BSD-3-Clause
import os, sys, datetime
sys.path.insert(0, os.path.abspath('.'))

from torii   import __version__ as torii_version
from squishy import __version__ as squishy_version

project   = 'Squishy'
version   = squishy_version
release   = version.split('+')[0]
copyright = f'{datetime.date.today().year}, Aki "lethalbit" Van Ness, et. al.'
language  = 'en'

extensions = [
	'sphinx.ext.autodoc',
	'sphinx.ext.doctest',
	'sphinx.ext.extlinks',
	'sphinx.ext.githubpages',
	'sphinx.ext.graphviz',
	'sphinx.ext.intersphinx',
	'sphinx.ext.napoleon',
	'sphinx.ext.todo',
	'sphinxcontrib.mermaid',
	'sphinxcontrib.wavedrom',
	'sphinxext.opengraph',
	'myst_parser',
	'sphinx_autodoc_typehints',
	'sphinx_copybutton',
	'sphinx_inline_tabs',
	'sphinx_design',
]

source_suffix = {
	'.rst': 'restructuredtext',
	'.md': 'markdown',
}

extlinks = {
	'sw-issue': ('https://github.com/squishy-scsi/squishy/issues/%s',  'squishy/%s', ),
	'hw-issue': ('https://github.com/squishy-scsi/hardware/issues/%s', 'squishy-hardware/%s', ),
	'pypi':     ('https://pypi.org/project/%s/', '%s', ),
}

pygments_style              = 'default'
pygments_dark_style         = 'monokai'
autodoc_member_order        = 'bysource'
autodoc_docstring_signature = False
graphviz_output_format      = 'svg'
todo_include_todos          = True

intersphinx_mapping = {
	'python'    : ('https://docs.python.org/3', None),
	'torii'     : (f'https://torii.shmdn.link/v{torii_version}', None),
	'torii-usb' : ('https://torii-usb.shmdn.link/', None),
	'construct' : ('https://construct.readthedocs.io/en/latest', None),
}

napoleon_google_docstring              = True
napoleon_numpy_docstring               = True
napoleon_use_ivar                      = True
napoleon_use_admonition_for_notes      = True
napoleon_use_admonition_for_examples   = True
napoleon_use_admonition_for_references = True
napoleon_custom_sections  = [
	('Attributes', 'params_style'),
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

always_use_bars_union = True
typehints_defaults = 'braces-after'
typehints_use_signature = True
typehints_use_signature_return = True

offline_skin_js_path = '_static/js/wavedrom.skin.js'
offline_wavedrom_js_path = '_static/js/wavedrom.min.js'


linkcheck_retries = 2
linkcheck_workers = 1 # At the cost of speed try to prevent rate-limiting
linkcheck_ignore  = [
	r'https://www\.codesrc\.com/.*', # SSL is broken
]

linkcheck_anchors_ignore_for_url = [
	r'^https://web\.libera\.chat/',
]
