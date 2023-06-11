#!/usr/bin/env python
# SPDX-License-Identifier: BSD-3-Clause
import sys
from pathlib import Path

try:
	from squishy.cli import main
except ImportError:
	squishy_path = Path(sys.argv[0]).resolve()

	if (squishy_path.parent / 'squishy').is_dir():
		sys.path.insert(0, str(squishy_path.parent))

	from squishy.cli import main

sys.exit(main())
