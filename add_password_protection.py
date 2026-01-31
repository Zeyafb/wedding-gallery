"""
Optional: Add password protection to your wedding gallery

Copy the check_password() function into your app.py main() function
to require a password before guests can view photos.
"""

import streamlit as st
import hashlib


def check_password():
    """
    Returns True if the user has entered the correct password.
    Call this at the start of your main() function.
    """

    def password_hash(password):
        """Hash password for security"""
        return hashlib.sha256(password.encode()).hexdigest()

    # ==========================================================================
    # SET YOUR PASSWORD HERE!
    # ==========================================================================
    # Option 1: Simple password (less secure, easier)
    CORRECT_PASSWORD = "WeddingDay2024"

    # Option 2: Pre-hashed password (more secure)
    # Generate hash by running: python -c "import hashlib; print(hashlib.sha256('YourPassword'.encode()).hexdigest())"
    # CORRECT_PASSWORD_HASH = "your-hash-here"
    # ==========================================================================

    # Initialize session state
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False

    # If already authenticated, return True
    if st.session_state.authenticated:
        return True

    # Show login form
    st.title("🔒 Wedding Photo Gallery")
    st.markdown("---")

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown("### Welcome!")
        st.markdown("Please enter the password to view photos.")

        password_input = st.text_input(
            "Password:",
            type="password",
            placeholder="Enter password..."
        )

        col_login, col_hint = st.columns(2)

        with col_login:
            if st.button("🔓 Login", use_container_width=True, type="primary"):
                if password_input == CORRECT_PASSWORD:
                    st.session_state.authenticated = True
                    st.success("✅ Access granted!")
                    st.rerun()
                else:
                    st.error("❌ Incorrect password")

        with col_hint:
            if st.button("💡 Hint", use_container_width=True):
                st.info("Check your wedding invitation or ask the couple!")

    st.markdown("---")
    st.caption("💒 This gallery is password-protected to keep our special moments private.")

    # Stop execution here if not authenticated
    st.stop()


# =============================================================================
# HOW TO USE
# =============================================================================
"""
Add this to the top of your main() function in app.py:

def main():
    init_session_state()

    # Add password protection (uncomment to enable)
    check_password()

    # ... rest of your app code
"""
