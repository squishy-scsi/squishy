# SPDX-License-Identifier: BSD-3-Clause

from PySide2.QtCore    import *
from PySide2.QtGui     import *
from PySide2.QtWidgets import *

class FontPicker(QWidget):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self._layout = QHBoxLayout(self)

		self.font = kwargs.get('font', QFont('Noto Sans', 12))
		self._font_info = QFontInfo(self.font)

		self._spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
		self._layout.addItem(self._spacer)

		self.lbl_font_name = QLabel(self)
		self.lbl_font_name.setText(
			f'{self._font_info.family()}, {self._font_info.pointSize()}'
		)
		self._layout.addWidget(self.lbl_font_name)

		self.btn_pick_font = QPushButton(self)
		self.btn_pick_font.setIcon(QIcon.fromTheme('dialog-text-and-font'))
		self._layout.addWidget(self.btn_pick_font)

		self.btn_pick_font.clicked.connect(self._pick_font)

	def set_font(self, family, size):
		self.font = QFont(family, size)
		self._font_info = QFontInfo(self.font)
		self._update_text()

	def _update_text(self):
		self.lbl_font_name.setText(
			f'{self._font_info.family()}, {self._font_info.pointSize()}'
		)

	def _pick_font(self):
		res = QFontDialog.getFont()
		if res[0]:
			self.font = res[1]
			self._font_info = QFontInfo(self.font)
			self._update_text()
