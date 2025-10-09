#!/usr/bin/env bash

BASE_DIR="."

# Loop through every subfolder like 000/*/* (e.g., 000/040625-LundoBin/040625-LundoBin-All)
for scene_dir in "$BASE_DIR"/*/*; do
    if [ -d "$scene_dir" ]; then
        echo "🧹 Cleaning $scene_dir ..."

        # Remove sparse folder
        rm -rf "$scene_dir/sparse"

        # Remove database.db
        rm -f "$scene_dir/database.db"

        # Remove pose_log.txt
        rm -f "$scene_dir/pose_log.txt"

        # Remove transforms*.json
        rm -f "$scene_dir"/transforms*.json
    fi
done

echo "✅ Cleanup complete."
