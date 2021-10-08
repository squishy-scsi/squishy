# SPDX-License-Identifier: BSD-3-Clause
from os import path

from PySide6.QtCore    import *
from PySide6.QtWidgets import *
from PySide6.QtUiTools import QUiLoader

from .widgets          import FontPicker, ColorPicker

class PreferencesWindow:
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

		self.window = self.loader.load(self._ui_file)


	def show(self):
		self.window.show()
