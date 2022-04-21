#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-3-Clause
import sys
from pathlib import Path

squishy_path = Path(sys.argv[0]).resolve()

from squishy import main

if __name__ == "__main__":
	sys.exit(main())
