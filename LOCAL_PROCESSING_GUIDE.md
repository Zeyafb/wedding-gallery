# Local Face Processing Guide

This guide will help you process faces on your Windows computer and deploy the app instantly.

## Why Process Locally?

- ✅ Avoids dlib build issues on Streamlit Cloud
- ✅ Faster deployment (2-3 minutes instead of 30+)
- ✅ Process faces once, deploy instantly forever

---

## Step 1: Install CMake on Windows

1. **Download CMake:**
   - Go to: https://cmake.org/download/
   - Download: `cmake-X.XX.X-windows-x86_64.msi`

2. **Install CMake:**
   - Run the installer
   - **IMPORTANT:** Check the box "Add CMake to the system PATH for all users"
   - Complete installation

3. **Verify CMake:**
   ```bash
   # Open new Command Prompt
   cmake --version
   # Should show: cmake version 3.XX.X
   ```

---

## Step 2: Install Python Dependencies

```bash
cd wedding-gallery
pip install -r requirements-local.txt
```

This will install:
- Pillow, numpy, scikit-learn, requests (quick)
- dlib (will take 5-10 mins to build on Windows)
- face_recognition

---

## Step 3: Run Face Processing

```bash
python process_faces_locally.py
```

**What happens:**
- Downloads all 430 photos from Cloudinary
- Detects faces in each photo (~10-15 minutes)
- Clusters faces by person
- Saves `face_embeddings_cache.pkl`

**Progress:**
```
[1/430] Processing: DSC00001.jpg... OK - Found 2 faces
[2/430] Processing: DSC00004.jpg... OK - Found 3 faces
...
```

---

## Step 4: Upload Cache to GitHub

```bash
git add face_embeddings_cache.pkl
git commit -m "Add pre-processed face cache"
git push
```

---

## Step 5: Deploy to Streamlit Cloud

**The deployment will now be FAST:**
- ✅ No dlib build (2-3 minute deploy)
- ✅ App loads pre-processed cache
- ✅ Face filtering works immediately!

**Just reboot your Streamlit app:**
- Go to Streamlit Cloud dashboard
- Click "Reboot"
- App deploys in 2-3 minutes
- Face filtering ready!

---

## Troubleshooting

### CMake not found
- Make sure you checked "Add to PATH" during installation
- Restart Command Prompt after installing
- Try running from a NEW Command Prompt window

### dlib build fails on Windows
- Make sure Visual Studio Build Tools are installed
- Alternative: Use pip's pre-built wheel:
  ```bash
  pip install cmake
  pip install dlib
  ```

### Script takes too long
- 10-15 minutes is normal for 430 photos
- Processing from Cloudinary (downloading each photo)
- One-time only!

---

## What Gets Uploaded

**Files in GitHub:**
- `cloudinary_urls.txt` (430 URLs, ~20 KB)
- `face_embeddings_cache.pkl` (Face data, ~5-10 MB)
- App code

**NOT uploaded:**
- Original wedding photos (stay on Cloudinary)
- Resized photos (local only, not needed)

---

## After Deployment

Your guests will:
- Load app instantly
- See face thumbnails immediately
- Filter photos by person
- Download photos

All powered by your pre-processed cache! 🎉
