#!/bin/bash

# Script to find TODOs across multiple GitHub repositories
# Creates a markdown report of all found TODOs

OUTPUT_FILE="todos.md"

# Initialize the output file with a header
echo "# TODOs Across GitHub Repositories" > $OUTPUT_FILE
echo "Generated on $(date)" >> $OUTPUT_FILE
echo "" >> $OUTPUT_FILE

# Find all git repositories in the current directory
REPOS=$(find . -maxdepth 2 -name ".git" -type d | sed 's/\/.git//')

# For each repository
for REPO in $REPOS; do
    REPO_NAME=$(basename "$REPO")
    TODO_COUNT=0
    
    echo "Scanning $REPO_NAME..."
    
    # Create a temporary file to store TODOs for this repo
    TEMP_FILE=$(mktemp)
    
    # Find TODOs in the repository, excluding .git directory and binary files
    find "$REPO" -type f -not -path "*/\.git/*" -not -path "*/node_modules/*" -not -path "*/build/*" -not -path "*/dist/*" | while read -r FILE; do
        # Skip binary files
        if file "$FILE" | grep -q "text"; then
            # Look for TODO comments in the file
            TODOS=$(grep -n -i "TODO\|FIXME\|XXX" "$FILE" 2>/dev/null)
            
            if [ ! -z "$TODOS" ]; then
                # Get the relative path within the repository
                REL_PATH=$(realpath --relative-to="$REPO" "$FILE")
                
                # Append to temp file
                echo "### $REL_PATH" >> "$TEMP_FILE"
                
                # Process each TODO
                echo "$TODOS" | while read -r TODO; do
                    LINE_NUM=$(echo "$TODO" | cut -d':' -f1)
                    TODO_TEXT=$(echo "$TODO" | cut -d':' -f2-)
                    
                    # Clean up the TODO text
                    TODO_TEXT=$(echo "$TODO_TEXT" | sed -e 's/^[[:space:]]*\/\/[[:space:]]*//' -e 's/^[[:space:]]*#[[:space:]]*//' -e 's/^[[:space:]]*\/\*[[:space:]]*//' -e 's/^[[:space:]]*\*[[:space:]]*//')
                    
                    echo "- Line $LINE_NUM: $TODO_TEXT" >> "$TEMP_FILE"
                    ((TODO_COUNT++))
                done
                
                echo "" >> "$TEMP_FILE"
            fi
        fi
    done
    
    # If TODOs were found, add them to the main output file
    if [ $TODO_COUNT -gt 0 ]; then
        echo "## $REPO_NAME ($TODO_COUNT TODOs)" >> $OUTPUT_FILE
        cat "$TEMP_FILE" >> $OUTPUT_FILE
        echo "" >> $OUTPUT_FILE
    fi
    
    # Clean up temporary file
    rm "$TEMP_FILE"
done

echo "Done! TODOs have been saved to $OUTPUT_FILE"