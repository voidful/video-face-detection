from silero_vad import load_silero_vad, read_audio, get_speech_timestamps
from argparse import ArgumentParser
from typing import List, Tuple
import os

SAMPLING_RATE = 16000
NEIGHBOR_THRESHOLD = 3  # seconds
MIN_DURATION = 15  # seconds


def load_audio_files(directory: str, extension: str = '.mp3') -> List[str]:
    """Load audio file paths with the specified extension from a directory."""
    return [os.path.join(directory, file) for file in os.listdir(directory) if file.endswith(extension)]


def process_audio_file(file_path: str, model, neighbor_threshold: int, min_duration: int) -> List[Tuple[float, float]]:
    """Process an audio file to extract and merge speech timestamps."""
    audio = read_audio(file_path)
    speech_timestamps = get_speech_timestamps(audio, model)

    # Convert timestamps from samples to seconds
    raw_chunks = [(chunk['start'] / SAMPLING_RATE, chunk['end'] / SAMPLING_RATE) for chunk in speech_timestamps]

    # Merge adjacent chunks if they are within the threshold
    merged_chunks = []
    if raw_chunks:
        current_chunk = raw_chunks[0]
        for next_chunk in raw_chunks[1:]:
            if next_chunk[0] - current_chunk[1] <= neighbor_threshold:
                current_chunk = (current_chunk[0], next_chunk[1])
            else:
                merged_chunks.append(current_chunk)
                current_chunk = next_chunk
        merged_chunks.append(current_chunk)

    # Filter out chunks that are shorter than the minimum duration
    return [(start, end) for start, end in merged_chunks if end - start >= min_duration]


def write_results(output_file: str, results: List[Tuple[str, int, float, float]]) -> None:
    """Write the processed results to a file."""
    with open(output_file, 'a') as f:
        for result in results:
            video_id, index, start_time, end_time = result
            print(f"{video_id},{index},{start_time},{end_time}", file=f)


def main(args):
    model = load_silero_vad(onnx=True)
    audio_files = load_audio_files(args.audio_directory)
    all_results = []

    for file_path in audio_files:
        file_name = os.path.basename(file_path)
        extracted_id = os.path.splitext(file_name)[0]
        chunks = process_audio_file(file_path, model, NEIGHBOR_THRESHOLD, MIN_DURATION)
        all_results.extend([(extracted_id, i, start, end) for i, (start, end) in enumerate(chunks)])

    write_results(args.output_file, all_results)


if __name__ == '__main__':
    parser = ArgumentParser(description="Process audio files to extract speech timestamps and save results.")
    parser.add_argument('--audio_directory', required=True, help="Directory containing audio files.")
    parser.add_argument('--output_file', required=True, help="Output file to save the speech timestamp results.")
    args = parser.parse_args()
    main(args)
