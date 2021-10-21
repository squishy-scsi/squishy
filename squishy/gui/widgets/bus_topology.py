# SPDX-License-Identifier: BSD-3-Clause

from PySide2.QtCore    import *
from PySide2.QtGui     import *
from PySide2.QtWidgets import *
from PySide2.QtSvg     import QSvgRenderer
from PySide2.QtOpenGL  import *

class BusTopologyWidget(QAbstractScrollArea):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self._scale = 1.0
		self._offset = QPoint(0, 0)


	def viewOffsetChanged(self, pos: QPoint):
		print(pos)

	def viewScaleChanged(self, scale: float):
		print(scale)


	def paintEvent(self, e):
		p = QPainter(self)


		p.end()

	def wheelEvent(self, e):
		pass

	def mousePressEvent(self, e):
		pass

	def mouseMoveEvent(self, e):
		pass

	def mouseReleaseEvent(self, e):
		pass

	def mouseDoubleClickEvent(self, e):
		pass

if __name__ == '__main__':
	import sys

	class MainWindow(QMainWindow):
		def __init__(self):
			super().__init__()

			self.resize(1024, 768)

			self.container = QFrame()
			self.layout = QVBoxLayout()

			self._widget = BusTopologyWidget()

			self.layout.addWidget(self._widget, Qt.AlignCenter, Qt.AlignCenter)

			self.container.setLayout(self.layout)
			self.setCentralWidget(self.container)

	app = QApplication(sys.argv)
	mw = MainWindow()
	mw.show()

	sys.exit(app.exec())
