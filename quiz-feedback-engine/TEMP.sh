#!/bin/bash

# TEMP.sh
# Append contents of all files in the current directory
# except files starting with "TEMP" to TEMP.log

for file in *; do
    # Skip directories and files starting with TEMP
    if [[ -f "$file" && "$file" != TEMP* ]]; then
        cat "$file" >> TEMP.log
    fi
done

