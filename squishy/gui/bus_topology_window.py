# SPDX-License-Identifier: BSD-3-Clause
from PySide2.QtCore    import *
from PySide2.QtWidgets import *
from PySide2.QtUiTools import QUiLoader

from .resources        import *
from .widgets          import BusTopologyWidget

class BusTopologyWindow:
	def __init__(self):
		self.loader = QUiLoader()
		self._ui_file = QFile(
			get_resource('bus_topology_window.ui', ResourceCategory.UI, ResourceType.PATH)
		)

		self.loader.registerCustomWidget(BusTopologyWidget)

		self.window = self.loader.load(self._ui_file)


	def show(self):
		self.window.show()
