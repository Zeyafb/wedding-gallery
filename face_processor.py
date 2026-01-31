"""
Face detection and clustering module
"""
import face_recognition
import numpy as np
from sklearn.cluster import DBSCAN
from typing import List, Dict, Tuple
import os
from PIL import Image
from io import BytesIO
import requests
import config


class FaceProcessor:
    """Handles face detection, encoding, and clustering"""

    def __init__(self):
        self.face_encodings = []
        self.face_locations = []
        self.photo_paths = []
        self.face_to_photo_map = []

    def load_images(self, folder_path: str = None) -> List[str]:
        """
        Load all image paths from the specified folder or storage backend

        Args:
            folder_path: Optional folder path (for local storage)

        Returns:
            List of image paths/URLs
        """
        # Use StorageManager for flexibility
        from storage_manager import StorageManager
        storage = StorageManager()

        return storage.list_photos()

    def detect_faces(self, image_paths: List[str], progress_callback=None) -> Dict:
        """
        Detect faces in all images and generate encodings

        Returns:
            Dict with face_encodings, face_locations, and face_to_photo_map
        """
        all_encodings = []
        all_locations = []
        face_to_photo = []

        total = len(image_paths)

        for idx, image_path in enumerate(image_paths):
            if progress_callback:
                progress_callback(idx, total, os.path.basename(image_path))

            try:
                # Load image (works with both local paths and URLs)
                if image_path.startswith('http'):
                    # Download from URL
                    import requests
                    from PIL import Image
                    import numpy as np
                    response = requests.get(image_path)
                    pil_image = Image.open(BytesIO(response.content))
                    image = np.array(pil_image)
                else:
                    # Load from local file
                    image = face_recognition.load_image_file(image_path)

                # Detect faces
                face_locations = face_recognition.face_locations(
                    image,
                    model=config.FACE_DETECTION_MODEL
                )

                # Generate encodings
                face_encodings = face_recognition.face_encodings(
                    image,
                    face_locations,
                    num_jitters=config.FACE_JITTERS
                )

                # Store results
                for encoding, location in zip(face_encodings, face_locations):
                    all_encodings.append(encoding)
                    all_locations.append(location)
                    face_to_photo.append({
                        'photo_path': image_path,
                        'location': location
                    })

            except Exception as e:
                print(f"Error processing {image_path}: {str(e)}")
                continue

        self.face_encodings = all_encodings
        self.face_locations = all_locations
        self.face_to_photo_map = face_to_photo

        return {
            'face_encodings': all_encodings,
            'face_to_photo_map': face_to_photo,
            'total_photos': total,
            'total_faces': len(all_encodings)
        }

    def cluster_faces(self, encodings: List) -> np.ndarray:
        """
        Cluster face encodings to group same people together

        Returns:
            Array of cluster labels for each face
        """
        if len(encodings) == 0:
            return np.array([])

        # Use DBSCAN clustering
        # eps corresponds to the max distance between faces in same cluster
        # Smaller eps = more strict clustering
        clustering = DBSCAN(
            eps=config.TOLERANCE,
            min_samples=1,  # Minimum faces to form a cluster
            metric='euclidean'
        ).fit(encodings)

        return clustering.labels_

    def get_person_clusters(self, cluster_labels: np.ndarray) -> Dict[int, List[int]]:
        """
        Organize faces by person (cluster)

        Returns:
            Dict mapping cluster_id -> list of face indices
        """
        person_clusters = {}

        for face_idx, cluster_id in enumerate(cluster_labels):
            if cluster_id not in person_clusters:
                person_clusters[cluster_id] = []
            person_clusters[cluster_id].append(face_idx)

        # Sort by cluster size (most photos first)
        person_clusters = dict(
            sorted(person_clusters.items(), key=lambda x: len(x[1]), reverse=True)
        )

        return person_clusters

    def extract_face_thumbnail(self, image_path: str, face_location: Tuple) -> Image.Image:
        """
        Extract face region from image and return as PIL Image

        Args:
            image_path: Path to the image file or URL
            face_location: Tuple of (top, right, bottom, left) coordinates
        """
        top, right, bottom, left = face_location

        # Load image with PIL (works with URLs and local paths)
        if image_path.startswith('http'):
            response = requests.get(image_path)
            image = Image.open(BytesIO(response.content))
        else:
            image = Image.open(image_path)

        # Add some padding around the face
        padding = 20
        top = max(0, top - padding)
        left = max(0, left - padding)
        bottom = min(image.height, bottom + padding)
        right = min(image.width, right + padding)

        # Crop face
        face_image = image.crop((left, top, right, bottom))

        # Resize to thumbnail size
        face_image.thumbnail((config.THUMBNAIL_SIZE, config.THUMBNAIL_SIZE), Image.Resampling.LANCZOS)

        return face_image
