"""
Local Face Processing Script
Run this ONCE on your Windows machine to generate the face cache
"""
import requests
from PIL import Image
from io import BytesIO
import pickle
import numpy as np
import face_recognition
from sklearn.cluster import DBSCAN
import os

print("=" * 70)
print("Local Face Processing for Wedding Gallery")
print("=" * 70)
print()

# Load Cloudinary URLs
print("Loading photo URLs from cloudinary_urls.txt...")
with open('cloudinary_urls.txt', 'r') as f:
    photo_urls = [line.strip() for line in f if line.strip()]

print(f"Found {len(photo_urls)} photos to process")
print()

# Process faces
all_encodings = []
all_locations = []
face_to_photo_map = []

print("Processing faces from Cloudinary photos...")
print("This will take about 10-15 minutes for 430 photos")
print()

for idx, photo_url in enumerate(photo_urls):
    print(f"[{idx + 1}/{len(photo_urls)}] Processing: {os.path.basename(photo_url)}...", end=" ")

    try:
        # Download photo from Cloudinary
        response = requests.get(photo_url, timeout=30)
        response.raise_for_status()

        # Load image
        pil_image = Image.open(BytesIO(response.content))
        image = np.array(pil_image)

        # Detect faces
        face_locations = face_recognition.face_locations(image, model="hog")

        # Generate encodings
        face_encodings = face_recognition.face_encodings(
            image,
            face_locations,
            num_jitters=1
        )

        # Store results
        for encoding, location in zip(face_encodings, face_locations):
            all_encodings.append(encoding)
            all_locations.append(location)
            face_to_photo_map.append({
                'photo_path': photo_url,  # Cloudinary URL
                'location': location
            })

        print(f"OK - Found {len(face_encodings)} faces")

    except Exception as e:
        print(f"ERROR: {str(e)}")
        continue

print()
print(f"Total faces detected: {len(all_encodings)}")
print()

# Cluster faces by person
print("Clustering faces by person...")
if len(all_encodings) > 0:
    clustering = DBSCAN(
        eps=0.6,  # Matching tolerance
        min_samples=1,
        metric='euclidean'
    ).fit(all_encodings)

    cluster_labels = clustering.labels_

    # Count unique people
    unique_people = len(set(cluster_labels))
    print(f"Found {unique_people} unique people")
else:
    cluster_labels = np.array([])
    print("No faces detected!")

print()

# Save cache
cache_data = {
    'face_encodings': all_encodings,
    'face_to_photo_map': face_to_photo_map,
    'cluster_labels': cluster_labels.tolist(),
    'total_photos': len(photo_urls),
    'total_faces': len(all_encodings)
}

cache_file = 'face_embeddings_cache.pkl'
print(f"Saving cache to {cache_file}...")
with open(cache_file, 'wb') as f:
    pickle.dump(cache_data, f, protocol=pickle.HIGHEST_PROTOCOL)

file_size = os.path.getsize(cache_file) / (1024 * 1024)  # MB
print(f"Cache file created: {file_size:.1f} MB")
print()

print("=" * 70)
print("SUCCESS!")
print("=" * 70)
print()
print("Next steps:")
print("1. Commit and push the cache file to GitHub:")
print("   git add face_embeddings_cache.pkl")
print("   git commit -m 'Add pre-processed face cache'")
print("   git push")
print()
print("2. Your Streamlit app will now deploy instantly with face filtering!")
print()
