#!/usr/bin/env bash

# approved includes for go
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

if [[ "$filename" == *""_test.go ]]; then
    field=".TestImports"
else
    field=".Imports"
fi

go list -f "{{join ${field} \"\n\"}}" "${filename}" | while read -r package; do
    if array_contains "$package" "${approved[@]}"; then
        echo "OK: $package found in $filename" >> DEBUG
    else
        echo "FORBIDDEN: $package found in $filename" >> DEBUG
        # fail the test
        echo 0 > OUTPUT
        exit 1
    fi
done
