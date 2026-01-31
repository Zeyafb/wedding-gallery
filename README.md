# 💒 Wedding Photo Gallery

A beautiful Streamlit app for sharing wedding photos with intelligent face-based filtering. Automatically detect and cluster faces, then let guests filter photos by person with a single click.

## Features

✨ **Smart Face Detection**
- Automatically detects all faces in ~430+ wedding photos
- Uses the `face_recognition` library for accurate face detection
- Processes photos once and caches results for instant loading

🎭 **Person-Based Filtering**
- Groups similar faces together using clustering algorithms
- Click on a face thumbnail to see all photos containing that person
- Visual face selector with photo counts

🖼️ **Beautiful UI**
- Clean, minimal design perfect for wedding guests
- Responsive grid layout that works on all devices
- Lightbox modal for viewing full-size photos
- Circular face thumbnails with hover effects

⚡ **High Performance**
- Caches all face embeddings and metadata locally
- Progress bars during initial processing
- Fast filtering and navigation

## Installation

### Prerequisites

This app requires Python 3.8+ and some system dependencies for face_recognition.

#### Windows
```bash
# Install CMake and dlib dependencies
pip install cmake
```

#### macOS
```bash
# Install using Homebrew
brew install cmake
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt-get update
sudo apt-get install build-essential cmake
sudo apt-get install libopenblas-dev liblapack-dev
sudo apt-get install libx11-dev libgtk-3-dev
```

### Install Python Dependencies

```bash
# Clone or download this repository
cd wedding-gallery

# Create a virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

## Quick Start

### 1. Add Your Photos

Create a folder with your wedding photos and note the path. For example:
```
C:\Users\YourName\Pictures\Wedding2024
```

### 2. Configure the App

Edit `config.py` and update the `PHOTOS_FOLDER` path:

```python
PHOTOS_FOLDER = "C:/Users/YourName/Pictures/Wedding2024"  # Update this!
```

Or you can enter the path in the sidebar when running the app.

### 3. Run the App

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

### 4. First Time Processing

On the first run:
- The app will process all photos (this takes a few minutes for ~430 photos)
- A progress bar shows the current status
- Results are cached automatically for instant loading next time

### 5. Share with Guests

Once processed, guests can:
- Click on face thumbnails to filter photos by person
- Click "Show All" to see all photos
- Click "View" on any photo to see it full-size
- Download individual photos

## Configuration Options

Edit `config.py` to customize:

```python
# Photo folder path
PHOTOS_FOLDER = "wedding_photos"

# Face detection model ('hog' is faster, 'cnn' is more accurate)
FACE_DETECTION_MODEL = "hog"

# Matching tolerance (lower = more strict, 0.6 is default)
TOLERANCE = 0.6

# UI settings
THUMBNAIL_SIZE = 100
GRID_COLUMNS = 4
MAX_DISPLAY_WIDTH = 800
```

## Deploying to Streamlit Cloud (Free)

### Option 1: Deploy with Photos in Repo (Small galleries only)

**Note:** GitHub has a 100MB per file limit and repos should stay under 1GB.

1. **Create a GitHub repository**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/yourusername/wedding-gallery.git
   git push -u origin main
   ```

2. **Deploy on Streamlit Cloud**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Sign in with GitHub
   - Click "New app"
   - Select your repository
   - Set main file path: `app.py`
   - Click "Deploy"

### Option 2: Deploy with External Photo Hosting (Recommended for 430+ photos)

For larger photo collections, host images separately and update paths:

1. **Host photos on cloud storage:**
   - **Google Drive**: Upload to a public folder, get shareable links
   - **AWS S3**: Upload to public bucket
   - **Cloudinary**: Free tier supports up to 25GB
   - **Imgur**: Good for smaller collections

2. **Update code to fetch from URLs:**
   - Modify `face_processor.py` to download images from URLs
   - Update config with your hosting URLs

3. **Deploy to Streamlit Cloud** (as in Option 1)

### Option 3: Self-Hosting

Deploy on your own server:

```bash
# Install and run with nohup
nohup streamlit run app.py --server.port 8501 &

# Or use screen/tmux for persistent sessions
screen -S wedding-gallery
streamlit run app.py
# Press Ctrl+A, then D to detach
```

## Usage Tips

### Clear Cache and Reprocess

If you add/remove photos or want to reprocess:
1. Click "Clear Cache & Reprocess" in the sidebar
2. The app will detect faces again on next load

### Improve Face Detection Accuracy

Edit `config.py`:
```python
FACE_DETECTION_MODEL = "cnn"  # More accurate but slower (requires GPU for best performance)
FACE_JITTERS = 2  # Higher = more accurate but slower
TOLERANCE = 0.5  # Lower = stricter matching
```

### Handling Large Collections

For 1000+ photos:
- Use `FACE_DETECTION_MODEL = "hog"` for faster processing
- Consider processing in batches
- Ensure good lighting in photos for better detection

## Troubleshooting

### "No module named 'face_recognition'"

Make sure you've installed all dependencies:
```bash
pip install -r requirements.txt
```

If installation fails, install `dlib` separately first:
```bash
pip install cmake
pip install dlib
pip install face_recognition
```

### "No faces detected in any photos"

- Check that photos contain visible faces
- Try using `FACE_DETECTION_MODEL = "cnn"` for better accuracy
- Ensure photos are in supported formats (jpg, png, etc.)

### Cache file is too large

The cache file can be large for many photos. To reduce size:
- Process fewer photos at once
- Use cloud storage for photos instead of local files

### App is slow

- Use `hog` model instead of `cnn` for faster processing
- Reduce `FACE_JITTERS` to 1
- Ensure cache is being used (check for `face_embeddings_cache.pkl`)

## Project Structure

```
wedding-gallery/
├── app.py                          # Main Streamlit app
├── face_processor.py               # Face detection and clustering
├── cache_manager.py                # Cache management
├── config.py                       # Configuration settings
├── requirements.txt                # Python dependencies
├── README.md                       # This file
├── .gitignore                      # Git ignore file
├── wedding_photos/                 # Your photos folder (create this)
└── face_embeddings_cache.pkl       # Generated cache file
```

## Privacy & Security

- All processing happens locally - no data is sent to external services
- When deploying to Streamlit Cloud, be mindful that photos will be publicly accessible
- Consider password-protecting your deployment or using Streamlit's authentication features
- Don't commit your cache file to git (it contains face embeddings)

## Performance Benchmarks

Approximate processing times (M1 MacBook Pro):
- 100 photos: ~2-3 minutes (hog model)
- 430 photos: ~8-12 minutes (hog model)
- 1000 photos: ~20-30 minutes (hog model)

Subsequent loads: **Instant** (cached)

## Credits

Built with:
- [Streamlit](https://streamlit.io) - App framework
- [face_recognition](https://github.com/ageitgey/face_recognition) - Face detection
- [scikit-learn](https://scikit-learn.org/) - Face clustering (DBSCAN)
- [Pillow](https://python-pillow.org/) - Image processing

## License

MIT License - feel free to use and modify for your own events!

## Support

Having issues? Check the troubleshooting section above or open an issue on GitHub.

---

**Enjoy sharing your beautiful wedding memories! 💒💕**
