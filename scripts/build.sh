#!/bin/bash -e
  
usage() {
  return 0
}

build() {
  rm -f README.rst && m2r README.md
  pip install -r requirements.txt
  python setup.py bdist_rpm --release ${BUILD_NUMBER}
}

clean() {
  rm -rf \
    README.rst build dist \
    f5_lbaasv2_bigiq_agent/__init__.pyc \
    f5_openstack_lbaasv2_bigiq_agent.egg-info
}

BUILD_DIR="."
BUILD_NUMBER="1"

while getopts d:n:h o ; do
  case "$o" in
    d)   BUILD_DIR="$OPTARG";;
    n)   BUILD_NUMBER="$OPTARG";;
    h)   usage
         exit 0;;
    [?]) usage
         exit 1;;
  esac
done
shift $((OPTIND-1))

cd ${BUILD_DIR}

if [[ $1 == "clean" ]] ; then
  clean
else
  build
fi
