#!/bin/bash
set -xo

# Function: replace a file if it does not exist OR is a dangling symlink
ensure_file() {
    local target="$1"
    local source="$2"

    # If the file is a symlink AND its destination does not exist → remove it
    if [ -h "$target" ] && [ ! -e "$(readlink "$target")" ]; then
        echo "Removing dangling symlink: $target"
        rm "$target"
    fi

    # If the file still does not exist → copy it
    if [ ! -e "$target" ]; then
        echo "Copying $source → $target"
        cp "$source" "$target"
    fi
}

# Apply to your files
ensure_file "publish.sh"        "utils/publish.sh.example"
ensure_file "_quarto.yml"       "utils/_quarto.yml"
ensure_file "docker-compose.yml" "utils/docker-compose.yml"
