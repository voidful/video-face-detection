from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
from argparse import ArgumentParser
from math import ceil, floor
import re

id_reg = re.compile(r'(\d+)\.|(?=\.\w+$)|\[(.*?)\](?!.*\[[^\[\]]*\])')


def main(args):
    extracted_id = re.search(id_reg, args.video_file).group()[1:-1]
    with open(args.timestamp_file, 'r') as f:
        chunks = f.readlines()
    chunks = [x.strip().split(',') for x in chunks]
    chunks = [x[2:] for x in chunks if x[0] == extracted_id]

    # Ensure the output directory ends with a slash
    output_dir = args.output_directory
    if not output_dir.endswith('/'):
        output_dir += '/'

    for i, chunk in enumerate(chunks):
        start_time, end_time = chunk
        start_time = floor(float(start_time))
        end_time = ceil(float(end_time))
        target_name = f'{output_dir}{extracted_id}_{i}.mp4'
        ffmpeg_extract_subclip(args.video_file, start_time, end_time, target_name)


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--video_file', required=True)
    parser.add_argument('--timestamp_file', required=True)
    parser.add_argument('--output_directory', required=True)
    args = parser.parse_args()
    main(args)
