#!/bin/sh

PACKAGE_JSON=../pootle/static/js/package.json
DOCS=../docs/*.md
VERSION=`grep '"version"' $PACKAGE_JSON | awk '{print $2}' | sed -e 's/[",]//g'`

sed -i "" -e "s/|version|/$VERSION/g" $DOCS
