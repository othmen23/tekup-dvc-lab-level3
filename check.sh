#!/bin/bash
# 1) rebuild the pipeline at this commit; if it cannot run, skip the commit
dvc repro >/dev/null 2>&1 || exit 125

# 2) test the metric
python check_metric.py
result=$?

# 3) restore tracked files that dvc repro may have touched,
#    so bisect can move to the next commit without "local changes" errors
git checkout -- dvc.lock metrics/metrics.json

exit $result
