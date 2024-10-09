video_folder=$1
frames_folder=$2
count=0

for video_file in "$video_folder"/*.mp4; do
  # Extract the video ID from the filename (before the first underscore)
  extracted_id=$(basename "$video_file" | cut -d'_' -f1)
  
  # Create folder for extracted frames
  mkdir -p "$frames_folder/$extracted_id"
  
  # Extract a frame every 5 seconds
  ffmpeg -i "$video_file" -vf "fps=1/5" "$frames_folder/$extracted_id/frame_%03d.png" > /dev/null 2>&1

  # Print progress
  count=$((count + 1))
  if (( count % 10 == 0 )); then
    echo "progress: $((count / 10))0%"
  fi
done
