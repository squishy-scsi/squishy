# SPDX-License-Identifier: BSD-3-Clause

__all__ = (
	'SquishyGuiKey'
)

from PySide2.QtCore import Qt

class SquishyGuiKey:
	_KEYMAP = {}
	for k, v in vars(Qt.Key).items():
		if isinstance(v, Qt.Key):
			_KEYMAP[v] = k.partition('_')[2]

	_MODMAP = {
		Qt.ControlModifier:     _KEYMAP[Qt.Key_Control],
		Qt.AltModifier:         _KEYMAP[Qt.Key_Alt],
		Qt.ShiftModifier:       _KEYMAP[Qt.Key_Shift],
		Qt.MetaModifier:        _KEYMAP[Qt.Key_Meta],
		Qt.GroupSwitchModifier: _KEYMAP[Qt.Key_AltGr],
		Qt.KeypadModifier:      _KEYMAP[Qt.Key_NumLock],
	}

	def __init__(self, event):
		self._event = event

	def __int__(self):
		return self._event.key()

	def __str__(self):
		return SquishyGuiKey.to_str(self._event)

	@staticmethod
	def to_str(e):
		seq = []
		for m, t in SquishyGuiKey._MODMAP.items():
			if e.nativeModifiers() & m:
				seq.append(t)

		key = SquishyGuiKey._KEYMAP.get(e.key(), e.text())
		if key not in seq:
			seq.append(key)

		return '+'.join(seq)
