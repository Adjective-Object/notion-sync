#!/usr/bin/env bash

CURRENT_VERSION=$(cat .bumpversion.cfg | grep current_version | sed 's/.*= //')
echo "compare against $CURRENT_VERSION"
MESSAGE=`git log v$CURRENT_VERSION..HEAD --pretty=%B`

if [[ $MESSAGE == *"major"* ]]; then
    echo "bumping major version"
    pipenv run bumpversion major
elif [[ $MESSAGE == *"minor"* ]]; then
    echo "bumping minor version"
    pipenv run bumpversion minor
elif [[ $MESSAGE == *"patch"* ]]; then
    echo "bumping patch  version"
    pipenv run bumpversion patch
else
    echo "commit message did not match major/patch/minor. not bumping version"
fi
