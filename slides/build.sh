#!/bin/bash
set -euo pipefail

for notebook in *.ipynb; do
    [[ "$notebook" == *lab-00* ]] && continue
    echo "Executing $notebook"
    jupyter nbconvert --clear-output --inplace "$notebook"
    jupyter nbconvert --execute --to notebook --inplace \
        --ExecutePreprocessor.timeout=600 "$notebook"
done
