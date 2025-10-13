#!/bin/bash

# Main function
main() {
    local file_name="$1"
    local -r static="src/meitav_view/static"
    # Check if file_name is provided
    if [[ -z "$file_name" ]]; then
        echo "Usage: $0 <file_name>"
        exit 1
    fi
    
    mkdir -p $static/js $static/css

    while IFS=',' read -r url dest; do
        dest_path="$static/$dest"
        echo $dest_path
        curl -L -o "$dest_path" "$url"
        # Check if the download was successful
        if [[ $? -eq 0 ]]; then
            echo "Downloaded $url to $dest_path"
        else
            echo "Failed to download $url"
        fi
    done < "$file_name"
}

# Run the main function with the first argument as the file_name
main "$1"
