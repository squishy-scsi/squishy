# SPDX-License-Identifier: BSD-3-Clause
from PySide2.QtCore    import *
from PySide2.QtWidgets import *
from PySide2.QtGui     import QPixmap
from PySide2.QtUiTools import QUiLoader

from .resources        import *
from ..                import __version__

class AboutWindow:
	def __init__(self):
		self.loader = QUiLoader()
		self._ui_file = QFile(
			get_resource('about_window.ui', ResourceCategory.UI, ResourceType.PATH)
		)

		self.window = self.loader.load(self._ui_file)
		self._sachi = QPixmap(get_resource('about.png', ResourceCategory.IMAGE, ResourceType.PATH))
		self.window.lbl_sachi.setPixmap(self._sachi)
		self.window.lbl_version.setText(__version__)

	def show(self):
		self.window.show()
