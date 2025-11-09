#!/bin/bash

# TEMP.sh
# Recursively append contents of all .py, .html, .js, and .css files
# (excluding files starting with "TEMP") to TEMP.log
# Adds a comment with the file's relative path before its content
# and two empty lines after each file.

# Optional: clear TEMP.log each run (uncomment if desired)
# > TEMP.log

# Use find to locate matching files recursively
find . -type f \( -name "*.py" -o -name "*.html" -o -name "*.js" -o -name "*.css" \) ! -name "TEMP*" | while read -r file; do
    echo "# File: $file" >> TEMP.log
    cat "$file" >> TEMP.log
    echo -e "\n\n" >> TEMP.log
done
