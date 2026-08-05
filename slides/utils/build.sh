#!/bin/bash
set -e
for FILE in *.ipynb; do # "lab-01-dataunderstanding.ipynb" "lab-02-housing.ipynb"
    echo "Processing $FILE file...";
    if [[ "$FILE" == *"lab-00"* ]]; then
        echo "Skipping $FILE"
        continue
    fi
    filename=$(basename -- "$FILE")
    extension="${filename##*.}"
    filename="${filename%.*}"
    jupyter nbconvert --clear-output --inplace "$FILE"
    jupyter nbconvert --execute --to notebook --inplace "$FILE"
done
