# SPDX-License-Identifier: BSD-3-Clause

from PySide2.QtCore    import *
from PySide2.QtGui     import *
from PySide2.QtWidgets import *

class ColorPicker(QWidget):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		size = QSize(114, 60)

		self.color = QColor(kwargs.get('color', '#2b2b2b'))


		self.resize(size)
		self.setMinimumSize(size)
		self.setMaximumSize(size)

		self._layout = QGridLayout(self)

		self.frm_display = QFrame(self)
		self.frm_display.setFrameShape(QFrame.StyledPanel)
		self._layout.addWidget(self.frm_display, 0, 0, 1, 1)

		self.btn_pick = QPushButton(self)
		self.btn_pick.setIcon(QIcon.fromTheme('preferences-desktop-color'))
		self.btn_pick.setIconSize(QSize(32, 32))
		self._layout.addWidget(self.btn_pick, 0, 1, 1, 1)

		self.btn_pick.clicked.connect(self._pick_color)
		self.frm_display.setStyleSheet(f'background-color: {self.color.name()};')

	def set_color(self, color):
		self.color = QColor(color)
		self.frm_display.setStyleSheet(f'background-color: {self.color.name()};')

	def _pick_color(self):
		dialog = QColorDialog(self)
		dialog.setCurrentColor(self.color)

		if dialog.exec_():
			self.color = dialog.selectedColor()
			self.frm_display.setStyleSheet(f'background-color: {self.color.name()};')

