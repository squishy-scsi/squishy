# SPDX-License-Identifier: BSD-3-Clause
from os import path

from PySide2.QtCore    import *
from PySide2.QtWidgets import *
from PySide2.QtUiTools import QUiLoader

class DevicesWindow:
	def __init__(self):
		self.loader = QUiLoader()
		self._ui_file = QFile(
			path.join(
				path.dirname(path.realpath(__file__)),
				'devices_window.ui'
			)
		)

		self.window = self.loader.load(self._ui_file)


	def show(self):
		self.window.show()
