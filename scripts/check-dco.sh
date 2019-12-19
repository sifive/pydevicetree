#!/usr/bin/env bash

set -eu

TARGET_BRANCH=$1; shift 1;
SOURCE_BRANCH=$1; shift 1;

MERGE_BASE=`git merge-base $TARGET_BRANCH $SOURCE_BRANCH`

PULL_COMMITS=`git log --format=%H --no-merges $MERGE_BASE..$SOURCE_BRANCH`

for commit in ${PULL_COMMITS[@]} ; do
        body=`git log --format=%B -n 1 $commit`
        if [ `echo $body | grep -c "Signed-off-by:"` -eq 0 ] ; then
                echo "$0 FAILED: Commit $commit missing a Developer Certificate of Origin (DCO)"
                exit 1
        else
                echo "$0: Found Developer Certificate of Origin in commit $commit"
        fi
done

echo "$0 PASSED: All commits contain a Developer Certificate of Origin (DCO)"
