#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-3-Clause
import sys
from pathlib import Path

gateware_path = Path(sys.argv[0]).resolve()

if (gateware_path.parent / 'squishy').is_dir():
	sys.path.insert(0, str(gateware_path.parent))

from squishy import cli

if __name__ == '__main__':
	sys.exit(cli())

