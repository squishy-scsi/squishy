#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-3-Clause
import sys
import os
from pathlib import Path

squishy_path = Path(sys.argv[0]).resolve()

luna_dir = os.environ.get('LUNA_DIR', squishy_path.parent.parent / 'deps/luna')

sys.path.insert(0, luna_dir)

print(luna_dir)

if (squishy_path.parent / 'squishy').is_dir():
	sys.path.insert(0, str(squishy_path.parent))

from squishy import main

if __name__ == '__main__':
	sys.exit(main())


