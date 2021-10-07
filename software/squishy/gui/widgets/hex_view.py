# SPDX-License-Identifier: BSD-3-Clause

from PySide6.QtCore    import *
from PySide6.QtGui     import *
from PySide6.QtWidgets import *


class HexViewWidget(QTableView):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)


if __name__ == '__main__':
	import sys

	class MainWindow(QMainWindow):
		def __init__(self):
			super().__init__()

			self.resize(1024, 768)

			self.container = QFrame()
			self.layout = QVBoxLayout()

			self._widget = HexViewWidget()

			self.layout.addWidget(self._widget, Qt.AlignCenter, Qt.AlignCenter)

			self.container.setLayout(self.layout)
			self.setCentralWidget(self.container)

	app = QApplication(sys.argv)
	mw = MainWindow()
	mw.show()

	sys.exit(app.exec())
