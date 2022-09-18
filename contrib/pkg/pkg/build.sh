#!/bin/bash
VERSION=${2}
PKG_NAME="python3-squishy-${VERSION}"

mkdir ${PKG_NAME}

pushd ${PKG_NAME}
tar xzf ${1}/*.tar.gz --strip-components=1
popd

tar cfJ ${PKG_NAME}.orig.tar.xz ${PKG_NAME}

rm -r ${PKG_NAME}

DIGEST="$(sha512sum ${PKG_NAME}.orig.tar.xz | tee ${PKG_NAME}.orig.tar.xz.sha512 | cut -b -128)"

sed -e "s/@SQUISHY_VERSION@/${VERSION}/g" \
	-e "s/@SQUISHY_PKG_VERSION@/$(echo $VERSION | sed 's/-/_/g')/" \
	-e "s/@SQUISHY_HASH@/${DIGEST}/g" PKGBUILD.in > PKGBUILD

makepkg -C
