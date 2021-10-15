# SPDX-License-Identifier: BSD-3-Clause
import json
from os import path

from PySide2.QtCore    import *
from PySide2.QtWidgets import *
from PySide2.QtUiTools import QUiLoader

from ..config          import SQUISHY_SETTINGS_FILE
from .widgets          import FontPicker, ColorPicker

class PreferencesWindow:
	def _fill_settings(self):
		self.window.chk_splash.setChecked(self.settings['gui']['appearance']['show_splash'])
		self.window.fp_main.set_font(
			self.settings['gui']['appearance']['font']['name'],
			self.settings['gui']['appearance']['font']['size'],
		)

		self.window.fp_hex.set_font(
			self.settings['gui']['appearance']['hex_view']['font']['name'],
			self.settings['gui']['appearance']['hex_view']['font']['size'],
		)
		self.window.clr_zero.set_color(
			self.settings['gui']['appearance']['hex_view']['color_map']['zero']
		)
		self.window.clr_low.set_color(
			self.settings['gui']['appearance']['hex_view']['color_map']['low']
		)
		self.window.clr_high.set_color(
			self.settings['gui']['appearance']['hex_view']['color_map']['high']
		)
		self.window.clr_max.set_color(
			self.settings['gui']['appearance']['hex_view']['color_map']['ones']
		)
		self.window.clr_printable.set_color(
			self.settings['gui']['appearance']['hex_view']['color_map']['printable']
		)

	def _save_settings(self):
		self.settings['gui']['appearance']['show_splash'] = self.window.chk_splash.checkState() == Qt.Checked
		self.settings['gui']['appearance']['font'] = {
			'name': self.window.fp_main._font_info.family(),
			'size': self.window.fp_main._font_info.pointSize(),
		}
		self.settings['gui']['appearance']['hex_view']['font'] = {
			'name': self.window.fp_hex._font_info.family(),
			'size': self.window.fp_hex._font_info.pointSize(),
		}
		self.settings['gui']['appearance']['hex_view']['color_map'] = {
			'zero'     : self.window.clr_zero.color.name(),
			'low'      : self.window.clr_low.color.name(),
			'high'     : self.window.clr_high.color.name(),
			'ones'     : self.window.clr_max.color.name(),
			'printable': self.window.clr_printable.color.name(),
		}



		with open(SQUISHY_SETTINGS_FILE, 'w') as cfg:
			json.dump(self.settings, cfg)

		self.window.close()

	def __init__(self):
		self.loader = QUiLoader()
		self._ui_file = QFile(
			path.join(
				path.dirname(path.realpath(__file__)),
				'preferences_window.ui'
			)
		)

		self.loader.registerCustomWidget(FontPicker)
		self.loader.registerCustomWidget(ColorPicker)

		with open(SQUISHY_SETTINGS_FILE, 'r') as cfg:
			self.settings = json.load(cfg)

		self.window = self.loader.load(self._ui_file)

		self.window.btn_save.clicked.connect(self._save_settings)
		self.window.lbl_settings.setText(f'Settings File: {SQUISHY_SETTINGS_FILE}')

		self.window.cmb_theme.addItems(QStyleFactory.keys())
		self.window.cmb_toolbar_style.addItems([
			'Icons Only',
			'Text Only',
			'Text and Icons',
		])
		self.window.cmb_hex_byte_style.addItems([
			'Hexadecimal',
			'Decimal',
			'Octal',
			'Binary'
		])

		self._fill_settings()

	def show(self):
		self.window.show()
