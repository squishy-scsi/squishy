#!/bin/bash
VERSION=${2}
PKG_NAME="python3-squishy-${VERSION}"

mkdir ${PKG_NAME}

pushd ${PKG_NAME}
tar xzf ${1}/*.tar.gz --strip-components=1
popd


tar cfJ ${PKG_NAME}.orig.tar.xz ${PKG_NAME}

rpmdev-setuptree

sed -e "s/@SQUISHY_VERSION@/${VERSION}/g" squishy.spec.in > ~/rpmbuild/SPECS/squishy.spec

cp ${PKG_NAME}.orig.tar.xz ~/rpmbuild/SOURCES/

rpmbuild -ba ~/rpmbuild/SPECS/squishy.spec

cp ~/rpmbuild/RPMS/noarch/python3-squishy-*.rpm .
