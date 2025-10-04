#!/bin/bash
# Script to add placeholder files to make folders visible in Obsidian

# Find all directories and add a .placeholder.md if they don't have any .md files
find . -type d -not -path '*/\.*' | while read dir; do
    # Check if directory has any .md files
    if [ -z "$(ls -A "$dir"/*.md 2>/dev/null)" ]; then
        # Create a placeholder with folder name as title
        folder_name=$(basename "$dir")
        echo "# $folder_name" > "$dir/.placeholder.md"
        echo "Added placeholder to: $dir"
    fi
done

echo "Done! All folders should now be visible in Obsidian"
