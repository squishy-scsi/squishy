# SPDX-License-Identifier: BSD-3-Clause

from PySide2.QtCore    import *
from PySide2.QtGui     import *
from PySide2.QtWidgets import *

from ..key_helper      import SquishyGuiKey

class HotkeySelect(QWidget):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self._layout    = QGridLayout(self)
		self._keys      = []
		self._new_input = False

		self._clr_btn = QPushButton(self)
		self._clr_btn.setIcon(QIcon.fromTheme('edit-clear'))

		clr_sp = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
		clr_sp.setHorizontalStretch(0)
		clr_sp.setVerticalStretch(0)
		clr_sp.setHeightForWidth(self._clr_btn.sizePolicy().hasHeightForWidth())

		self._clr_btn.setSizePolicy(clr_sp)
		self._layout.addWidget(self._clr_btn, 0, 1, 1, 1)

		self._pick_btn = QPushButton(self)
		self._pick_btn.setIcon(QIcon.fromTheme('dialog-object-properties'))
		self._pick_btn.setCheckable(True)
		self._pick_btn.setText('None')
		self._pick_btn.setFocusPolicy(Qt.NoFocus)

		pick_sp = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Minimum)
		pick_sp.setHorizontalStretch(0)
		pick_sp.setVerticalStretch(0)
		pick_sp.setHeightForWidth(self._pick_btn.sizePolicy().hasHeightForWidth())

		self._pick_btn.setSizePolicy(pick_sp)
		self._layout.addWidget(self._pick_btn, 0, 0, 1, 1)

		self._clr_btn.clicked.connect(self.clear)
		self._pick_btn.clicked.connect(self._pick)

		self._rst_timer = QTimer(self)
		self._rst_timer.setInterval(5000)
		self._rst_timer.setSingleShot(True)
		self._rst_timer.timeout.connect(self._reset)


	def _update_label(self):
		if len(self._keys) > 0:
			self._pick_btn.setText('+'.join(self._keys))
		else:
			self._pick_btn.setText('None')

	def keyPressEvent(self, e):
		if self._pick_btn.isChecked():
			if self._new_input:
				self._keys = []
				self._new_input = False

			key = e.key()

			if key == Qt.Key_Meta and (e.nativeModifiers() & Qt.ShiftModifier) == Qt.ShiftModifier:
				key = Qt.Key_Alt

			self._keys.append(SquishyGuiKey.to_str(e))
			self._update_label()
			self._rst_timer.start()

	def keyReleaseEvent(self, e):
		if self._pick_btn.isChecked():
			self._reset()
		elif e.key() == Qt.Key_Space or e.key() == Qt.Key_Enter or e.key() == Qt.Key_Return:
			self._pick_btn.setChecked(True)
			self._pick_btn.setText('Input...')
			self._rst_timer.start()
			self._new_input = True

	def clear(self):
		self._keys = []
		self._update_label()

	def _reset(self):
		self._pick_btn.setChecked(False)
		self._update_label()

	def _pick(self):
		self._pick_btn.setChecked(True)
		self._pick_btn.setText('Input...')
		self._rst_timer.start()
		self._new_input = True

	def keys(self):
		return self._keys

	def set_keys(self, keys):
		self._keys = keys
		self._update_label()


if __name__ == '__main__':
	import sys

	class MainWindow(QMainWindow):
		def __init__(self):
			super().__init__()

			self.resize(210, 42)

			self.container = QFrame()
			self.layout = QVBoxLayout()

			self._widget = HotkeySelect()

			self.layout.addWidget(self._widget, Qt.AlignCenter, Qt.AlignCenter)

			self.container.setLayout(self.layout)
			self.setCentralWidget(self._widget)

	app = QApplication(sys.argv)
	mw = MainWindow()
	mw.show()

	sys.exit(app.exec_())
