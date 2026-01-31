"""
Configuration settings for the wedding photo gallery app
"""
import os

# =============================================================================
# STORAGE BACKEND CONFIGURATION
# =============================================================================
# Options: 'local', 'cloudinary', 's3'
STORAGE_BACKEND = "cloudinary"

# -----------------------------------------------------------------------------
# LOCAL STORAGE (for testing locally)
# -----------------------------------------------------------------------------
PHOTOS_FOLDER = "wedding_photos"  # CHANGE THIS to your local wedding photos folder

# -----------------------------------------------------------------------------
# CLOUDINARY STORAGE (RECOMMENDED for deployment - free 25GB)
# -----------------------------------------------------------------------------
# Sign up at https://cloudinary.com
CLOUDINARY_CLOUD_NAME = "dwt17ikflb"  # Your Cloudinary cloud name
CLOUDINARY_FOLDER = "wedding-photos"  # Folder name in Cloudinary
CLOUDINARY_URL_LIST_FILE = "cloudinary_urls.txt"  # URL list file

# -----------------------------------------------------------------------------
# AWS S3 STORAGE (for production deployments)
# -----------------------------------------------------------------------------
S3_BUCKET_NAME = "your-bucket-name"
S3_FOLDER = "wedding-photos"
S3_REGION = "us-east-1"
S3_BASE_URL = f"https://{S3_BUCKET_NAME}.s3.{S3_REGION}.amazonaws.com"

# =============================================================================
# CACHE & PROCESSING SETTINGS
# =============================================================================
CACHE_FILE = "face_embeddings_cache.pkl"

# Face detection settings
FACE_DETECTION_MODEL = "hog"  # 'hog' is faster, 'cnn' is more accurate but requires GPU
FACE_JITTERS = 1  # Number of times to re-sample face for encoding (higher = more accurate but slower)
TOLERANCE = 0.6  # Lower is more strict for face matching (0.6 is default)

# =============================================================================
# UI SETTINGS
# =============================================================================
THUMBNAIL_SIZE = 100  # Size of face thumbnails in pixels
GRID_COLUMNS = 4  # Number of columns in photo grid
MAX_DISPLAY_WIDTH = 800  # Max width for displayed photos

# Supported image extensions
IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp', '.bmp'}
