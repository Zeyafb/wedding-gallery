"""
Cache manager for storing and loading face detection results
"""
import pickle
import os
from typing import Dict, Optional
import config


class CacheManager:
    """Manages caching of face embeddings and metadata"""

    def __init__(self, cache_file: str = config.CACHE_FILE):
        self.cache_file = cache_file

    def save_cache(self, data: Dict) -> bool:
        """
        Save face detection data to cache file

        Args:
            data: Dictionary containing face_encodings, face_to_photo_map, etc.

        Returns:
            True if successful, False otherwise
        """
        try:
            with open(self.cache_file, 'wb') as f:
                pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)
            return True
        except Exception as e:
            print(f"Error saving cache: {str(e)}")
            return False

    def load_cache(self) -> Optional[Dict]:
        """
        Load face detection data from cache file

        Returns:
            Dictionary with cached data or None if cache doesn't exist/is invalid
        """
        if not os.path.exists(self.cache_file):
            return None

        try:
            with open(self.cache_file, 'rb') as f:
                data = pickle.load(f)
            return data
        except Exception as e:
            print(f"Error loading cache: {str(e)}")
            return None

    def is_cache_valid(self, folder_path: str) -> bool:
        """
        Check if cache is still valid (no new/deleted photos)

        Args:
            folder_path: Path to photos folder

        Returns:
            True if cache is valid, False otherwise
        """
        cache_data = self.load_cache()
        if cache_data is None:
            return False

        # Get current photos
        try:
            current_photos = set()
            for filename in os.listdir(folder_path):
                ext = os.path.splitext(filename)[1].lower()
                if ext in config.IMAGE_EXTENSIONS:
                    current_photos.add(os.path.join(folder_path, filename))
        except Exception:
            return False

        # Get cached photos
        cached_photos = set()
        for face_info in cache_data.get('face_to_photo_map', []):
            cached_photos.add(face_info['photo_path'])

        # Cache is valid if photo sets match
        return current_photos == cached_photos

    def clear_cache(self) -> bool:
        """
        Delete the cache file

        Returns:
            True if successful, False otherwise
        """
        try:
            if os.path.exists(self.cache_file):
                os.remove(self.cache_file)
            return True
        except Exception as e:
            print(f"Error clearing cache: {str(e)}")
            return False
