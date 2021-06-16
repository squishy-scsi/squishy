#!/usr/bin/env python
# SPDX-License-Identifier: BSD-3-Clause
import sys
from pathlib import Path

squish_path = Path(sys.argv[0]).resolve()

if (squish_path.parent / 'squish').is_dir():
	sys.path.insert(0, str(squish_path.parent))

from squish import main

if __name__ == '__main__':
	sys.exit(main())
