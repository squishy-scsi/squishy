#!/bin/bash
VERSION=$(git describe --tag --always)
PKG_NAME="python3-squishy-${VERSION}"

mkdir AppDir

PIP_CONFIG_FILE=/dev/null pip install --isolated --root="AppDir" --prefix="/usr" --ignore-installed "../../../.[gui,toolchain,firmware]"

sed -e "s/@SQUISHY_VERSION@/${VERSION}/g" \
	-e "s/@SQUISHY_PKG_VERSION@/$(echo $VERSION | sed 's/-/_/g')/" \
	squishy-appimage.yml.in > squishy-appimage.yml

appimage-builder --recipe squishy-appimage.yml

rm -r AppDir
