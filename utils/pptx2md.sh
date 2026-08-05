#!/bin/bash

# Usage: ./pptx2md-wrapper.sh <input1.pptx> <input2>
# Example: ./pptx2md-wrapper.sh slides.pptx assets/

set -exo

if [ "$#" -ne 2 ]; then
  echo "Usage: $0 <input1.pptx> <input2>" >&2
  exit 1
fi

INPUT1="$1"
INPUT2="$2"

# Ensure input1 ends with .pptx
if [[ "$INPUT1" != *.pptx ]]; then
  echo "Error: input1 must be a .pptx file" >&2
  exit 1
fi

# Replace .pptx with .md for output
OUTPUT_MD="${INPUT1%.pptx}.md"

pptx2md "$INPUT1" \
  -i "img/$INPUT2" \
  -o "$OUTPUT_MD" \
  --disable-color \
  --disable-escaping \
  --disable-notes \
  --keep-similar-titles

# Run post-processing script on the generated Markdown
UTILS_SCRIPT="utils/clean_pptx2md.py"

if [ ! -f "$UTILS_SCRIPT" ]; then
echo "Error: $UTILS_SCRIPT not found or not executable" >&2
exit 1
fi

python "$UTILS_SCRIPT" "$OUTPUT_MD"