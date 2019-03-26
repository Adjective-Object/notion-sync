#!/usr/bin/env bash
git branch
git log -1 
git diff --exit-code master origin/master
if [[ "$?" != "0" ]]; then
    git push https://$GITHUB_TOKEN:x-oauth-basic@$GITHUB_REMOTE master:master
    git push https://$GITHUB_TOKEN:x-oauth-basic@$GITHUB_REMOTE --tags
	make publish-travis
fi
