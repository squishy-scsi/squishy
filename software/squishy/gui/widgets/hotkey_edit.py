# SPDX-License-Identifier: BSD-3-Clause

from PySide2.QtCore    import *
from PySide2.QtGui     import *
from PySide2.QtWidgets import *

from .hotkey_select    import HotkeySelect

__all__ = (
	'HotkeyEdit'
)


class HotkeyModel(QStandardItemModel):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.setColumnCount(2)
		self.setHorizontalHeaderLabels([
			'Action', 'Shortcut'
		])

class HotkeyDelegate(QStyledItemDelegate):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)


	def createEditor(self, p, opt, idx):
		if idx.column() == 1:
			n = HotkeySelect(p)

			return n
		else:
			return super().createEditor(p, opt, idx)

class HotkeyEntry(QStandardItem):
	def __init__(self, *args, name = '', hotkey = None, **kwargs):
		super().__init__(*args, **kwargs)
		self._hotkey = hotkey
		self._name = name

		self.setText(hotkey if hotkey != '' else 'None...')
		self.setEditable(True)

class HotkeyEdit(QWidget):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self._layout = QVBoxLayout(self)

		self._filter = QLineEdit(self)
		self._filter.setPlaceholderText('Filter...')
		self._layout.addWidget(self._filter)


		self._tree_view = QTreeView(self)
		# self._tree_view.setEditTriggers(QAbstractItemView.NoEditTriggers)
		self._tree_view.setAlternatingRowColors(True)
		self._tree_view.setSelectionBehavior(QAbstractItemView.SelectItems)
		self._tree_view.setRootIsDecorated(True)
		self._tree_view.setUniformRowHeights(True)
		self._tree_view.setSortingEnabled(False)
		self._tree_view.setAllColumnsShowFocus(False)
		self._layout.addWidget(self._tree_view)

		self._model = HotkeyModel()
		self._tree_view.setModel(self._model)
		self._edit_delagate = HotkeyDelegate()
		self._tree_view.setItemDelegate(self._edit_delagate)

		self._root_node = self._model.invisibleRootItem()


	def populate(self, hotkeys):


		for s, d in hotkeys.items():
			itm = QStandardItem(s)
			itm.setEditable(False)

			if isinstance(d, dict):
				for sub, sd in d.items():
					sub_itm = QStandardItem(sub)
					sub_itm.setEditable(False)

					for a, k in sd.items():
						if isinstance(k, dict):
							s2_itm = QStandardItem(a)
							s2_itm.setEditable(False)

							for s2, k2 in k.items():
								s2itm = QStandardItem(s2)
								s2itm.setEditable(False)

								key = HotkeyEntry(name = s2, hotkey = k2)
								s2_itm.appendRow([s2itm, key])

							sub_itm.appendRow(s2_itm)
						else:
							lbl_itm = QStandardItem(a)
							lbl_itm.setEditable(False)

							key = HotkeyEntry(name = a, hotkey = k)

							sub_itm.appendRow([lbl_itm, key])

					itm.appendRow(sub_itm)

			self._root_node.appendRow(itm)


if __name__ == '__main__':
	import sys

	_HOTKEYS = {
		'Menu': {
			'File': {
				'action_file_new_session': 'Ctrl+N',
				'action_file_open'       : 'Ctrl+O',
				'action_file_save'       : 'Ctrl+S',
				'action_file_save_as'    : 'Ctrl+Shift+S',
				'action_file_export_as'  : 'Ctrl+Shift+X',
				'action_file_quit'       : 'Ctrl+Q',
			},
			'Edit': {
				'Copy As...': {
					'action_copy_binary'   : '',
					'action_copy_hex'      : '',
					'action_copy_c_array'  : '',
					'action_copy_cpp_array': '',
					'action_copy_json'     : '',
				},
				'action_edit_find'         : 'Ctrl+F',
				'action_edit_find_next'    : 'Ctrl+Shift+N',
				'action_edit_find_previous': 'Ctrl+Shift+B',
				'action_edit_chrono_shift' : 'Ctrl+Shift+T',
				'action_edit_preferences'  : 'Ctrl+Shift+P',
			},
			'View': {
				'action_view_hex'         : '',
				'action_view_dissector'   : '',
				'action_view_repl'        : '',
				'action_view_toolbar'     : '',
				'action_view_bus_topology': '',
			},
			'Go': {
				'action_go_message' : 'Ctrl+G',
				'action_go_previous': 'Ctrl+Down',
				'action_go_next'    : 'Ctrl+Up',
				'action_go_first'   : 'Ctrl+Home',
				'action_go_last'    : 'Ctrl+End',
			},
			'Capture': {
				'action_capture_start'        : 'Ctrl+E',
				'action_capture_stop'         : 'Ctrl+Shift+E',
				'action_capture_restart'      : 'Ctrl+R',
				'action_capture_replay'       : 'Ctrl+Shift+R',
				'action_capture_filters'      : '',
				'action_capture_triggers'     : '',
				'action_capture_select_device': 'Ctrl+D',
				'action_capture_auto_scroll'  : '',
			},
			'Help': {
				'action_help_website': '',
				'action_help_about'  : '',
			}
		}
	}

	class MainWindow(QMainWindow):
		def __init__(self):
			super().__init__()

			self.resize(800, 800)

			self.container = QFrame()
			self.layout = QVBoxLayout()

			self._widget = HotkeyEdit()

			self._widget.populate(_HOTKEYS)

			self.layout.addWidget(self._widget, Qt.AlignCenter, Qt.AlignCenter)

			self.container.setLayout(self.layout)
			self.setCentralWidget(self._widget)

	app = QApplication(sys.argv)
	mw = MainWindow()
	mw.show()

	sys.exit(app.exec_())
