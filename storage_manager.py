"""
Storage manager for handling different photo storage backends
Supports: local, Cloudinary, AWS S3
"""
import os
from typing import List, Optional
import config
from io import BytesIO
import requests


class StorageManager:
    """Handles photo loading from different storage backends"""

    def __init__(self, backend: str = None):
        self.backend = backend or config.STORAGE_BACKEND
        self._cloudinary_client = None
        self._s3_client = None

    def list_photos(self) -> List[str]:
        """
        List all photo paths/URLs from the configured storage backend

        Returns:
            List of photo paths (local) or URLs (cloud)
        """
        if self.backend == "local":
            return self._list_local_photos()
        elif self.backend == "cloudinary":
            return self._list_cloudinary_photos()
        elif self.backend == "s3":
            return self._list_s3_photos()
        else:
            raise ValueError(f"Unsupported storage backend: {self.backend}")

    def load_image(self, photo_path: str):
        """
        Load an image from storage

        Args:
            photo_path: Path (local) or URL (cloud)

        Returns:
            PIL Image or numpy array compatible with face_recognition
        """
        if self.backend == "local":
            # Return path as-is for face_recognition.load_image_file()
            return photo_path
        else:
            # For cloud storage, download to temp location or return BytesIO
            return self._download_image(photo_path)

    def get_display_url(self, photo_path: str) -> str:
        """
        Get a URL suitable for displaying in Streamlit

        Args:
            photo_path: Path (local) or URL (cloud)

        Returns:
            URL or local path
        """
        if self.backend == "local":
            return photo_path
        else:
            # Cloud URLs are already display-ready
            return photo_path

    # =========================================================================
    # LOCAL STORAGE
    # =========================================================================

    def _list_local_photos(self) -> List[str]:
        """List photos from local folder"""
        folder_path = config.PHOTOS_FOLDER
        image_paths = []

        if not os.path.exists(folder_path):
            raise ValueError(f"Folder not found: {folder_path}")

        for filename in os.listdir(folder_path):
            ext = os.path.splitext(filename)[1].lower()
            if ext in config.IMAGE_EXTENSIONS:
                image_paths.append(os.path.join(folder_path, filename))

        return sorted(image_paths)

    # =========================================================================
    # CLOUDINARY STORAGE
    # =========================================================================

    def _get_cloudinary_client(self):
        """Initialize Cloudinary client (lazy loading)"""
        if self._cloudinary_client is None:
            try:
                import cloudinary
                import cloudinary.api

                cloudinary.config(
                    cloud_name=config.CLOUDINARY_CLOUD_NAME,
                    api_key=os.environ.get('CLOUDINARY_API_KEY', ''),
                    api_secret=os.environ.get('CLOUDINARY_API_SECRET', ''),
                    secure=True
                )
                self._cloudinary_client = cloudinary
            except ImportError:
                raise ImportError(
                    "Cloudinary not installed. Run: pip install cloudinary"
                )

        return self._cloudinary_client

    def _list_cloudinary_photos(self) -> List[str]:
        """
        List photos from Cloudinary

        First tries to load from URL list file (no API keys needed!)
        Falls back to API if URL list doesn't exist
        """
        # Try loading from URL list file first (no API keys needed!)
        url_list_file = getattr(config, 'CLOUDINARY_URL_LIST_FILE', 'cloudinary_urls.txt')
        if os.path.exists(url_list_file):
            print(f"Loading photo URLs from {url_list_file}...")
            with open(url_list_file, 'r') as f:
                urls = [line.strip() for line in f if line.strip()]
            return sorted(urls)

        # Fallback to API if URL list doesn't exist
        try:
            cloudinary = self._get_cloudinary_client()

            # List all images in the folder
            result = cloudinary.api.resources(
                type="upload",
                prefix=config.CLOUDINARY_FOLDER,
                max_results=500  # Adjust if you have more photos
            )

            # Extract URLs
            photo_urls = [resource['secure_url'] for resource in result['resources']]
            return sorted(photo_urls)

        except Exception as e:
            # Fallback: If you have a pre-generated list of URLs
            print(f"Error listing Cloudinary photos: {e}")
            print("Tip: Generate cloudinary_urls.txt using generate_urls_simple.py")
            return []

    # =========================================================================
    # AWS S3 STORAGE
    # =========================================================================

    def _get_s3_client(self):
        """Initialize S3 client (lazy loading)"""
        if self._s3_client is None:
            try:
                import boto3

                self._s3_client = boto3.client(
                    's3',
                    region_name=config.S3_REGION,
                    aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID', ''),
                    aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY', '')
                )
            except ImportError:
                raise ImportError(
                    "boto3 not installed. Run: pip install boto3"
                )

        return self._s3_client

    def _list_s3_photos(self) -> List[str]:
        """List photos from AWS S3 bucket"""
        s3 = self._get_s3_client()

        try:
            response = s3.list_objects_v2(
                Bucket=config.S3_BUCKET_NAME,
                Prefix=config.S3_FOLDER
            )

            photo_urls = []
            for obj in response.get('Contents', []):
                key = obj['Key']
                ext = os.path.splitext(key)[1].lower()

                if ext in config.IMAGE_EXTENSIONS:
                    # Construct public URL
                    url = f"{config.S3_BASE_URL}/{key}"
                    photo_urls.append(url)

            return sorted(photo_urls)

        except Exception as e:
            print(f"Error listing S3 photos: {e}")
            return []

    # =========================================================================
    # UTILITY METHODS
    # =========================================================================

    def _download_image(self, url: str) -> BytesIO:
        """
        Download image from URL to BytesIO for face_recognition

        Args:
            url: Image URL

        Returns:
            BytesIO buffer with image data
        """
        response = requests.get(url)
        response.raise_for_status()
        return BytesIO(response.content)


# =============================================================================
# SIMPLE URL LIST APPROACH (No API keys needed)
# =============================================================================

class SimpleCloudinaryStorage:
    """
    Simplified Cloudinary storage that uses pre-generated URL list
    No API keys needed for deployment!
    """

    def __init__(self, url_list_file: str = "cloudinary_urls.txt"):
        self.url_list_file = url_list_file

    def list_photos(self) -> List[str]:
        """Load photo URLs from text file"""
        if not os.path.exists(self.url_list_file):
            print(f"URL list file not found: {self.url_list_file}")
            return []

        with open(self.url_list_file, 'r') as f:
            urls = [line.strip() for line in f if line.strip()]

        return urls

    def get_display_url(self, photo_url: str) -> str:
        """URLs are already ready for display"""
        return photo_url
