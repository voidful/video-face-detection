from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
from argparse import ArgumentParser
from math import ceil, floor
import hashlib


def process_video_chunks(video_file, timestamp_file, output_directory):
    """
    Process video chunks based on timestamps and save them with hash-based names.
    :param video_file: Path to the video file
    :param timestamp_file: Path to the file containing timestamp data
    :param output_directory: Directory to save the output video files
    """
    # Generate hash ID for the video file
    video_id = video_file.split('/')[-1].split('.')[0]

    # Read and parse the timestamp file
    with open(timestamp_file, 'r') as f:
        chunks = f.readlines()
    chunks = [x.strip().split(',') for x in chunks]
    chunks = [x[2:] for x in chunks if x[0] == video_id]

    # Ensure the output directory ends with a slash
    if not output_directory.endswith('/'):
        output_directory += '/'

    # Process each timestamp chunk
    for i, chunk in enumerate(chunks):
        start_time, end_time = chunk
        start_time = floor(float(start_time))
        end_time = ceil(float(end_time))
        target_name = f'{output_directory}{video_id}_{i}.mp4'
        ffmpeg_extract_subclip(video_file, start_time, end_time, target_name)


def main(args):
    process_video_chunks(args.video_file, args.timestamp_file, args.output_directory)


if __name__ == '__main__':
    parser = ArgumentParser(
        description="Extract video subclips based on timestamps and save them with hash-based names.")
    parser.add_argument('--video_file', required=True, help="Path to the input video file.")
    parser.add_argument('--timestamp_file', required=True, help="Path to the timestamp file.")
    parser.add_argument('--output_directory', required=True, help="Directory to save the output video files.")
    args = parser.parse_args()
    main(args)
