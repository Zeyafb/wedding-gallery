# Cloudinary Setup Guide (Recommended Method)

## Why Cloudinary is Best for Your Wedding Gallery

✅ **Free & Fast**
- 25GB storage, 25GB bandwidth/month (FREE)
- Fast CDN delivery worldwide
- Photos load instantly for all guests

✅ **Easy Deployment**
- No complex API setup needed for Streamlit Cloud
- Upload once, use everywhere
- Works perfectly with face detection

✅ **Crisp Photo Loading**
- Photos are delivered via CDN (Content Delivery Network)
- Automatically optimized for web
- Much faster than Google Drive

---

## Method 1: Simple URL List (RECOMMENDED - No API Keys Needed!)

This is the easiest way to deploy without dealing with API keys on Streamlit Cloud.

### Step 1: Upload Photos to Cloudinary

1. **Sign up** at [cloudinary.com](https://cloudinary.com) (free account)

2. **Upload your photos:**
   - Go to Media Library
   - Create a folder called `wedding-photos`
   - Upload all ~430 photos (can bulk upload)

3. **Get photo URLs:**
   - Click on any photo
   - Copy the "Secure URL" (starts with `https://res.cloudinary.com/...`)
   - They all follow the same pattern

### Step 2: Generate URL List

Run this helper script after uploading to Cloudinary:

```python
# save as: generate_cloudinary_urls.py

# Your Cloudinary cloud name (get from dashboard)
CLOUD_NAME = "your-cloud-name"
FOLDER = "wedding-photos"

# List of your photo filenames (or get them from Cloudinary API)
# You can get this list by exporting from Media Library
photo_filenames = [
    "IMG_001.jpg",
    "IMG_002.jpg",
    # ... all your photos
]

# Generate URLs
with open("cloudinary_urls.txt", "w") as f:
    for filename in photo_filenames:
        url = f"https://res.cloudinary.com/{CLOUD_NAME}/image/upload/{FOLDER}/{filename}"
        f.write(url + "\n")

print(f"Generated {len(photo_filenames)} URLs to cloudinary_urls.txt")
```

Or use the automatic script I've created (see below).

### Step 3: Update Config

Edit `config.py`:

```python
STORAGE_BACKEND = "cloudinary"
CLOUDINARY_CLOUD_NAME = "your-cloud-name"  # From dashboard
```

### Step 4: Deploy to Streamlit Cloud

1. Push to GitHub (include `cloudinary_urls.txt`)
2. Deploy on Streamlit Cloud
3. Share the URL with friends!

**Done! No API keys needed on Streamlit Cloud.**

---

## Method 2: Using Cloudinary API (More Automatic)

If you want the app to automatically list photos from Cloudinary.

### Setup:

1. **Get API credentials** from Cloudinary dashboard:
   - API Key
   - API Secret

2. **Update `requirements.txt`** - uncomment the line:
   ```
   cloudinary>=1.36.0
   ```

3. **Set environment variables** on Streamlit Cloud:
   - `CLOUDINARY_API_KEY` = your-api-key
   - `CLOUDINARY_API_SECRET` = your-api-secret

4. **Update `config.py`**:
   ```python
   STORAGE_BACKEND = "cloudinary"
   CLOUDINARY_CLOUD_NAME = "your-cloud-name"
   CLOUDINARY_FOLDER = "wedding-photos"
   ```

---

## Helper Script: Auto-Generate URL List from Cloudinary

Save this as `generate_urls_from_cloudinary.py`:

```python
import cloudinary
import cloudinary.api

# Configure (get these from your Cloudinary dashboard)
cloudinary.config(
    cloud_name="your-cloud-name",
    api_key="your-api-key",
    api_secret="your-api-secret",
    secure=True
)

# Get all photos from folder
folder = "wedding-photos"
result = cloudinary.api.resources(
    type="upload",
    prefix=folder,
    max_results=500  # Increase if you have more photos
)

# Write URLs to file
with open("cloudinary_urls.txt", "w") as f:
    for resource in result['resources']:
        f.write(resource['secure_url'] + "\n")

print(f"Generated {len(result['resources'])} URLs!")
print("File saved: cloudinary_urls.txt")
```

Run it:
```bash
pip install cloudinary
python generate_urls_from_cloudinary.py
```

---

## Comparison: What Gets You the Sharpest Photos?

| Storage Method | Speed | Quality | Setup Difficulty |
|----------------|-------|---------|------------------|
| **Cloudinary** | ⚡⚡⚡⚡⚡ | 🎨🎨🎨🎨🎨 | ⭐⭐⭐⭐⭐ |
| **AWS S3** | ⚡⚡⚡⚡⚡ | 🎨🎨🎨🎨🎨 | ⭐⭐⭐ |
| **Google Drive** | ⚡⚡ | 🎨🎨🎨 | ⭐⭐ |
| **Local (for testing)** | ⚡⚡⚡⚡⚡ | 🎨🎨🎨🎨🎨 | ⭐⭐⭐⭐⭐ |

**Winner: Cloudinary** (fast CDN + easy setup + free)

---

## Testing Locally First

Before deploying, test with local photos:

1. Create a `wedding_photos` folder
2. Add a few test photos
3. Keep `STORAGE_BACKEND = "local"` in config.py
4. Run: `streamlit run app.py`
5. Process faces and test the interface
6. Once happy, switch to Cloudinary for deployment

---

## Common Questions

**Q: Will photos load fast for all my guests?**
A: Yes! Cloudinary uses a CDN, so photos are served from servers closest to each guest.

**Q: Can I password-protect the gallery?**
A: Yes! See the main README for how to add simple password protection.

**Q: What if I have more than 430 photos?**
A: Cloudinary free tier handles 25GB (~5000+ high-res photos). You're good!

**Q: Will face detection work with cloud URLs?**
A: Yes! The app downloads photos temporarily for face detection, then caches results.

**Q: How long does initial processing take?**
A: ~10-15 minutes for 430 photos (one time only). After caching, instant loading!

---

## Next Steps

1. ✅ Sign up for Cloudinary
2. ✅ Upload your wedding photos
3. ✅ Use Method 1 (URL list) for easiest deployment
4. ✅ Test locally first
5. ✅ Deploy to Streamlit Cloud
6. 🎉 Share with friends!
