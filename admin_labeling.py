"""
Admin interface for labeling people in the wedding gallery
Run this locally: streamlit run admin_labeling.py
"""
import streamlit as st
import json
import os
from cache_manager import CacheManager
import config
import numpy as np

# Page configuration
st.set_page_config(
    page_title="Admin - Label People",
    page_icon="✏️",
    layout="wide"
)

NAMES_FILE = "person_names.json"


def load_names():
    """Load existing name mappings"""
    if os.path.exists(NAMES_FILE):
        with open(NAMES_FILE, 'r') as f:
            return json.load(f)
    return {}


def save_names(names_dict):
    """Save name mappings to JSON file"""
    with open(NAMES_FILE, 'w') as f:
        json.dump(names_dict, f, indent=2)


def get_person_clusters(cluster_labels):
    """Organize faces by person (cluster)"""
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


def get_face_thumbnail_url(image_path, face_location):
    """Get optimized face thumbnail URL using Cloudinary transformations"""
    if image_path.startswith('https://res.cloudinary.com/'):
        top, right, bottom, left = face_location

        # Calculate crop dimensions with padding
        padding = 20
        crop_left = max(0, left - padding)
        crop_top = max(0, top - padding)
        crop_width = (right - left) + (2 * padding)
        crop_height = (bottom - top) + (2 * padding)

        base_url = image_path.split('/upload/')[0]
        image_part = image_path.split('/upload/')[1]

        # Use exact coordinates for cropping, then resize to thumbnail
        transformation = f"c_crop,x_{crop_left},y_{crop_top},w_{crop_width},h_{crop_height}/c_scale,h_150,w_150"
        thumbnail_url = f"{base_url}/upload/{transformation}/{image_part}"

        return thumbnail_url
    else:
        return image_path


def get_photos_for_person(face_data, person_clusters, person_id):
    """Get all unique photo paths for a specific person"""
    if person_id not in person_clusters:
        return []

    face_indices = person_clusters[person_id]
    photo_paths = set()

    for face_idx in face_indices:
        face_info = face_data['face_to_photo_map'][face_idx]
        photo_paths.add(face_info['photo_path'])

    return len(photo_paths)


def get_used_photos(face_data, person_clusters, person_names):
    """Get set of photos that appear in the main gallery (have valid named faces)"""
    used_photos = set()

    # Only count photos that have at least one valid named person
    for person_id, face_indices in person_clusters.items():
        # Skip noise cluster
        if person_id < 0:
            continue

        # Check if this person has a valid name
        name = person_names.get(str(person_id), "")
        skip_keywords = ['skip', 'sk', '???', 'this one is blank', 'no idea', 'need to review']
        if not name or name.lower() in skip_keywords or any(keyword in name.lower() for keyword in skip_keywords):
            continue

        # This person is valid, add all their photos
        for face_idx in face_indices:
            face_info = face_data['face_to_photo_map'][face_idx]
            photo_url = face_info['photo_path']
            # Skip sample images
            if not any(sample in photo_url for sample in ['sample.jpg.jpg', 'cld-sample-2.jpg.jpg', 'cld-sample-5.jpg.jpg']):
                used_photos.add(photo_url)

    return used_photos


def get_all_photos():
    """Get all photos from cloudinary_urls.txt"""
    try:
        with open('cloudinary_urls.txt', 'r') as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        return []


def show_unused_photos():
    """Show photos that don't have detected faces and allow tagging with names"""
    st.markdown("### Tag photos without detected faces")
    st.markdown("These photos were uploaded but no faces were detected in them. You can manually tag them with names.")

    # Get all photos and used photos
    all_photos = get_all_photos()
    used_photos = get_used_photos(
        st.session_state.face_data,
        st.session_state.person_clusters,
        st.session_state.person_names
    )

    # Find unused photos (exclude sample images)
    unused_photos = [p for p in all_photos
                    if p not in used_photos
                    and not any(sample in p for sample in ['sample.jpg.jpg', 'cld-sample-2.jpg.jpg', 'cld-sample-5.jpg.jpg'])]

    if not unused_photos:
        st.success("All photos have detected faces!")
        return

    st.info(f"Found {len(unused_photos)} photos without detected faces (out of {len(all_photos)} total)")

    # Load photo tags
    if 'photo_tags' not in st.session_state:
        try:
            with open('photo_tags.json', 'r') as f:
                st.session_state.photo_tags = json.load(f)
        except FileNotFoundError:
            st.session_state.photo_tags = {}

    # Get list of valid names
    valid_names = []
    for pid, name in st.session_state.person_names.items():
        if name and name.lower() not in ['skip', 'sk', '???', 'this one is blank'] and 'no idea' not in name.lower() and 'need to review' not in name.lower():
            valid_names.append(name)
    valid_names = sorted(set(valid_names))

    # Save button
    if st.button("💾 Save Photo Tags", type="primary", use_container_width=True):
        with open('photo_tags.json', 'w') as f:
            json.dump(st.session_state.photo_tags, f, indent=2)
        st.success(f"Saved {len(st.session_state.photo_tags)} photo tags!")

    st.markdown("---")

    # Display in grid
    cols_per_row = 3
    for row_start in range(0, len(unused_photos), cols_per_row):
        cols = st.columns(cols_per_row)
        row_photos = unused_photos[row_start:row_start + cols_per_row]

        for col_idx, photo_url in enumerate(row_photos):
            with cols[col_idx]:
                try:
                    # Display photo
                    st.image(photo_url, use_container_width=True)

                    # Show filename
                    filename = photo_url.split('/')[-1]
                    st.caption(filename)

                    # Get current tags for this photo (can be multiple)
                    current_tags = st.session_state.photo_tags.get(photo_url, [])
                    if isinstance(current_tags, str):
                        # Convert old single-tag format to list
                        current_tags = [current_tags] if current_tags else []

                    # Multi-name selector
                    selected_names = st.multiselect(
                        "Tag with names:",
                        valid_names,
                        default=current_tags,
                        key=f"tag_{photo_url}",
                        placeholder="Select name(s)...",
                        label_visibility="collapsed"
                    )

                    # Update tags
                    if selected_names:
                        st.session_state.photo_tags[photo_url] = selected_names
                    else:
                        if photo_url in st.session_state.photo_tags:
                            del st.session_state.photo_tags[photo_url]

                    # Show count
                    if selected_names:
                        st.caption(f"Tagged: {', '.join(selected_names)}")

                    st.markdown("---")

                except Exception as e:
                    st.error(f"Error: {str(e)[:30]}")


def main():
    st.title("✏️ Admin - Label People & Photos")
    st.markdown("---")

    # Mode selector
    mode = st.radio(
        "Select mode:",
        ["Label People (Face Detection)", "View Unused Photos"],
        horizontal=True
    )
    st.markdown("---")

    # Load face data
    if 'face_data' not in st.session_state:
        cache_manager = CacheManager()
        with st.spinner("Loading face data..."):
            cache_data = cache_manager.load_cache()
            if cache_data:
                st.session_state.face_data = cache_data
                st.session_state.cluster_labels = np.array(cache_data['cluster_labels'])
                st.session_state.person_clusters = get_person_clusters(
                    st.session_state.cluster_labels
                )
            else:
                st.error("Face cache not found. Please run face processing first.")
                return

    # Load existing names
    if 'person_names' not in st.session_state:
        st.session_state.person_names = load_names()

    # Handle different modes
    if mode == "View Unused Photos":
        show_unused_photos()
        return

    # Statistics
    valid_people = [(pid, faces) for pid, faces in st.session_state.person_clusters.items() if pid >= 0]
    labeled_count = len([pid for pid, _ in valid_people if str(pid) in st.session_state.person_names])

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total People", len(valid_people))
    with col2:
        st.metric("Labeled", labeled_count)
    with col3:
        st.metric("Unlabeled", len(valid_people) - labeled_count)

    st.markdown("---")

    # Add new person section
    st.markdown("### ➕ Create New Person")
    col_new1, col_new2 = st.columns([3, 1])
    with col_new1:
        new_person_name = st.text_input(
            "Add a person not in face detection:",
            placeholder="Enter name...",
            key="new_person_input"
        )
    with col_new2:
        st.markdown("<br>", unsafe_allow_html=True)  # Spacing
        if st.button("Add Person", use_container_width=True):
            if new_person_name and new_person_name.strip():
                # Find next available ID (use negative numbers to avoid conflicts)
                existing_ids = [int(pid) for pid in st.session_state.person_names.keys()]
                new_id = min(existing_ids) - 1 if existing_ids else -1000

                st.session_state.person_names[str(new_id)] = new_person_name.strip()
                save_names(st.session_state.person_names)
                st.success(f"✓ Added '{new_person_name.strip()}' - you can now tag photos with this name!")
                st.rerun()
            else:
                st.error("Please enter a name")

    st.markdown("---")

    # Save button at top
    if st.button("💾 Save All Names", type="primary", use_container_width=True):
        save_names(st.session_state.person_names)
        st.success(f"Saved {len(st.session_state.person_names)} names to {NAMES_FILE}")

    st.markdown("---")
    st.markdown("### Label each person by typing their name:")

    # Display faces in grid
    cols_per_row = 4
    valid_people = [(pid, faces) for pid, faces in st.session_state.person_clusters.items() if pid >= 0]

    for row_start in range(0, len(valid_people), cols_per_row):
        cols = st.columns(cols_per_row)
        row_people = valid_people[row_start:row_start + cols_per_row]

        for col_idx, (person_id, face_indices) in enumerate(row_people):
            with cols[col_idx]:
                # Get first face of this person as representative
                first_face_idx = face_indices[0]
                face_info = st.session_state.face_data['face_to_photo_map'][first_face_idx]

                # Get face thumbnail URL
                try:
                    face_thumb_url = get_face_thumbnail_url(
                        face_info['photo_path'],
                        face_info['location']
                    )

                    # Display face thumbnail
                    st.image(face_thumb_url, use_container_width=True)

                    # Photo count
                    num_photos = get_photos_for_person(
                        st.session_state.face_data,
                        st.session_state.person_clusters,
                        person_id
                    )
                    st.caption(f"Person {person_id} • {num_photos} photos")

                    # Name input
                    current_name = st.session_state.person_names.get(str(person_id), "")
                    new_name = st.text_input(
                        "Name:",
                        value=current_name,
                        key=f"name_{person_id}",
                        placeholder="Type name...",
                        label_visibility="collapsed"
                    )

                    # Update session state if name changed
                    if new_name != current_name:
                        if new_name.strip():
                            st.session_state.person_names[str(person_id)] = new_name.strip()
                        elif str(person_id) in st.session_state.person_names:
                            del st.session_state.person_names[str(person_id)]

                    # Show status
                    if str(person_id) in st.session_state.person_names:
                        st.success("✓ Labeled")
                    else:
                        st.info("Unlabeled")

                except Exception as e:
                    st.error(f"Error: {str(e)[:30]}")

                st.markdown("---")

    # Save button at bottom too
    st.markdown("---")
    if st.button("💾 Save All Names ", type="primary", use_container_width=True, key="save_bottom"):
        save_names(st.session_state.person_names)
        st.success(f"Saved {len(st.session_state.person_names)} names to {NAMES_FILE}")

    # Show current mappings
    if st.session_state.person_names:
        st.markdown("---")
        st.markdown("### Current Name Mappings:")
        st.json(st.session_state.person_names)


if __name__ == "__main__":
    main()
