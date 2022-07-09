#!/usr/bin/env bash

# approved includes
filename=$1
shift
approved=( "$@" )

array_contains () {
    local seeking=$1
    shift
    for element; do
        if [[ $element == "$seeking" ]]; then
            return 0
        fi
    done
    return 1
}

echo 100 > OUTPUT

grep -iPo '^\s*#include\s*(<|")\K(\.*/)*\w+(/\w+)*(\.\w+)?' -- "$filename" | cut -d : -f 2 | while read -r lib; do
    if array_contains "$lib" "${approved[@]}"; then
        echo "OK: $lib found in $filename" >> DEBUG
    else
        echo "FORBIDDEN: $lib found in $filename" >> DEBUG
        # fail the test
        echo 0 > OUTPUT
        exit 1
    fi
done
