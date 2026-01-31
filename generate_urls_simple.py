"""
Simple URL generator for Cloudinary
Creates URLs based on your uploaded files without needing API keys
"""
import os

# =============================================================================
# CONFIGURATION
# =============================================================================
CLOUD_NAME = "dwt17ikflb"
FOLDER = "wedding-photos"
RESIZED_FOLDER = r"D:\Fayez & Kyla Final Wedding - Resized"

# =============================================================================

def generate_urls():
    """Generate Cloudinary URLs from local filenames"""

    print("=" * 70)
    print("Simple Cloudinary URL Generator")
    print("=" * 70)
    print()

    # Get all image files from resized folder
    if not os.path.exists(RESIZED_FOLDER):
        print(f"[ERROR] Folder not found: {RESIZED_FOLDER}")
        return

    image_files = []
    for filename in os.listdir(RESIZED_FOLDER):
        if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            image_files.append(filename)

    if not image_files:
        print("[ERROR] No images found!")
        return

    image_files = sorted(image_files)

    print(f"Found {len(image_files)} photos")
    print(f"Generating URLs for cloud: {CLOUD_NAME}")
    print(f"Folder: {FOLDER}")
    print()

    # Generate URLs
    urls = []
    for filename in image_files:
        # Remove extension and create URL
        # Cloudinary URL format: https://res.cloudinary.com/{cloud_name}/image/upload/{folder}/{filename}
        url = f"https://res.cloudinary.com/{CLOUD_NAME}/image/upload/{FOLDER}/{filename}"
        urls.append(url)

    # Save to file
    output_file = "cloudinary_urls.txt"
    with open(output_file, "w") as f:
        for url in urls:
            f.write(url + "\n")

    print(f"Generated {len(urls)} URLs")
    print(f"Saved to: {output_file}")
    print()
    print("Sample URLs:")
    for url in urls[:3]:
        print(f"  {url}")
    print(f"  ... ({len(urls) - 3} more)")
    print()
    print("Next steps:")
    print("1. Update config.py: STORAGE_BACKEND = 'cloudinary'")
    print("2. Update config.py: CLOUDINARY_CLOUD_NAME = 'dwt17ikflb'")
    print("3. Test the app locally or deploy to Streamlit Cloud!")
    print()


if __name__ == "__main__":
    generate_urls()
