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


	def _save_settings(self):
		self.settings['gui']['appearance']['show_splash'] = self.window.chk_splash.checkState() == Qt.Checked


		with open(SQUISHY_SETTINGS_FILE, 'w') as cfg:
			json.dump(self.settings, cfg)

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

		self._fill_settings()

	def show(self):
		self.window.show()
