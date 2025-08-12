# SPDX-License-Identifier: BSD-3-Clause
from datetime import date

from torii     import __version__ as torii_version
from torii_usb import __version__ as torii_usb_version
from squishy   import __version__ as squishy_version

project   = 'Squishy'
version   = squishy_version
release   = version.split('+')[0]
copyright = f'{date.today().year}, Aki "lethalbit" Van Ness, et. al.'
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
	'myst_parser',
	'sphinx_autodoc_typehints',
	'sphinx_codeautolink',
	'sphinx_copybutton',
	'sphinx_design',
	'sphinx_inline_tabs',
	'sphinx_multiversion',
	'sphinxcontrib.mermaid',
	'sphinxcontrib.wavedrom',
	'sphinxext.opengraph',
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
graphviz_output_format      = 'svg'
autodoc_docstring_signature = False
todo_include_todos          = True

intersphinx_mapping = {
	'python': ('https://docs.python.org/3', None),
	'torii': (f'https://torii.shmdn.link/v{torii_version}', None),
	'torii-usb': (f'https://torii-usb.shmdn.link/v{torii_usb_version}', None),
	'construct': ('https://construct.readthedocs.io/en/latest', None),
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

always_use_bars_union = True
typehints_defaults = 'braces-after'
typehints_use_signature = True
typehints_use_signature_return = True

templates_path = [
	'_templates',
]

html_baseurl     = 'https://docs.scsi.moe'
html_theme       = 'furo'
html_copy_source = False

html_theme_options = {
	'announcement': 'This documentation is a work in progress, and you can help us <a href="https://github.com/squishy-scsi/squishy/blob/main/CONTRIBUTING.md">improve it!</a>', # noqa: E501
	'light_css_variables': {
		'color-brand-primary': '#2672a8',
		'color-brand-content': '#2672a8',
		'color-announcement-background': '#ffab87',
		'color-announcement-text': '#494453',
	},
	'dark_css_variables': {
		'color-brand-primary': '#85C2FE',
		'color-brand-content': '#85C2FE',
		'color-announcement-background': '#ffab87',
		'color-announcement-text': '#494453',
	},
	'source_repository': 'https://github.com/squishy-scsi/squishy/',
	'source_branch': 'main',
	'source_directory': 'docs/',
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

# TODO(aki): OpenGraph metadata stuff
ogp_site_url = html_baseurl
ogp_social_cards = {}
ogp_image = None
ogp_image_alt = None
ogp_custom_meta_tags = list[str]()
ogp_enable_meta_description = True

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

# Sphinx-Multiversion stuff
# TODO(aki): Revert to `^v(?!0)\d+\.\d+\.\d+$` when `v1.0.0` drops, we need to gen the v0.8.0 stable for now
smv_tag_whitelist    = r'^v\d+\.\d+\.\d+$'
smv_branch_whitelist = r'^main$'                    # Only look at `main`
smv_remote_whitelist = r'^origin$'
smv_released_pattern = r'^refs/tags/v.+$'           # Only consider tags to be full releases
smv_outputdir_format = '{ref.name}'
