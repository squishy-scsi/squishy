#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-3-Clause
import sys
from pathlib import Path

try:
	from squishy.main import gui_main
except ImportError:
	squishy_path = Path(sys.argv[0]).resolve()

	if (squishy_path.parent.parent / 'squishy').is_dir():
		sys.path.insert(0, str(squishy_path.parent.parent))

	from squishy.main import gui_main

sys.exit(gui_main())
