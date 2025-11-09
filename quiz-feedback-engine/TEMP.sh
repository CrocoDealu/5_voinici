#!/bin/bash

# TEMP.sh
# Append contents of all files in the current directory
# except files starting with "TEMP" to TEMP.log
# Adds a comment with the filename before each file’s content
# and two blank lines after each file’s content.

# Optional: clear previous TEMP.log (uncomment next line if you want fresh output each run)
# > TEMP.log

for file in *; do
    # Skip directories and files starting with TEMP
    if [[ -f "$file" && "$file" != TEMP* ]]; then
        echo "# File: $file" >> TEMP.log
        cat "$file" >> TEMP.log
        echo -e "\n\n" >> TEMP.log  # add two empty lines
    fi
done
