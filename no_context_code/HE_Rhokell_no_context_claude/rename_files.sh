#!/bin/bash

# Rename all HumanEval_*.rhok files to *.rhk format
for file in HumanEval_*.rhok; do
  if [ -f "$file" ]; then
    # Extract the task number
    task_num=$(echo "$file" | sed 's/HumanEval_\([0-9]*\)\.rhok/\1/')
    # Create the new filename
    new_name="${task_num}.rhk"
    # Rename the file
    mv "$file" "$new_name"
    echo "Renamed $file to $new_name"
  fi
done
