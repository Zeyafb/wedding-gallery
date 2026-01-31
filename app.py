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
import requests

from cache_manager import CacheManager
from storage_manager import StorageManager
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


def get_person_clusters(cluster_labels):
    """
    Organize faces by person (cluster)

    Args:
        cluster_labels: Array of cluster IDs for each face

    Returns:
        Dict mapping cluster_id -> list of face indices
    """
    person_clusters = {}

    for face_idx, cluster_id in enumerate(cluster_labels):
        if cluster_id not in person_clusters:
            person_clusters[cluster_id] = []
        person_clusters[cluster_id].append(face_idx)

    # Sort by cluster size (most photos first)
    person_clusters = dict(
        sorted(person_clusters.items(), key=lambda x: len(x[1]), reverse=True)
    )

    return person_clusters


def extract_face_thumbnail(image_path, face_location):
    """
    Extract face region from image and return as PIL Image

    Args:
        image_path: Path to the image file or URL
        face_location: Tuple of (top, right, bottom, left) coordinates

    Returns:
        PIL Image of the cropped face
    """
    top, right, bottom, left = face_location

    # Load image with PIL (works with URLs and local paths)
    if image_path.startswith('http'):
        response = requests.get(image_path)
        image = Image.open(BytesIO(response.content))
    else:
        image = Image.open(image_path)

    # Add some padding around the face
    padding = 20
    top = max(0, top - padding)
    left = max(0, left - padding)
    bottom = min(image.height, bottom + padding)
    right = min(image.width, right + padding)

    # Crop face
    face_image = image.crop((left, top, right, bottom))

    # Resize to thumbnail size
    face_image.thumbnail((config.THUMBNAIL_SIZE, config.THUMBNAIL_SIZE), Image.Resampling.LANCZOS)

    return face_image


def load_faces_from_cache():
    """Load pre-processed faces from cache"""
    cache_manager = CacheManager()

    with st.spinner("Loading face data..."):
        cache_data = cache_manager.load_cache()
        if cache_data:
            st.session_state.face_data = cache_data
            st.session_state.cluster_labels = np.array(cache_data['cluster_labels'])
            st.session_state.person_clusters = get_person_clusters(
                st.session_state.cluster_labels
            )

            # Filter out noise cluster (-1) from display
            if -1 in st.session_state.person_clusters:
                noise_count = len(st.session_state.person_clusters[-1])
                unique_people = len(st.session_state.person_clusters) - 1
            else:
                noise_count = 0
                unique_people = len(st.session_state.person_clusters)

            st.success(f"✓ Loaded {cache_data['total_faces']} faces from {cache_data['total_photos']} photos ({unique_people} unique people)")
            return True
        else:
            st.error("⚠️ Face cache not found. Please contact the administrator.")
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

    # "Show All" button at the top
    if st.button("🏠 Show All Photos", use_container_width=True, type="primary" if st.session_state.selected_person is None else "secondary"):
        st.session_state.selected_person = None
        st.rerun()

    st.markdown("---")
    st.markdown("**Click a face to filter photos:**")

    # Get valid people (exclude noise cluster -1) and sort by face count
    valid_people = [(pid, faces) for pid, faces in st.session_state.person_clusters.items() if pid >= 0]

    # Display faces in a grid (8 columns per row)
    cols_per_row = 8

    for row_start in range(0, len(valid_people), cols_per_row):
        cols = st.columns(cols_per_row)
        row_people = valid_people[row_start:row_start + cols_per_row]

        for col_idx, (person_id, face_indices) in enumerate(row_people):
            with cols[col_idx]:
            # Get first face of this person as representative
            first_face_idx = face_indices[0]
            face_info = st.session_state.face_data['face_to_photo_map'][first_face_idx]

            # Extract face thumbnail
            try:
                face_thumb = extract_face_thumbnail(
                    face_info['photo_path'],
                    face_info['location']
                )

                # Display circular thumbnail with count
                num_photos = len(get_photos_for_person(person_id))

                # Create a circular mask
                face_thumb_np = np.array(face_thumb)

                # Display image with click button
                st.image(
                    face_thumb_np,
                    use_container_width=True
                )

                # Button to select this person
                button_type = "primary" if st.session_state.selected_person == person_id else "secondary"
                if st.button(f"📷 {num_photos}", key=f"person_{person_id}", use_container_width=True, type=button_type, help=f"{num_photos} photos with this person"):
                    st.session_state.selected_person = person_id
                    st.rerun()

            except Exception as e:
                st.error(f"Error: {str(e)[:50]}")


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

    # Load pre-processed faces from cache
    if st.session_state.face_data is None:
        load_faces_from_cache()

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
