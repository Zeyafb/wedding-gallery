"""
Helper script to generate Cloudinary URLs for deployment
This creates a cloudinary_urls.txt file with all photo URLs

Usage:
1. Install: pip install cloudinary
2. Update the config below with your Cloudinary details
3. Run: python generate_cloudinary_urls.py
"""

import cloudinary
import cloudinary.api
import sys

# =============================================================================
# CONFIGURATION - UPDATE THESE!
# =============================================================================
CLOUD_NAME = "dwt17ikflb"           # Your Cloudinary cloud name
API_KEY = "your-api-key"            # Get from Cloudinary dashboard (if using API)
API_SECRET = "your-api-secret"      # Get from Cloudinary dashboard (if using API)
FOLDER = "wedding-photos"           # Your folder name in Cloudinary

# =============================================================================

def generate_urls():
    """Generate URL list from Cloudinary"""

    # Configure Cloudinary
    cloudinary.config(
        cloud_name=CLOUD_NAME,
        api_key=API_KEY,
        api_secret=API_SECRET,
        secure=True
    )

    print(f"Connecting to Cloudinary: {CLOUD_NAME}")
    print(f"Fetching photos from folder: {FOLDER}")
    print()

    try:
        # Get all photos from folder
        result = cloudinary.api.resources(
            type="upload",
            prefix=FOLDER,
            max_results=500  # Adjust if you have more photos
        )

        if not result.get('resources'):
            print(f"❌ No photos found in folder '{FOLDER}'")
            print("   Make sure you've uploaded photos to Cloudinary!")
            sys.exit(1)

        # Write URLs to file
        output_file = "cloudinary_urls.txt"
        with open(output_file, "w") as f:
            for resource in result['resources']:
                f.write(resource['secure_url'] + "\n")

        print(f"✅ Success! Generated {len(result['resources'])} photo URLs")
        print(f"📄 Saved to: {output_file}")
        print()
        print("Next steps:")
        print("1. Add cloudinary_urls.txt to your git repo")
        print("2. Update config.py: STORAGE_BACKEND = 'cloudinary'")
        print("3. Deploy to Streamlit Cloud!")

    except cloudinary.exceptions.AuthorizationRequired:
        print("❌ Authentication failed!")
        print("   Check your API_KEY and API_SECRET")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)


def check_config():
    """Check if configuration is updated"""
    if CLOUD_NAME == "your-cloud-name":
        print("⚠️  You need to update the configuration first!")
        print()
        print("Edit this file and update:")
        print("  - CLOUD_NAME (from Cloudinary dashboard)")
        print("  - API_KEY (from Cloudinary dashboard)")
        print("  - API_SECRET (from Cloudinary dashboard)")
        print("  - FOLDER (your folder name in Cloudinary)")
        print()
        sys.exit(1)


if __name__ == "__main__":
    print("=" * 60)
    print("Cloudinary URL Generator")
    print("=" * 60)
    print()

    check_config()
    generate_urls()
