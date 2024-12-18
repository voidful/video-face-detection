import hashlib
from argparse import ArgumentParser
from moviepy.editor import *

def generate_hash_id(file_path):
    """
    Generate a hash ID from the given file path.
    :param file_path: Path to the input file
    :return: Hash ID as a string
    """
    hash_object = hashlib.md5(file_path.encode('utf-8'))
    return hash_object.hexdigest()[:10]  # Truncate to 10 characters for brevity

def process_video(input_path, output_directory):
    """
    Extract audio from a video file and save it as an MP3 file with a hash ID.
    :param input_path: Path to the input video file
    :param output_directory: Directory to save the output MP3 file
    :raises: ValueError if the input file format is unsupported
    """
    if not input_path.lower().endswith('.mp4'):
        raise ValueError("Only .mp4 format is supported.")

    # Generate a unique hash ID for the file
    hash_id = generate_hash_id(input_path)

    # Ensure the output directory ends with a slash
    if not output_directory.endswith('/'):
        output_directory += '/'

    output_path = f"{output_directory}{hash_id}.mp3"

    # Process video and extract audio
    with VideoFileClip(input_path) as video_clip:
        video_clip.audio.write_audiofile(output_path, codec='libmp3lame')

def main(args):
    process_video(args.input_path, args.output_directory)

if __name__ == '__main__':
    parser = ArgumentParser(description="Extract audio from a video file and save it as MP3.")
    parser.add_argument('--input_path', required=True, help="Path to the input video file (.mp4 format only).")
    parser.add_argument('--output_directory', required=True, help="Directory to save the output MP3 file.")
    args = parser.parse_args()
    main(args)
