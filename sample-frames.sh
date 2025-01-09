#!/bin/bash

if [ "$#" -ne 2 ]; then
  echo "Usage: $0 <video_folder> <frames_folder>"
  exit 1
fi

video_folder=$1
frames_folder=$2
interval=1
count=0

if ! command -v ffmpeg &> /dev/null; then
  echo "Error: ffmpeg is not installed. Please install it and try again."
  exit 1
fi

total=$(ls "$video_folder"/*.mp4 2>/dev/null | wc -l)
if [ "$total" -eq 0 ]; then
  echo "No .mp4 files found in the video folder."
  exit 1
fi

for video_file in "$video_folder"/*.mp4; do

  extracted_id=$(basename "$video_file" | cut -d'_' -f1)
  

  mkdir -p "$frames_folder/$extracted_id"

  ffmpeg -i "$video_file" -vf "fps=1/$interval" "$frames_folder/$extracted_id/frame_%03d.png" > /dev/null 2>&1
  if [ $? -ne 0 ]; then
    echo "Error processing file: $video_file"
    continue
  fi

  count=$((count + 1))
  progress=$((count * 100 / total))
  echo "Progress: $progress%"
done

echo "Frame extraction completed for $count out of $total videos."
