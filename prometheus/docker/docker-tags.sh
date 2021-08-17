#!/bin/bash

# This script returns a space separated list of versions that should
# be used when building a docker image from this git ref

# If a ref is passed in we can check if it is a tag or a branch
REF=$1

# Get script dir
CURDIR=$(cd $(dirname $0); pwd)

DATABRIDGE_PATH=$CURDIR/../unisight-data-bridge
VERSION=$(cd $DATABRIDGE_PATH && python setup.py --version 2> /dev/null)

# Always include our slug version as determined by setuptools_scm
VERSION_SLUG=$(echo $VERSION | sed 's/\+/_/')
TAGS=$VERSION_SLUG

# If our passed in ref is a tag
if echo $REF | grep '^refs/tags/v' > /dev/null 2>&1; then
    TAGS="$TAGS $(echo $VERSION | sed 's/^\([0-9]*\)\.\([0-9]*\)\..*/\1.\2/' )"
fi

if [ "$REF" == "refs/heads/master" ]; then
    TAGS="$TAGS latest"
fi

echo $TAGS
