#!/bin/bash
VERSION="$2"

flatpak-builder --force-clean $1 moe.scsi.Squishy.json
