#!/bin/bash

# Main function
main() {
    local file_name="$1"
    
    # Check if file_name is provided
    if [[ -z "$file_name" ]]; then
        echo "Usage: $0 <file_name>"
        exit 1
    fi
    
    # Create directories if they don't exist
    mkdir -p static/js static/css

    # Read the file line by line
    while IFS= read -r url; do
        # Check if URL is for JS or CSS based on extension
        if [[ "$url" == *.js ]]; then
            dest_folder="static/js"
        elif [[ "$url" == *.css ]]; then
            dest_folder="static/css"
        elif [[ "$url" == *. ]]
        else
            echo "Skipping unsupported file type for URL: $url"
            continue
        fi
        
        # Get the filename from the URL
        file_name=$(basename "$url")
        dest_path="$dest_folder/$file_name"
        
        # Check if the file already exists
        if [[ -f "$dest_path" ]]; then
            echo "File $dest_path already exists, skipping download."
            continue
        fi

        # Download the file to the appropriate folder
        curl -o "$dest_path" "$url"
        
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
