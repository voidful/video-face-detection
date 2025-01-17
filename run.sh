# run.sh
#! /usr/env/bash

video_folder=$1
result_folder=$2

shopt -s nullglob

for video_file in $video_folder/*.mp4; do
  if [[ ! -f "$video_file" ]]; then
    continue
  fi

  # Step 1: Extract audio and run VAD
  mkdir temp
  echo "Processing $video_file"
  python3 extract.py --input_path "$video_file" --output_directory "temp"
  echo "Extracted audio from $video_file"
  python3 vad.py --audio_directory "temp" --output_file "timestamps.csv"

  # Step 2: Chunk the video based on VAD timestamps
  mkdir -p chunked_videos
  echo "Chunking $video_file"
  python3 chunking.py --video_file "$video_file" --timestamp_file "timestamps.csv" --output_directory "chunked_videos"

  mkdir frames_folder
  # Step 3: Sample frames from the chunked videos
  echo "Extracting frames from $video_file"
  for chunked_video in chunked_videos/*.mp4; do
    extracted_id=$(python3 -c "$chunked_video.split('/')[-1].split('.')[0]")
    echo "Extracting frames for $extracted_id"
    mkdir -p "frames_folder/$extracted_id"
    ffmpeg -i "$chunked_video" -vf "fps=1/5" "frames_folder/$extracted_id/frame_%03d.png" > /dev/null 2>&1
  done

  mkdir -p $result_folder
  # Step 4: Run the main Python script
  echo "Running main script for $video_file"
  python3 main.py --frame_dir "frames_folder" --result_folder "$result_folder" --chunked_videos_dir "chunked_videos"

  rm -rf temp
  rm -rf chunked_videos
  rm -rf frames_folder
  rm -rf stimestamps.csv

done