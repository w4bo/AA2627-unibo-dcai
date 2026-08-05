#!/bin/bash

SRC="removed-img"
DEST="img"

for dir in "$SRC"/*/; do
  folder_name=$(basename "$dir")

  src_path="$SRC/$folder_name"
  dest_path="$DEST/$folder_name"

  # Create destination folder if it doesn't exist
  mkdir -p "$dest_path"

  # Move files
  mv "$src_path"/* "$dest_path"/ 2>/dev/null
done

# Move files directly inside removed-img to img
find "$SRC" -maxdepth 1 -type f -exec mv {} "$DEST"/ \;