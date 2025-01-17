# run.sh
#! /usr/env/bash

video_folder=$1
result_folder=$2

shopt -s nullglob

for video_file in $video_folder/*.mp4; do
  if [[ ! -f "$video_file" ]]; then
    continue
  fi

  # Generate a unique hash for the temp directory
  temp_dir=$(python3 -c "import hashlib, time, random; print(hashlib.md5(f'{time.time()}{random.random()}'.encode()).hexdigest())")
  mkdir $temp_dir

  # Step 1: Extract audio and run VAD
  echo "Processing $video_file"
  python3 extract.py --input_path "$video_file" --output_directory "$temp_dir"
  echo "Extracted audio from $video_file"
  python3 vad.py --audio_directory "$temp_dir" --output_file "$temp_dir/timestamps.csv"

  # Step 2: Chunk the video based on VAD timestamps
  chunked_videos_dir="$temp_dir/chunked_videos"
  mkdir -p $chunked_videos_dir
  echo "Chunking $video_file"
  python3 chunking.py --video_file "$video_file" --timestamp_file "$temp_dir/timestamps.csv" --output_directory "$chunked_videos_dir"

  frames_folder="$temp_dir/frames_folder"
  mkdir $frames_folder
  # Step 3: Sample frames from the chunked videos
  echo "Extracting frames from $video_file"
  for chunked_video in $chunked_videos_dir/*.mp4; do
    extracted_id=$(python3 -c "print('$chunked_video'.split('/')[-1].split('.')[0])")
    echo "Extracting frames for $extracted_id"
    mkdir -p "$frames_folder/$extracted_id"
    ffmpeg -i "$chunked_video" -vf "fps=1/5" "$frames_folder/$extracted_id/frame_%03d.png" > /dev/null 2>&1
  done

  mkdir -p $result_folder
  # Step 4: Run the main Python script
  echo "Running main script for $video_file"
  python3 main.py --frame_dir "$frames_folder" --result_folder "$result_folder" --chunked_videos_dir "$chunked_videos_dir"

  # Remove the temporary directory
  rm -rf $temp_dir
done