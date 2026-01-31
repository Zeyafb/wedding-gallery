# Deployment Guide: Photo Storage & Sharing

## The Challenge

With ~430 wedding photos (probably 2-5GB total), you can't store them directly in a GitHub repo for Streamlit Cloud deployment. Here are your best options:

---

## ⭐ RECOMMENDED: Option 1 - Cloudinary + Streamlit Cloud

**Best for:** Easy setup, reliable, free for your use case

### Step 1: Upload Photos to Cloudinary

1. **Sign up for free**: [cloudinary.com](https://cloudinary.com)
   - Free tier: 25GB storage, 25GB bandwidth/month
   - Perfect for wedding galleries

2. **Create a folder** called `wedding-photos`

3. **Bulk upload your photos**:
   ```bash
   # Using Cloudinary's web interface (easiest)
   # Or use their CLI:
   npm install -g cloudinary-cli
   cld admin upload wedding_photos/* --folder wedding-photos
   ```

4. **Get your Cloud Name** from the dashboard (you'll need this)

### Step 2: Update the App Configuration

Add to your `config.py`:
```python
# Storage backend: 'local' or 'cloudinary'
STORAGE_BACKEND = "cloudinary"

# Cloudinary settings (if using cloudinary)
CLOUDINARY_CLOUD_NAME = "your-cloud-name"  # Get from dashboard
CLOUDINARY_FOLDER = "wedding-photos"
```

### Step 3: Deploy to Streamlit Cloud

1. **Push to GitHub**:
   ```bash
   cd wedding-gallery
   git init
   git add .
   git commit -m "Wedding photo gallery"
   git branch -M main
   git remote add origin https://github.com/YOUR-USERNAME/wedding-gallery.git
   git push -u origin main
   ```

2. **Deploy on Streamlit Cloud**:
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Sign in with GitHub
   - Click "New app"
   - Repository: `YOUR-USERNAME/wedding-gallery`
   - Branch: `main`
   - Main file: `app.py`
   - Click "Deploy!"

3. **You'll get a URL like**: `https://your-app-name.streamlit.app`

### Step 4: Share with Friends

Just send them the Streamlit URL! They can:
- Browse all photos
- Filter by person
- Download photos they want

**Cost:** $0 (both services are free)

---

## Option 2 - Google Drive + Streamlit Cloud

**Best for:** If you already use Google Drive

### Setup:

1. **Upload photos to Google Drive**
2. **Make folder publicly accessible** (Anyone with link can view)
3. **Use Google Drive API** or direct links
4. **Deploy app to Streamlit Cloud**

**Pros:**
- 15GB free storage
- Already have Google account

**Cons:**
- API setup is more complex
- Slower than CDN
- Rate limits

---

## Option 3 - AWS S3 + Streamlit Cloud

**Best for:** If you want professional hosting and have AWS experience

### Setup:

1. **Create S3 bucket** (public read access)
2. **Upload photos**:
   ```bash
   aws s3 sync ./wedding_photos s3://your-bucket-name/wedding-photos/ --acl public-read
   ```
3. **Update config** with bucket URL
4. **Deploy to Streamlit Cloud**

**Cost:** ~$0.50-2/month for storage + bandwidth

---

## Option 4 - Self-Host Everything (Advanced)

**Best for:** Full control, privacy, technical users

### Option 4A: Use a VPS (DigitalOcean, Linode, etc.)

1. **Get a VPS** ($5-10/month)
2. **Upload photos** to VPS
3. **Run Streamlit** with systemd
4. **Set up nginx** as reverse proxy
5. **Get free SSL** with Let's Encrypt

**Share URL:** `https://your-domain.com`

### Option 4B: Use Ngrok (Quick Test)

```bash
# Run app locally
streamlit run app.py

# In another terminal, expose it
ngrok http 8501
```

You'll get a temporary URL like: `https://abc123.ngrok.io`

**Cons:** Free ngrok URLs expire after 8 hours

---

## Comparison Table

| Solution | Cost | Ease | Speed | Privacy |
|----------|------|------|-------|---------|
| **Cloudinary + Streamlit** ⭐ | Free | ⭐⭐⭐⭐⭐ | ⚡⚡⚡⚡⚡ | Public |
| Google Drive + Streamlit | Free | ⭐⭐⭐ | ⚡⚡⚡ | Link-only |
| AWS S3 + Streamlit | ~$2/mo | ⭐⭐⭐ | ⚡⚡⚡⚡⚡ | Public |
| Self-Host VPS | $5-10/mo | ⭐⭐ | ⚡⚡⚡⚡ | Full control |
| Ngrok (temp) | Free | ⭐⭐⭐⭐ | ⚡⚡⚡⚡ | Link-only |

---

## Making Your Gallery Private

If you want to restrict access to invited guests only:

### Add Password Protection

I can add a simple password to the app:

```python
# In app.py, add at the top of main():
def check_password():
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        password = st.text_input("Enter password:", type="password")
        if st.button("Login"):
            if password == "YourWeddingPassword123":  # Change this!
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Incorrect password")
        st.stop()

check_password()
```

### Or Use Streamlit's Built-in Auth (Paid)

Streamlit Cloud has built-in authentication for Teams plan ($20/month).

---

## My Recommendation for You

**For quick & free sharing:**

1. **Use Cloudinary** for photo storage (free 25GB)
2. **Deploy to Streamlit Cloud** (free hosting)
3. **Add simple password** if you want privacy
4. **Share URL** with wedding guests

**Total cost:** $0
**Setup time:** ~30 minutes
**Shareable URL:** `https://your-wedding-gallery.streamlit.app`

---

## Need Help?

Let me know which option you want to pursue and I can:
- Update the code to support your chosen storage backend
- Add password protection
- Help with the deployment process
- Create upload scripts for bulk photo transfer
