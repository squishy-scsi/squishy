# SPDX-License-Identifier: BSD-3-Clause

from PySide2.QtCore    import *
from PySide2.QtGui     import *
from PySide2.QtWidgets import *


class CaptureLog(QWidget):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self._layout = QVBoxLayout(self)

		self._filter = QLineEdit(self)
		self._filter.setPlaceholderText('Filter...')
		self._layout.addWidget(self._filter)

		self._log = QListView(self)
		self._layout.addWidget(self._log)
