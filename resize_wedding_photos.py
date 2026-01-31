"""
Resize wedding photos for Cloudinary upload
Reduces file size while maintaining quality for web display
"""
from PIL import Image
import os
from pathlib import Path

# =============================================================================
# CONFIGURATION
# =============================================================================
SOURCE_FOLDER = r"D:\Fayez & Kyla Final Wedding"
OUTPUT_FOLDER = r"D:\Fayez & Kyla Final Wedding - Resized"

# Resize settings
MAX_DIMENSION = 2000  # Max width or height in pixels (plenty for web)
JPEG_QUALITY = 85      # Quality (85 is great balance of quality/size)
TARGET_SIZE_MB = 5     # Target max file size in MB

# =============================================================================

def resize_image(input_path, output_path):
    """Resize and compress a single image"""
    try:
        # Open image
        img = Image.open(input_path)

        # Convert RGBA to RGB if needed (for PNG images)
        if img.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = background

        # Get current dimensions
        width, height = img.size

        # Calculate new dimensions (maintain aspect ratio)
        if width > height:
            if width > MAX_DIMENSION:
                new_width = MAX_DIMENSION
                new_height = int(height * (MAX_DIMENSION / width))
            else:
                new_width, new_height = width, height
        else:
            if height > MAX_DIMENSION:
                new_height = MAX_DIMENSION
                new_width = int(width * (MAX_DIMENSION / height))
            else:
                new_width, new_height = width, height

        # Resize image
        if (new_width, new_height) != (width, height):
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

        # Save with compression
        img.save(
            output_path,
            'JPEG',
            quality=JPEG_QUALITY,
            optimize=True,
            progressive=True
        )

        # Get file sizes
        original_size = os.path.getsize(input_path) / (1024 * 1024)  # MB
        new_size = os.path.getsize(output_path) / (1024 * 1024)  # MB

        return True, original_size, new_size

    except Exception as e:
        return False, 0, 0, str(e)


def main():
    """Process all wedding photos"""

    print("=" * 70)
    print("Wedding Photo Resizer for Cloudinary")
    print("=" * 70)
    print()

    # Check if source folder exists
    if not os.path.exists(SOURCE_FOLDER):
        print(f"[ERROR] Source folder not found: {SOURCE_FOLDER}")
        return

    # Create output folder
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    print(f"Source: {SOURCE_FOLDER}")
    print(f"Output: {OUTPUT_FOLDER}")
    print()

    # Find all image files
    image_extensions = {'.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG'}
    image_files = [
        f for f in os.listdir(SOURCE_FOLDER)
        if os.path.splitext(f)[1] in image_extensions
    ]

    if not image_files:
        print("[ERROR] No image files found in source folder!")
        return

    print(f"Found {len(image_files)} photos to resize")
    print()

    # Process each image
    total_original_size = 0
    total_new_size = 0
    successful = 0
    failed = 0

    for idx, filename in enumerate(image_files, 1):
        input_path = os.path.join(SOURCE_FOLDER, filename)

        # Change extension to .jpg for output
        output_filename = os.path.splitext(filename)[0] + '.jpg'
        output_path = os.path.join(OUTPUT_FOLDER, output_filename)

        # Show progress
        print(f"[{idx}/{len(image_files)}] Processing: {filename}...", end=" ")

        # Resize
        result = resize_image(input_path, output_path)

        if result[0]:  # Success
            original_size, new_size = result[1], result[2]
            total_original_size += original_size
            total_new_size += new_size
            successful += 1

            reduction = ((original_size - new_size) / original_size) * 100
            print(f"OK {original_size:.1f}MB -> {new_size:.1f}MB (-{reduction:.0f}%)")
        else:
            failed += 1
            print(f"FAILED")

    # Summary
    print()
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Successfully resized: {successful} photos")
    if failed > 0:
        print(f"Failed: {failed} photos")
    print()
    print(f"Original total size: {total_original_size:.1f} MB")
    print(f"New total size: {total_new_size:.1f} MB")
    print(f"Space saved: {total_original_size - total_new_size:.1f} MB ({((total_original_size - total_new_size) / total_original_size * 100):.0f}% reduction)")
    print()
    print("Ready to upload to Cloudinary!")
    print(f"Upload from: {OUTPUT_FOLDER}")
    print()


if __name__ == "__main__":
    main()
