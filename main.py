from argparse import ArgumentParser
import os
import json
from tqdm import tqdm
from face_recognition import load_image_file, batch_face_locations, face_encodings
from scipy.cluster.hierarchy import linkage, fcluster
from scipy.spatial.distance import pdist
from collections import Counter
import numpy as np
import shutil

TOLERANCE = 0.7
LOG_CLUSTER_IMG = False
BATCH_SIZE = 1
NUM_JITTERS = 1

def load_images_from_folder(folder_path):
    """Load images from a given folder."""
    images = []
    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)
        if os.path.isfile(file_path):
            image = load_image_file(file_path)
            images.append(np.ascontiguousarray(image[:, :, ::-1]))
    return images

def detect_faces_in_batches(images):
    """Detect faces in batches using GPU acceleration."""
    face_locations = []
    for i in range(0, len(images), BATCH_SIZE):
        batch = images[i:i + BATCH_SIZE]
        face_locations.extend(batch_face_locations(batch, number_of_times_to_upsample=0))
    return face_locations

def encode_faces(images, face_locations):
    """Encode face locations into embeddings."""
    embeddings = []
    face_areas = []
    for i, locations in enumerate(face_locations):
        areas = [(pos[2] - pos[0]) * (pos[1] - pos[3]) for pos in locations]
        areas.sort(reverse=True)
        end_idx = next((j + 1 for j in range(len(areas) - 1) if areas[j] / areas[j + 1] > 3), len(areas))
        face_areas.append(areas[:end_idx])
        embeddings.extend(face_encodings(images[i], known_face_locations=locations[:end_idx], num_jitters=NUM_JITTERS, model='large'))
    return embeddings, face_areas

def cluster_faces(embeddings, tolerance):
    """Cluster face embeddings."""
    if len(embeddings) <= 1:
        return None, []
    distance_matrix = pdist(embeddings, metric='euclidean')
    Z = linkage(distance_matrix, method='complete')
    clusters = fcluster(Z, t=tolerance, criterion='distance')
    return clusters, Counter(clusters)

def process_video_folder(args):
    """Process a single video folder."""
    video_folder_path, chunked_videos_dir, result_folder = args
    images = load_images_from_folder(video_folder_path)
    if not images:
        return None

    face_locations = detect_faces_in_batches(images)
    embeddings, face_areas = encode_faces(images, face_locations)

    face_prob = len([a for a in face_areas if a]) / len(images)
    avg_num_faces = np.mean([len(a) for a in face_areas]) if face_areas else 0

    clusters, cluster_counter = cluster_faces(embeddings, TOLERANCE)
    if face_prob >= 0.7 and 1.8 <= avg_num_faces <= 2.2:
        video_id = os.path.basename(video_folder_path)
        chunked_video_path = os.path.join(chunked_videos_dir, video_id)
        shutil.copy(chunked_video_path, os.path.join(result_folder, video_id))
        return {
            "video_id": video_id,
            "face_prob": face_prob,
            "face_clusters": [round(cluster_counter[c] / len(images), 2) for c in sorted(cluster_counter, key=cluster_counter.get, reverse=True)],
            "avg_num_faces": avg_num_faces
        }
    return None

def main(args):
    os.makedirs(args.result_folder, exist_ok=True)
    os.makedirs(args.frame_dir, exist_ok=True)
    os.makedirs(args.chunked_videos_dir, exist_ok=True)
    video_folders = [
        (os.path.join(args.frame_dir, folder), args.chunked_videos_dir, args.result_folder)
        for folder in os.listdir(args.frame_dir)
        if os.path.isdir(os.path.join(args.frame_dir, folder))
    ]

    results = []
    for video_folder in tqdm(video_folders, desc=f"Processing video folders"):
        result = process_video_folder(video_folder)
        if result is not None:
            results.append(result)

    with open('results.json', 'w') as fout:
        json.dump(results, fout, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    parser = ArgumentParser(description="Process video frames to detect faces and save results.")
    parser.add_argument("--frame_dir", required=True, help="Directory containing frame folders for videos.")
    parser.add_argument("--result_folder", required=True, help="Folder to save results.")
    parser.add_argument("--chunked_videos_dir", required=True, help="Directory containing chunked video files.")
    args = parser.parse_args()
    main(args)
