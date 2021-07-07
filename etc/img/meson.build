# SPDX-License-Identifier: BSD-3-Clause

inkscape = find_program('inkscape', native: true, required: true)


png_export = generator(
	inkscape,
    output: '@BASENAME@.png',
    arguments: [
    	'-o', '@OUTPUT@',
    	'--export-type=png',
    	'-D',
    	'-d', get_option('image_dpi').to_string(),
    	'@INPUT@'
    ],
)
