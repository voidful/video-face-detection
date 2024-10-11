from argparse import ArgumentParser
import face_recognition
import os
import json
from tqdm import tqdm
import cv2
import numpy as np
from scipy.cluster.hierarchy import linkage, fcluster
from scipy.spatial.distance import pdist
from collections import Counter
import shutil

TOLERANCE = 0.7
LOG_CLUSTER_IMG = False
BATCH_SIZE = 64
NUM_JITTERS = 1

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--frame_dir", required=True)
    parser.add_argument("--result_folder", required=True)
    parser.add_argument("--chunked_videos_dir", required=True)
    args = parser.parse_args()

    frame_dir = args.frame_dir
    result_folder = args.result_folder
    chunked_videos_dir = args.chunked_videos_dir
    results = []

    for video_folder in tqdm(os.listdir(frame_dir)):
        video_folder_path = os.path.join(frame_dir, video_folder)
        if not os.path.isdir(video_folder_path):
            continue

        N = len(os.listdir(video_folder_path))
        all_embs = []
        all_faces = []
        has_face = 0
        batch_img = []
        face_in_frames = []

        # Read images
        for frame_png in os.listdir(video_folder_path):
            image = face_recognition.load_image_file(os.path.join(video_folder_path, frame_png))
            image = np.ascontiguousarray(image[:, :, ::-1])
            batch_img.append(image)

        # Find face locations with GPU
        batch_of_face_locations = []
        for batch_i in range(0, len(batch_img), BATCH_SIZE):
            end = min(len(batch_img), batch_i + BATCH_SIZE)
            locations = face_recognition.batch_face_locations(batch_img[batch_i:end], number_of_times_to_upsample=0)
            batch_of_face_locations.extend(locations)

        # Encode the images into embeddings
        for frame_number_in_batch, face_locations in enumerate(batch_of_face_locations):
            face_areas = [(pos[2] - pos[0]) * (pos[1] - pos[3]) for pos in face_locations]
            face_areas = sorted(face_areas, reverse=True)

            # Background faces removal
            end_idx = len(face_areas)
            for i in range(len(face_areas)):
                if i + 1 < len(face_areas) and face_areas[i] / face_areas[i + 1] > 3:
                    end_idx = i + 1
                    break
            face_areas = face_areas[:end_idx]

            # Encode faces into embeddings
            face_embs = face_recognition.face_encodings(
                batch_img[frame_number_in_batch], known_face_locations=face_locations,
                num_jitters=NUM_JITTERS, model='large'
            )
            if len(face_areas) > 0:
                face_in_frames.append(len(face_areas))
            all_embs.extend(face_embs)

            if LOG_CLUSTER_IMG:
                for i in range(len(face_embs)):
                    pos = face_locations[i]
                    img = batch_img[frame_number_in_batch][pos[0]:pos[2], pos[3]:pos[1], :]
                    all_faces.append(img)
            if len(face_embs) > 0:
                has_face += 1

        if len(all_embs) == 0:
            face_prob = 0
            avg_num_faces = 0
        elif len(all_embs) == 1:
            face_prob = has_face / N
            avg_num_faces = 1.0
        else:
            # Run clustering
            distance_matrix = pdist(all_embs, metric='euclidean')
            Z = linkage(distance_matrix, method='complete')
            clusters = fcluster(Z, t=TOLERANCE, criterion='distance')

            counter = Counter(clusters)
            order_id = sorted(counter, key=counter.get, reverse=True)

            face_prob = round(has_face / N, 2)
            avg_num_faces = np.mean(face_in_frames)

        # Skip appending the result and remove the video folder if the condition is met
        if face_prob >= 0.7 and avg_num_faces <= 2:
            # Copy the video to the result folder if the condition is met
            chunked_video_path = os.path.join(chunked_videos_dir, video_folder)
            shutil.copytree(chunked_video_path, os.path.join(result_folder, video_folder))

            results.append([
                video_folder,  # video_id
                face_prob,  # face_prob
                [round(counter[i] / N, 2) for i in order_id],  # face_clusters
                avg_num_faces  # avg_num_faces
            ])

            if LOG_CLUSTER_IMG:
                for i in range(len(all_faces)):
                    cluster = clusters[i]
                    os.makedirs(f"debug/{cluster}/", exist_ok=True)
                    cv2.imwrite(f"debug/{cluster}/{i}.png", all_faces[i])

    with open('results.json', "w") as fout:
        json.dump(results, fout, indent=2, ensure_ascii=False)