# SPDX-License-Identifier: BSD-3-Clause
from os import path

from PySide2.QtCore    import *
from PySide2.QtWidgets import *
from PySide2.QtGui     import QPixmap
from PySide2.QtUiTools import QUiLoader

from .resources   import SQUISHY_GUI_RESOURCES_LOC

class AboutWindow:
	def __init__(self):
		self.loader = QUiLoader()
		self._ui_file = QFile(
			path.join(
				path.dirname(path.realpath(__file__)),
				'about_window.ui'
			)
		)

		self.window = self.loader.load(self._ui_file)
		self._sachi = QPixmap(f'{SQUISHY_GUI_RESOURCES_LOC}/images/about.png')
		self.window.lbl_sachi.setPixmap(self._sachi)


	def show(self):
		self.window.show()
