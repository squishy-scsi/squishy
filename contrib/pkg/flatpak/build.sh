#!/bin/bash
VERSION=$(git describe --tag --always)
PKG_NAME="python3-squishy-${VERSION}"

sed -e "s/@SQUISHY_VERSION@/${VERSION}/g" \
	-e "s/@SQUISHY_PKG_VERSION@/$(echo $VERSION | sed 's/-/_/g')/" \
	moe.scsi.Squishy.yml.in > moe.scsi.Squishy.yml
