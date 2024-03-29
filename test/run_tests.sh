#!/bin/bash
# script_dir=$(dirname "$(readlink -f "$0")")
# export KB_DEPLOYMENT_CONFIG=$script_dir/../deploy.cfg
# export KB_AUTH_TOKEN=`cat /kb/module/work/token`
# echo "Removing temp files..."
# rm -rf /kb/module/work/tmp/*
# echo "...done removing temp files."
# export PYTHONPATH=$script_dir/../lib:$PATH:$PYTHONPATH
# cd $script_dir/../test
# python -m nose --with-coverage --cover-package=kb_qsip --cover-html --cover-html-dir=/kb/module/work/test_coverage --nocapture  --nologcapture .


# #!/bin/sh
echo "Removing temp files..."
rm -rf /kb/module/work/tmp/* || true
echo "...done removing temp files."

current_dir=$(dirname "$(readlink -f "$0")")
export KB_DEPLOYMENT_CONFIG="$current_dir"/deploy.cfg
export PYTHONPATH="$current_dir"/../lib:"$PYTHONPATH"

# N.b. if running the data fetch tests, you will need a valid KBase dev token

# collect coverage data
pytest \
    --cov=lib/combinatrix \
    --cov-config=.coveragerc \
    --cov-report=html \
    --cov-report=xml \
    test/
