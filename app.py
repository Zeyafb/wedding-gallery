"""
Wedding Photo Gallery - Streamlit App
Share wedding photos with face-based filtering
"""
import streamlit as st
import os
from PIL import Image
import base64
from io import BytesIO
import numpy as np

from face_processor import FaceProcessor
from cache_manager import CacheManager
import config

# Page configuration
st.set_page_config(
    page_title="Wedding Photo Gallery",
    page_icon="💒",
    layout="wide",
    initial_sidebar_state="collapsed"
)


def init_session_state():
    """Initialize session state variables"""
    if 'face_data' not in st.session_state:
        st.session_state.face_data = None
    if 'selected_person' not in st.session_state:
        st.session_state.selected_person = None
    if 'person_clusters' not in st.session_state:
        st.session_state.person_clusters = {}
    if 'cluster_labels' not in st.session_state:
        st.session_state.cluster_labels = None
    if 'lightbox_photo' not in st.session_state:
        st.session_state.lightbox_photo = None


def load_or_process_faces(folder_path: str):
    """Load faces from cache or process if needed"""
    cache_manager = CacheManager()
    face_processor = FaceProcessor()

    # Check if cache exists and is valid
    if cache_manager.is_cache_valid(folder_path):
        with st.spinner("Loading from cache..."):
            cache_data = cache_manager.load_cache()
            if cache_data:
                st.session_state.face_data = cache_data
                st.session_state.cluster_labels = np.array(cache_data['cluster_labels'])
                st.session_state.person_clusters = face_processor.get_person_clusters(
                    st.session_state.cluster_labels
                )
                st.success(f"Loaded {cache_data['total_faces']} faces from {cache_data['total_photos']} photos!")
                return True

    # Process faces with progress bar
    st.info("Processing faces for the first time... This may take a few minutes.")
    progress_bar = st.progress(0)
    status_text = st.empty()

    def progress_callback(current, total, filename):
        progress = (current + 1) / total
        progress_bar.progress(progress)
        status_text.text(f"Processing {current + 1}/{total}: {filename}")

    try:
        # Load and detect faces
        image_paths = face_processor.load_images(folder_path)
        if len(image_paths) == 0:
            st.error(f"No images found in {folder_path}")
            return False

        face_data = face_processor.detect_faces(image_paths, progress_callback)

        if face_data['total_faces'] == 0:
            st.warning("No faces detected in any photos!")
            return False

        # Cluster faces
        status_text.text("Clustering faces by person...")
        cluster_labels = face_processor.cluster_faces(face_data['face_encodings'])

        # Organize by person
        person_clusters = face_processor.get_person_clusters(cluster_labels)

        # Save to cache
        cache_data = {
            'face_encodings': face_data['face_encodings'],
            'face_to_photo_map': face_data['face_to_photo_map'],
            'cluster_labels': cluster_labels.tolist(),
            'total_photos': face_data['total_photos'],
            'total_faces': face_data['total_faces']
        }
        cache_manager.save_cache(cache_data)

        # Store in session state
        st.session_state.face_data = cache_data
        st.session_state.cluster_labels = cluster_labels
        st.session_state.person_clusters = person_clusters

        progress_bar.empty()
        status_text.empty()
        st.success(f"Processed {face_data['total_faces']} faces from {face_data['total_photos']} photos!")
        return True

    except Exception as e:
        st.error(f"Error processing faces: {str(e)}")
        return False


def get_photos_for_person(person_id: int) -> list:
    """Get all unique photo paths for a specific person"""
    if person_id not in st.session_state.person_clusters:
        return []

    face_indices = st.session_state.person_clusters[person_id]
    photo_paths = set()

    for face_idx in face_indices:
        face_info = st.session_state.face_data['face_to_photo_map'][face_idx]
        photo_paths.add(face_info['photo_path'])

    return sorted(list(photo_paths))


def get_all_photos() -> list:
    """Get all unique photo paths"""
    photo_paths = set()
    for face_info in st.session_state.face_data['face_to_photo_map']:
        photo_paths.add(face_info['photo_path'])
    return sorted(list(photo_paths))


def display_face_selector():
    """Display face thumbnail selector"""
    st.markdown("### Select a person to filter photos")

    # "Show All" button
    col_all, *cols = st.columns(len(st.session_state.person_clusters) + 1)

    with col_all:
        if st.button("🏠 Show All", use_container_width=True, type="primary" if st.session_state.selected_person is None else "secondary"):
            st.session_state.selected_person = None
            st.rerun()

    # Face thumbnails
    face_processor = FaceProcessor()

    for idx, (person_id, face_indices) in enumerate(st.session_state.person_clusters.items()):
        with cols[idx]:
            # Get first face of this person as representative
            first_face_idx = face_indices[0]
            face_info = st.session_state.face_data['face_to_photo_map'][first_face_idx]

            # Extract face thumbnail
            try:
                face_thumb = face_processor.extract_face_thumbnail(
                    face_info['photo_path'],
                    face_info['location']
                )

                # Display circular thumbnail with count
                num_photos = len(get_photos_for_person(person_id))

                # Create a circular mask
                face_thumb_np = np.array(face_thumb)

                # Display image
                st.image(
                    face_thumb_np,
                    use_container_width=True,
                    caption=f"{num_photos} photos"
                )

                # Button to select this person
                button_type = "primary" if st.session_state.selected_person == person_id else "secondary"
                if st.button(f"Person {person_id + 1}", key=f"person_{person_id}", use_container_width=True, type=button_type):
                    st.session_state.selected_person = person_id
                    st.rerun()

            except Exception as e:
                st.error(f"Error loading face: {str(e)}")


def image_to_base64(image_path: str) -> str:
    """Convert image to base64 for display"""
    with open(image_path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()


def display_photo_grid(photo_paths: list):
    """Display photos in a responsive grid"""
    if len(photo_paths) == 0:
        st.info("No photos to display")
        return

    st.markdown(f"### Showing {len(photo_paths)} photos")

    # Create grid
    cols_per_row = config.GRID_COLUMNS
    rows = [photo_paths[i:i + cols_per_row] for i in range(0, len(photo_paths), cols_per_row)]

    for row in rows:
        cols = st.columns(cols_per_row)
        for idx, photo_path in enumerate(row):
            with cols[idx]:
                try:
                    # Load and display image
                    image = Image.open(photo_path)

                    # Resize for display
                    image.thumbnail((config.MAX_DISPLAY_WIDTH, config.MAX_DISPLAY_WIDTH), Image.Resampling.LANCZOS)

                    st.image(image, use_container_width=True)

                    # Button to open in lightbox
                    if st.button("🔍 View", key=f"view_{photo_path}", use_container_width=True):
                        st.session_state.lightbox_photo = photo_path
                        st.rerun()

                except Exception as e:
                    st.error(f"Error loading {os.path.basename(photo_path)}: {str(e)}")


def display_lightbox():
    """Display lightbox modal for viewing full-size photo"""
    if st.session_state.lightbox_photo:
        # Create modal-like dialog
        with st.container():
            col1, col2, col3 = st.columns([1, 3, 1])

            with col2:
                st.markdown("---")
                try:
                    image = Image.open(st.session_state.lightbox_photo)
                    st.image(image, use_container_width=True)

                    st.markdown(f"**{os.path.basename(st.session_state.lightbox_photo)}**")

                    # Close and download buttons
                    col_close, col_download = st.columns(2)

                    with col_close:
                        if st.button("✖ Close", use_container_width=True, type="primary"):
                            st.session_state.lightbox_photo = None
                            st.rerun()

                    with col_download:
                        # Download button
                        with open(st.session_state.lightbox_photo, "rb") as f:
                            st.download_button(
                                "⬇ Download",
                                data=f,
                                file_name=os.path.basename(st.session_state.lightbox_photo),
                                mime="image/jpeg",
                                use_container_width=True
                            )

                    st.markdown("---")

                except Exception as e:
                    st.error(f"Error displaying photo: {str(e)}")
                    st.session_state.lightbox_photo = None


def main():
    """Main app function"""
    init_session_state()

    # Custom CSS
    st.markdown("""
    <style>
        /* Main title styling */
        h1 {
            text-align: center;
            color: #2c3e50;
            font-family: 'Georgia', serif;
            margin-bottom: 2rem;
        }

        /* Circular face thumbnails */
        .stImage > img {
            border-radius: 50%;
            border: 3px solid #e0e0e0;
            transition: transform 0.2s;
        }

        .stImage > img:hover {
            transform: scale(1.05);
            border-color: #3498db;
        }

        /* Button styling */
        .stButton > button {
            border-radius: 8px;
            font-weight: 500;
        }

        /* Clean container spacing */
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }

        /* Grid spacing */
        [data-testid="column"] {
            padding: 0.5rem;
        }
    </style>
    """, unsafe_allow_html=True)

    # Header
    st.title("💒 Wedding Photo Gallery")
    st.markdown("---")

    # Sidebar for settings
    with st.sidebar:
        st.header("Settings")

        # Folder path input
        folder_path = st.text_input(
            "Photos Folder Path",
            value=config.PHOTOS_FOLDER,
            help="Enter the path to your wedding photos folder"
        )

        # Clear cache button
        if st.button("🔄 Clear Cache & Reprocess", type="secondary"):
            cache_manager = CacheManager()
            cache_manager.clear_cache()
            st.session_state.face_data = None
            st.session_state.person_clusters = {}
            st.session_state.cluster_labels = None
            st.session_state.selected_person = None
            st.success("Cache cleared! Refresh to reprocess.")
            st.rerun()

        st.markdown("---")
        st.caption(f"Face detection model: {config.FACE_DETECTION_MODEL}")
        st.caption(f"Matching tolerance: {config.TOLERANCE}")

    # Load or process faces
    if st.session_state.face_data is None:
        if os.path.exists(folder_path):
            load_or_process_faces(folder_path)
        else:
            st.error(f"Folder not found: {folder_path}")
            st.info("Please update the folder path in the sidebar or in config.py")
            return

    # Show lightbox if photo is selected
    if st.session_state.lightbox_photo:
        display_lightbox()
        return

    # Display face selector
    if st.session_state.face_data and len(st.session_state.person_clusters) > 0:
        display_face_selector()
        st.markdown("---")

        # Display filtered photos
        if st.session_state.selected_person is None:
            photos = get_all_photos()
        else:
            photos = get_photos_for_person(st.session_state.selected_person)

        display_photo_grid(photos)
    else:
        st.info("Processing photos...")


if __name__ == "__main__":
    main()
