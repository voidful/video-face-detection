# extract.py
import argparse
from moviepy.editor import VideoFileClip


def main(args):
    extracted_id = args.input_path.split('/')[-1].split('.')[0]
    print("extract.py", extracted_id)
    if not args.input_path.endswith('.mp4'):
        raise IOError('Format not supported')
    with VideoFileClip(args.input_path) as video_clip:
        video_clip.audio.write_audiofile((args.output_directory if args.output_directory.endswith(
            '/') else args.output_directory + '/') + extracted_id + '.mp3')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_path', required=True)
    parser.add_argument('--output_directory', required=True)
    args = parser.parse_args()
    main(args)
