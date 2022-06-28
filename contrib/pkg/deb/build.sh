#!/bin/bash
VERSION=$(git describe --tag --always)
PKG_NAME="python3-squishy_${VERSION}"

pushd ../../../
python3 setup.py sdist
popd

mkdir ${PKG_NAME}

pushd ${PKG_NAME}
tar xzf ../../../../dist/*.tar.gz --strip-components=1
popd

tar cfJ ${PKG_NAME}.orig.tar.xz ${PKG_NAME}

cp -a debian ${PKG_NAME}
pushd ${PKG_NAME}
debuild
popd

rm -rf ${PKG_NAME} ${PKG_NAME}-1_amd64.build ${PKG_NAME}_amd64.build
