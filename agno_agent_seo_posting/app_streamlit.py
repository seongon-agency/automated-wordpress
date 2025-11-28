"""
Streamlit App for WordPress SEO Publishing System - LOCAL VERSION

Test the local workflow directly (no FastAPI required).
"""

import streamlit as st
import sys
import os
from pathlib import Path
import time
from dotenv import load_dotenv

# Load environment variables (for local development fallback)
load_dotenv()


def get_secret(key: str, default=None):
    """
    Get a secret value with fallback chain:
    1. Streamlit secrets (st.secrets) - for Streamlit Cloud deployment
    2. Environment variable (os.getenv) - for local development
    3. Default value
    """
    # Try Streamlit secrets first
    try:
        if hasattr(st, 'secrets') and key in st.secrets:
            return st.secrets[key]
    except Exception:
        pass

    # Fall back to environment variable
    env_value = os.getenv(key)
    if env_value is not None:
        return env_value

    return default


# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from src.database import (
    init_database,
    create_project,
    list_projects,
    get_project,
    delete_project,
    update_project
)
from src.workflows.publishing_workflow import execute_publishing_workflow
import json
import anthropic

# ============================================
# Page Configuration
# ============================================

st.set_page_config(
    page_title="WordPress SEO Publisher",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database
init_database()

# Initialize session state for navigation
if 'current_page' not in st.session_state:
    st.session_state.current_page = "Home"

# ============================================
# Sidebar - Navigation
# ============================================

st.sidebar.title("WordPress SEO Publisher")
st.sidebar.caption("Local Development • AI-Powered")

st.sidebar.markdown("")

# Quick action button
if st.sidebar.button("Quick Publish", type="primary", use_container_width=True):
    st.session_state.current_page = "Publish Content"

st.sidebar.markdown("---")

# Navigation sections
st.sidebar.subheader("Overview")
if st.sidebar.button("Dashboard", use_container_width=True,
                      disabled=(st.session_state.current_page == "Home")):
    st.session_state.current_page = "Home"

st.sidebar.markdown("")
st.sidebar.subheader("Projects")
col1, col2 = st.sidebar.columns(2)
with col1:
    if st.button("View", use_container_width=True, key="view_projects"):
        st.session_state.current_page = "Projects"
with col2:
    if st.button("New", use_container_width=True, key="new_project"):
        st.session_state.current_page = "Create Project"

if st.sidebar.button("Edit Project Settings", use_container_width=True):
    st.session_state.current_page = "Edit Project"

st.sidebar.markdown("")
st.sidebar.subheader("AI Configuration")
if st.sidebar.button("Edit HTML Patterns (Natural Language)", use_container_width=True):
    st.session_state.current_page = "AI Pattern Editor"
if st.sidebar.button("Scan & Generate Patterns", use_container_width=True):
    st.session_state.current_page = "Scan HTML Template"

st.sidebar.markdown("")
st.sidebar.subheader("Publishing")
if st.sidebar.button("Publish Single Content", use_container_width=True):
    st.session_state.current_page = "Publish Content"
if st.sidebar.button("Batch Publish (Multiple)", use_container_width=True):
    st.session_state.current_page = "Batch Publish"
if st.sidebar.button("View Publishing History", use_container_width=True):
    st.session_state.current_page = "Publishing History"

st.sidebar.markdown("---")

# Quick stats in sidebar
try:
    projects = list_projects(status='all')
    col1, col2 = st.sidebar.columns(2)
    with col1:
        st.metric("Projects", len(projects))
    with col2:
        st.metric("Status", "Ready")
except:
    pass

st.sidebar.markdown("---")
st.sidebar.caption("**Tip:** Use Quick Publish for fast access")
st.sidebar.caption("**Tech:** SQLite • Python • Claude AI")

# Set page from session state
page = st.session_state.current_page

# ============================================
# Page: Home
# ============================================

if page == "Home":
    st.title("WordPress SEO Publishing System")
    st.markdown("### Local Development Version")
    st.markdown("---")

    st.markdown("""
    ## Welcome!

    This is the **local development version** of the WordPress SEO Publishing System.

    ### System Features:

    1. **Project Management**
       - Create and manage WordPress projects
       - Each project stores WordPress credentials and HTML transformation patterns
       - Supports multiple WordPress sites

    2. **Content Publishing**
       - Publish Google Docs to WordPress
       - Automatic HTML transformation based on project templates
       - Image processing and upload to WordPress media library
       - Creates draft posts by default for safety

    3. **Complete Workflow**
       - Convert Google Docs → HTML
       - Process images (download, resize, upload)
       - Apply HTML transformations
       - Publish to WordPress
       - Track publishing history

    ### Quick Start:

    1. **Setup Google OAuth** - Place `client_secret.json` in `credentials/` folder
    2. **Create a Project** - Add your WordPress site details
    3. **Prepare Content** - Write content in Google Docs
    4. **Publish** - Select project and paste any Google Docs URL (edit/view/published)
    5. **Done!** - Get the WordPress post URL

    ---
    """)

    # Show quick stats
    col1, col2, col3 = st.columns(3)

    with col1:
        try:
            projects = list_projects(status='all')
            st.metric("Total Projects", len(projects))
        except:
            st.metric("Total Projects", "0")

    with col2:
        st.metric("System Status", "Ready")

    with col3:
        st.metric("Version", "1.0.0")

    st.markdown("---")

    st.info("**Use the sidebar to navigate** between pages")

# ============================================
# Page: Projects
# ============================================

elif page == "Projects":
    st.title("Projects")
    st.markdown("---")

    # Fetch all projects
    try:
        projects = list_projects(status='all')

        if projects:
            st.success(f"Found {len(projects)} project(s)")

            for project in projects:
                with st.expander(f"{project['project_name']} ({project['project_id']})"):
                    col1, col2 = st.columns([3, 1])

                    with col1:
                        st.markdown(f"**Project ID:** `{project['project_id']}`")
                        st.markdown(f"**WordPress URL:** {project['wordpress_url']}")
                        st.markdown(f"**Username:** {project['wordpress_username']}")
                        st.markdown(f"**Status:** {project['status']}")
                        st.markdown(f"**Created:** {project.get('created_at', 'N/A')}")

                        # Show HTML patterns count
                        html_configs = project.get('html_configs')
                        if html_configs and html_configs.get('patterns'):
                            st.markdown(f"**HTML Patterns:** {len(html_configs['patterns'])} configured")
                        else:
                            st.markdown("**HTML Patterns:** None configured")

                        # Show image config
                        image_configs = project.get('image_configs')
                        if image_configs:
                            st.markdown(f"**Image Width:** {image_configs.get('target_width', 800)}px")
                            st.markdown(f"**Image Quality:** {image_configs.get('image_quality', 92)}")
                        else:
                            st.markdown("**Image Settings:** Using defaults")

                    with col2:
                        if st.button("Delete", key=f"del_{project['project_id']}"):
                            try:
                                delete_project(project['project_id'])
                                st.success("Project deleted!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Failed to delete: {e}")

        else:
            st.info("No projects found. Create your first project!")

    except Exception as e:
        st.error(f"Error loading projects: {e}")

# ============================================
# Page: Create Project
# ============================================

elif page == "Create Project":
    st.title("Create New Project")
    st.markdown("---")

    st.markdown("""
    ### What is a Project?

    A **project** represents a WordPress site where you'll publish content. Each project stores:
    - WordPress site URL and credentials
    - HTML transformation patterns (optional)
    - Image processing settings (optional)

    Once configured, you can publish multiple articles to the same project without reconfiguring.
    """)

    st.markdown("---")

    # Image resize method selection OUTSIDE form so it updates immediately
    # Initialize session state for resize method if not set
    if 'create_resize_method' not in st.session_state:
        st.session_state.create_resize_method = "Fixed Width"

    st.markdown("### Image Resizing Method")
    resize_options = ["Fixed Width", "Google Docs Original Size", "No Resize (Original Quality)"]
    current_index = resize_options.index(st.session_state.create_resize_method) if st.session_state.create_resize_method in resize_options else 0
    resize_method = st.radio(
        "Select how images should be resized",
        options=resize_options,
        index=current_index,
        help="Fixed Width: Resize all images to a specific width. Google Docs Original: Use dimensions from Google Docs. No Resize: Upload original images without any processing (best quality).",
        key="create_resize_method_selector"
    )
    # Update session state
    st.session_state.create_resize_method = resize_method

    with st.form("create_project_form"):
        st.markdown("### Basic Information")

        project_id = st.text_input(
            "Project ID *",
            placeholder="e.g., my_blog_2024",
            help="Unique identifier (lowercase, underscores only). This cannot be changed later."
        )

        project_name = st.text_input(
            "Project Name *",
            placeholder="e.g., My Awesome Blog",
            help="Display name for this project"
        )

        st.markdown("### WordPress Configuration")

        wp_url = st.text_input(
            "WordPress Site URL *",
            placeholder="https://your-wordpress-site.com",
            help="Full URL to your WordPress site (no trailing slash)"
        )

        wp_username = st.text_input(
            "WordPress Username *",
            placeholder="admin",
            help="Your WordPress username"
        )

        wp_password = st.text_input(
            "WordPress Application Password *",
            type="password",
            placeholder="xxxx xxxx xxxx xxxx",
            help="NOT your regular password! Get from: WordPress Admin → Users → Profile → Application Passwords"
        )

        st.markdown("### Image Settings (Optional)")

        # Show different settings based on resize method from session state
        if st.session_state.create_resize_method == "Fixed Width":
            st.markdown("#### Fixed Width Settings")
            col1, col2 = st.columns(2)

            with col1:
                image_width = st.number_input(
                    "Target Image Width (px)",
                    min_value=100,
                    max_value=2000,
                    value=800,
                    key="create_fixed_width",
                    help="Images will be resized to this width while maintaining aspect ratio"
                )

                image_quality = st.slider(
                    "Image Quality (%)",
                    min_value=50,
                    max_value=100,
                    value=92,
                    key="create_fixed_quality",
                    help="Higher = better quality but larger file size"
                )

            with col2:
                image_format = st.selectbox(
                    "Image Format",
                    options=["JPEG", "PNG", "WEBP"],
                    index=0,
                    key="create_fixed_format",
                    help="Output format for processed images"
                )

        elif st.session_state.create_resize_method == "Google Docs Original Size":
            st.markdown("#### Google Docs Original Size Settings")
            st.info("🎯 Images will be resized to their exact dimensions from Google Docs (width and height from <img> tags)")

            col1, col2 = st.columns(2)

            with col1:
                image_quality = st.slider(
                    "Image Quality (%)",
                    min_value=50,
                    max_value=100,
                    value=92,
                    key="create_gdocs_quality",
                    help="Higher = better quality but larger file size"
                )

            with col2:
                image_format = st.selectbox(
                    "Image Format",
                    options=["JPEG", "PNG", "WEBP"],
                    index=0,
                    key="create_gdocs_format",
                    help="Output format for processed images"
                )

            # Set default width for backend (not used in google_docs_original mode)
            image_width = 800

        else:
            # No Resize (Original Quality)
            st.markdown("#### Original Quality Settings")
            st.success("✨ Images will be uploaded exactly as they are from Google Docs - no resizing, no re-encoding. Best quality!")
            st.info("Note: Original images may be large. Make sure your WordPress can handle them.")

            # Set defaults (not used in no_resize mode)
            image_width = 800
            image_quality = 100
            image_format = "PNG"

        st.markdown("### Image Naming")

        naming_method = st.selectbox(
            "Image Naming Method",
            options=["Default (project_name)", "Alt Text Based", "Main Keyword Based"],
            index=0,
            key="create_naming_method",
            help="How to name downloaded images"
        )

        if naming_method == "Alt Text Based":
            st.info("📝 Images will be named using the first N words of their alt text (slug format). Images without alt text will be named 'unnamed-image-1', 'unnamed-image-2', etc.")
            alt_text_words = st.number_input(
                "Number of words from alt text",
                min_value=1,
                max_value=20,
                value=5,
                key="create_alt_text_words",
                help="How many words from the alt text to use for the filename"
            )
        elif naming_method == "Main Keyword Based":
            st.info("🔑 Images will be named using a main keyword you provide when publishing (e.g., 'main-keyword-01', 'main-keyword-02')")
            alt_text_words = 5  # default, not used
        else:
            st.info("📁 Images will be named using the project ID (e.g., 'projectname_1', 'projectname_2')")
            alt_text_words = 5  # default, not used

        st.markdown("### Caption Options")

        enable_auto_captions = st.checkbox(
            "Enable Automatic WordPress Captions",
            value=True,
            help="Automatically wrap images with WordPress [caption] shortcodes. Disable this if you want to control caption formatting with HTML patterns."
        )

        st.markdown("### Google Drive Backup (Optional)")

        google_drive_folder_url = st.text_input(
            "Google Drive Folder URL",
            placeholder="https://drive.google.com/drive/folders/...",
            help="Optional: Paste a Google Drive folder URL to automatically backup images. A subfolder will be created for each post."
        )

        if google_drive_folder_url:
            st.info("📁 Images will be backed up to Google Drive before WordPress upload. A subfolder named after the post title will be created.")

        st.markdown("### Notes (Optional)")

        notes = st.text_area(
            "Project Notes",
            placeholder="Any notes about this project...",
            help="Optional notes for reference"
        )

        st.markdown("---")
        submit = st.form_submit_button("Create Project", type="primary", use_container_width=True)

        if submit:
            # Validation
            if not all([project_id, project_name, wp_url, wp_username, wp_password]):
                st.error("Please fill in all required fields (marked with *)")
            else:
                try:
                    # Prepare image configs
                    # Convert UI label to backend key (from session state)
                    if st.session_state.create_resize_method == "Fixed Width":
                        resize_method_key = "fixed_width"
                    elif st.session_state.create_resize_method == "Google Docs Original Size":
                        resize_method_key = "google_docs_original"
                    else:
                        resize_method_key = "no_resize"

                    # Convert naming method to backend key
                    naming_method_key = "default"
                    if naming_method == "Alt Text Based":
                        naming_method_key = "alt_text"
                    elif naming_method == "Main Keyword Based":
                        naming_method_key = "main_keyword"

                    image_configs = {
                        "resize_method": resize_method_key,
                        "target_width": image_width,
                        "image_quality": image_quality,
                        "image_format": image_format,
                        "enable_auto_captions": enable_auto_captions,
                        "naming_method": naming_method_key,
                        "alt_text_words": alt_text_words,
                        "google_drive_folder_url": google_drive_folder_url.strip() if google_drive_folder_url else ""
                    }

                    # Create project
                    with st.spinner("Creating project..."):
                        result = create_project(
                            project_id=project_id,
                            project_name=project_name,
                            wordpress_url=wp_url,
                            wordpress_username=wp_username,
                            wordpress_app_password=wp_password,
                            image_configs=image_configs,
                            notes=notes if notes else None
                        )

                    st.success("Project created successfully!")
                    st.info("You can now publish content to this project. Go to 'Publish Content' page.")

                    # Show summary
                    st.json(result)

                except Exception as e:
                    st.error(f"Failed to create project: {e}")

# ============================================
# Page: Edit Project
# ============================================

elif page == "Edit Project":
    st.title("Edit Project")
    st.markdown("---")

    st.markdown("""
    ### Update Project Settings

    Modify WordPress credentials, image settings, or other project configuration.
    """)

    st.markdown("---")

    # Fetch projects
    try:
        projects = list_projects(status='all')

        if not projects:
            st.warning("No projects found. Please create a project first.")
        else:
            # Select project to edit
            project_options = {f"{p['project_name']} ({p['project_id']})": p['project_id'] for p in projects}

            selected_display = st.selectbox(
                "Select Project to Edit",
                options=list(project_options.keys()),
                help="Choose which project to modify"
            )
            selected_project_id = project_options[selected_display]

            # Load current project data
            current_project = get_project(selected_project_id)

            # Reset session state if project changed
            if 'edit_project_id' not in st.session_state or st.session_state.edit_project_id != selected_project_id:
                st.session_state.edit_project_id = selected_project_id
                # Clear cached values so they reload from database
                if 'edit_resize_method' in st.session_state:
                    del st.session_state.edit_resize_method
                if 'edit_naming_method_state' in st.session_state:
                    del st.session_state.edit_naming_method_state

            st.markdown("---")
            st.markdown(f"### Editing: **{current_project['project_name']}**")

            # Image resize method selection OUTSIDE form so it updates immediately
            current_image_config = current_project.get('image_configs') or {}
            current_resize_method = current_image_config.get('resize_method', 'fixed_width')

            # Map backend key to UI label
            resize_method_map = {
                'fixed_width': 'Fixed Width',
                'google_docs_original': 'Google Docs Original Size',
                'no_resize': 'No Resize (Original Quality)'
            }
            current_resize_method_label = resize_method_map.get(current_resize_method, 'Fixed Width')

            # Initialize session state for resize method if not set
            if 'edit_resize_method' not in st.session_state:
                st.session_state.edit_resize_method = current_resize_method_label

            st.markdown("#### Image Resizing Method")
            edit_resize_options = ["Fixed Width", "Google Docs Original Size", "No Resize (Original Quality)"]
            current_edit_index = edit_resize_options.index(st.session_state.edit_resize_method) if st.session_state.edit_resize_method in edit_resize_options else 0
            new_resize_method = st.radio(
                "Select how images should be resized",
                options=edit_resize_options,
                index=current_edit_index,
                help="Fixed Width: Resize to specific width. Google Docs Original: Use dimensions from Google Docs. No Resize: Upload original images (best quality).",
                key="resize_method_selector"
            )
            # Update session state
            st.session_state.edit_resize_method = new_resize_method

            # Image naming method selection OUTSIDE form so it updates immediately
            st.markdown("#### Image Naming Method")

            # Get current naming method from database
            current_naming_method = current_image_config.get('naming_method', 'default')

            # Map backend key to UI label
            naming_method_map = {
                'default': 'Default (project_name)',
                'alt_text': 'Alt Text Based',
                'main_keyword': 'Main Keyword Based'
            }
            current_naming_method_label = naming_method_map.get(current_naming_method, 'Default (project_name)')

            # Initialize session state for naming method if not set
            if 'edit_naming_method_state' not in st.session_state:
                st.session_state.edit_naming_method_state = current_naming_method_label

            edit_naming_options = ["Default (project_name)", "Alt Text Based", "Main Keyword Based"]
            current_naming_index = edit_naming_options.index(st.session_state.edit_naming_method_state) if st.session_state.edit_naming_method_state in edit_naming_options else 0

            new_naming_method_outside = st.radio(
                "Select how images should be named",
                options=edit_naming_options,
                index=current_naming_index,
                help="Default: Uses project name. Alt Text: Uses image alt text. Main Keyword: You provide a keyword when publishing.",
                key="naming_method_selector"
            )
            # Update session state
            st.session_state.edit_naming_method_state = new_naming_method_outside

            # Show info based on selection
            if new_naming_method_outside == "Alt Text Based":
                st.info("📝 Images will be named using the first N words of their alt text (slug format).")
            elif new_naming_method_outside == "Main Keyword Based":
                st.info("🔑 Images will be named using a main keyword you provide when publishing (e.g., 'main-keyword-01', 'main-keyword-02')")
            else:
                st.info("📁 Images will be named using the project ID (e.g., 'projectname_1', 'projectname_2')")

            with st.form("edit_project_form"):
                st.markdown("#### Basic Information")

                new_project_name = st.text_input(
                    "Project Name",
                    value=current_project['project_name'],
                    help="Display name for this project"
                )

                st.markdown("#### WordPress Configuration")

                new_wp_url = st.text_input(
                    "WordPress Site URL",
                    value=current_project['wordpress_url'],
                    help="Full URL to your WordPress site"
                )

                new_wp_username = st.text_input(
                    "WordPress Username",
                    value=current_project['wordpress_username'],
                    help="Your WordPress username"
                )

                new_wp_password = st.text_input(
                    "WordPress Application Password",
                    type="password",
                    placeholder="Leave empty to keep current password",
                    help="Enter new password or leave empty to keep existing"
                )

                st.markdown("#### Image Settings")

                # Show different settings based on resize method from session state
                if st.session_state.edit_resize_method == "Fixed Width":
                    st.markdown("##### Fixed Width Settings")
                    col1, col2 = st.columns(2)

                    with col1:
                        new_image_width = st.number_input(
                            "Target Image Width (px)",
                            min_value=100,
                            max_value=2000,
                            value=current_image_config.get('target_width', 800),
                            key="edit_fixed_width",
                            help="Images will be resized to this width while maintaining aspect ratio"
                        )

                        new_image_quality = st.slider(
                            "Image Quality (%)",
                            min_value=50,
                            max_value=100,
                            value=current_image_config.get('image_quality', 92),
                            key="edit_fixed_quality",
                            help="Higher = better quality but larger file size"
                        )

                    with col2:
                        new_image_format = st.selectbox(
                            "Image Format",
                            options=["JPEG", "PNG", "WEBP"],
                            index=["JPEG", "PNG", "WEBP"].index(current_image_config.get('image_format', 'JPEG')),
                            key="edit_fixed_format",
                            help="Output format for processed images"
                        )

                elif st.session_state.edit_resize_method == "Google Docs Original Size":
                    st.markdown("##### Google Docs Original Size Settings")
                    st.info("🎯 Images will be resized to their exact dimensions from Google Docs (width and height from <img> tags)")

                    col1, col2 = st.columns(2)

                    with col1:
                        new_image_quality = st.slider(
                            "Image Quality (%)",
                            min_value=50,
                            max_value=100,
                            value=current_image_config.get('image_quality', 92),
                            key="edit_gdocs_quality",
                            help="Higher = better quality but larger file size"
                        )

                    with col2:
                        new_image_format = st.selectbox(
                            "Image Format",
                            options=["JPEG", "PNG", "WEBP"],
                            index=["JPEG", "PNG", "WEBP"].index(current_image_config.get('image_format', 'JPEG')),
                            key="edit_gdocs_format",
                            help="Output format for processed images"
                        )

                    # Keep existing width value (not used in google_docs_original mode)
                    new_image_width = current_image_config.get('target_width', 800)

                else:
                    # No Resize (Original Quality)
                    st.markdown("##### Original Quality Settings")
                    st.success("✨ Images will be uploaded exactly as they are from Google Docs - no resizing, no re-encoding. Best quality!")
                    st.info("Note: Original images may be large. Make sure your WordPress can handle them.")

                    # Set defaults (not used in no_resize mode)
                    new_image_width = current_image_config.get('target_width', 800)
                    new_image_quality = 100
                    new_image_format = current_image_config.get('image_format', 'PNG')

                # Alt text words setting (for Alt Text Based naming)
                if st.session_state.edit_naming_method_state == "Alt Text Based":
                    new_alt_text_words = st.number_input(
                        "Number of words from alt text",
                        min_value=1,
                        max_value=20,
                        value=current_image_config.get('alt_text_words', 5),
                        key="edit_alt_text_words",
                        help="How many words from the alt text to use for the filename"
                    )
                else:
                    new_alt_text_words = current_image_config.get('alt_text_words', 5)  # keep existing

                st.markdown("#### Caption Options")

                new_enable_auto_captions = st.checkbox(
                    "Enable Automatic WordPress Captions",
                    value=current_image_config.get('enable_auto_captions', True),
                    help="Automatically wrap images with WordPress [caption] shortcodes. Disable this if you want to control caption formatting with HTML patterns."
                )

                st.markdown("#### Google Drive Backup (Optional)")

                new_google_drive_folder_url = st.text_input(
                    "Google Drive Folder URL",
                    value=current_image_config.get('google_drive_folder_url', ''),
                    placeholder="https://drive.google.com/drive/folders/...",
                    help="Optional: Paste a Google Drive folder URL to automatically backup images. A subfolder will be created for each post."
                )

                if new_google_drive_folder_url:
                    st.info("📁 Images will be backed up to Google Drive before WordPress upload.")

                st.markdown("#### Notes")

                new_notes = st.text_area(
                    "Project Notes",
                    value=current_project.get('notes', ''),
                    help="Optional notes for reference"
                )

                st.markdown("---")
                submit = st.form_submit_button("Save Changes", type="primary", use_container_width=True)

                if submit:
                    try:
                        # Prepare updates
                        # Convert UI label to backend key (from session state)
                        if st.session_state.edit_resize_method == "Fixed Width":
                            new_resize_method_key = "fixed_width"
                        elif st.session_state.edit_resize_method == "Google Docs Original Size":
                            new_resize_method_key = "google_docs_original"
                        else:
                            new_resize_method_key = "no_resize"

                        # Convert naming method to backend key (from session state)
                        new_naming_method_key = "default"
                        if st.session_state.edit_naming_method_state == "Alt Text Based":
                            new_naming_method_key = "alt_text"
                        elif st.session_state.edit_naming_method_state == "Main Keyword Based":
                            new_naming_method_key = "main_keyword"

                        updates = {
                            'project_name': new_project_name,
                            'wordpress_url': new_wp_url,
                            'wordpress_username': new_wp_username,
                            'image_configs': {
                                'resize_method': new_resize_method_key,
                                'target_width': new_image_width,
                                'image_quality': new_image_quality,
                                'image_format': new_image_format,
                                'enable_auto_captions': new_enable_auto_captions,
                                'naming_method': new_naming_method_key,
                                'alt_text_words': new_alt_text_words,
                                'google_drive_folder_url': new_google_drive_folder_url.strip() if new_google_drive_folder_url else ""
                            },
                            'notes': new_notes if new_notes else None
                        }

                        # Only update password if provided
                        if new_wp_password:
                            updates['wordpress_app_password'] = new_wp_password

                        # Update project
                        with st.spinner("Saving changes..."):
                            result = update_project(selected_project_id, **updates)

                        st.success("Project updated successfully!")
                        st.balloons()

                        # Clear session state so next edit reloads from database
                        if 'edit_naming_method_state' in st.session_state:
                            del st.session_state.edit_naming_method_state
                        if 'edit_resize_method' in st.session_state:
                            del st.session_state.edit_resize_method
                        if 'edit_project_id' in st.session_state:
                            del st.session_state.edit_project_id

                        # Show what changed
                        with st.expander("Updated Project Details"):
                            st.json(result)

                    except Exception as e:
                        st.error(f"Failed to update project: {e}")

    except Exception as e:
        st.error(f"Error loading projects: {e}")

# ============================================
# Page: AI Pattern Editor
# ============================================

elif page == "AI Pattern Editor":
    st.title("AI Pattern Editor")
    st.markdown("### Modify HTML Patterns with Natural Language")
    st.markdown("---")

    st.markdown("""
    Use **AI-powered natural language** to modify your project's HTML transformation patterns.

    **Examples:**
    - "Make all h2 headings blue"
    - "Add a class 'highlight' to all paragraphs"
    - "Make links open in new tab"
    - "Remove all styling from images"
    """)

    st.markdown("---")

    # Initialize session state for modified patterns
    if 'modified_patterns' not in st.session_state:
        st.session_state.modified_patterns = None
    if 'modified_patterns_project_id' not in st.session_state:
        st.session_state.modified_patterns_project_id = None
    if 'pattern_changes_made' not in st.session_state:
        st.session_state.pattern_changes_made = None

    # Fetch projects
    try:
        projects = list_projects(status='all')

        if not projects:
            st.warning("No projects found. Please create a project first.")
        else:
            # Select project
            project_options = {f"{p['project_name']} ({p['project_id']})": p['project_id'] for p in projects}

            selected_display = st.selectbox(
                "Select Project",
                options=list(project_options.keys()),
                help="Choose which project's patterns to modify"
            )
            selected_project_id = project_options[selected_display]

            # Load project
            project = get_project(selected_project_id)
            html_configs = project.get('html_configs') or {}
            current_patterns = html_configs.get('patterns', [])

            st.markdown("---")

            if not current_patterns:
                st.warning("This project has no HTML patterns configured yet. Use 'Scan HTML Template' to generate patterns first.")
            else:
                st.success(f"Project has **{len(current_patterns)}** pattern(s) configured")

                # Show current patterns with delete buttons
                with st.expander("View & Manage Current Patterns", expanded=True):
                    st.markdown("**Click the delete button to remove a pattern**")

                    for idx, pattern in enumerate(current_patterns):
                        col1, col2 = st.columns([10, 1])

                        with col1:
                            st.markdown(f"**Pattern {idx + 1}: `{pattern.get('element_type', 'unknown')}`**")
                            st.code(f"Source: {pattern.get('source_pattern', 'N/A')}\nTarget: {pattern.get('target_pattern', 'N/A')}", language="html")

                        with col2:
                            if st.button("🗑️", key=f"delete_pattern_{idx}", help=f"Delete pattern {idx + 1}"):
                                # Remove pattern from list
                                updated_patterns = [p for i, p in enumerate(current_patterns) if i != idx]

                                # Update database
                                try:
                                    from src.database import update_project

                                    updated_html_configs = {**html_configs, 'patterns': updated_patterns}
                                    update_project(selected_project_id, html_configs=updated_html_configs)

                                    st.success(f"Pattern {idx + 1} ({pattern.get('element_type')}) deleted successfully!")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Failed to delete pattern: {e}")

                        if idx < len(current_patterns) - 1:
                            st.markdown("---")

                st.markdown("---")
                st.markdown("### Natural Language Instructions")

                # Natural language input
                instruction = st.text_area(
                    "What changes do you want to make?",
                    placeholder="e.g., Make all h2 headings blue and add a bottom margin",
                    help="Describe the changes you want in plain English"
                )

                if st.button("Apply Changes with AI", type="primary", disabled=not instruction):
                    if instruction:
                        with st.spinner("AI is analyzing your instruction and modifying patterns..."):
                            try:
                                # Import the pattern modifier
                                from src.utils.pattern_modifier import modify_patterns_with_ai

                                # Get API key
                                api_key = get_secret('ANTHROPIC_API_KEY')
                                if not api_key:
                                    st.error("ANTHROPIC_API_KEY not found in secrets or environment variables")
                                else:
                                    # Modify patterns
                                    result = modify_patterns_with_ai(
                                        current_patterns=current_patterns,
                                        instruction=instruction,
                                        api_key=api_key
                                    )

                                    if result['success']:
                                        # Store in session state for persistence
                                        st.session_state.modified_patterns = result['patterns']
                                        st.session_state.modified_patterns_project_id = selected_project_id
                                        st.session_state.pattern_changes_made = result['changes_made']

                                        st.success("Patterns modified successfully!")
                                        st.info("Scroll down to review and save the changes.")

                                    else:
                                        st.error(f"AI modification failed: {result.get('error', 'Unknown error')}")

                            except Exception as e:
                                st.error(f"Error: {e}")
                                import traceback
                                with st.expander("Error Details"):
                                    st.code(traceback.format_exc())

            # Display modified patterns from session state (outside button scope)
            if st.session_state.modified_patterns and st.session_state.modified_patterns_project_id == selected_project_id:
                st.markdown("---")
                st.markdown("### Modified Patterns")

                # Show what changed
                if st.session_state.pattern_changes_made:
                    st.info(f"**Changes Made:** {st.session_state.pattern_changes_made}")

                # Show new patterns
                with st.expander("View Updated Patterns", expanded=True):
                    st.json(st.session_state.modified_patterns)

                # Save/Discard buttons
                st.markdown("---")
                st.markdown("### Save Changes?")

                col1, col2 = st.columns(2)

                with col1:
                    if st.button("Save to Project", type="primary", use_container_width=True, key="save_modified_patterns_btn"):
                        try:
                            # Get current project config
                            current_project = get_project(st.session_state.modified_patterns_project_id)
                            current_html_configs = current_project.get('html_configs') or {}

                            # Merge new patterns with existing config
                            updated_html_configs = {**current_html_configs}
                            updated_html_configs['patterns'] = st.session_state.modified_patterns

                            # Update project with merged config
                            update_project(
                                st.session_state.modified_patterns_project_id,
                                html_configs=updated_html_configs
                            )

                            # Clear session state
                            st.session_state.modified_patterns = None
                            st.session_state.modified_patterns_project_id = None
                            st.session_state.pattern_changes_made = None

                            st.success("Patterns saved to project!")
                            st.balloons()
                            st.info("You can now use these patterns when publishing content!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Failed to save: {e}")
                            import traceback
                            st.code(traceback.format_exc())

                with col2:
                    if st.button("Discard Changes", use_container_width=True, key="discard_modified_patterns_btn"):
                        # Clear session state
                        st.session_state.modified_patterns = None
                        st.session_state.modified_patterns_project_id = None
                        st.session_state.pattern_changes_made = None
                        st.info("Changes discarded. Patterns not saved.")
                        st.rerun()

    except Exception as e:
        st.error(f"Error loading projects: {e}")

# ============================================
# Page: Scan HTML Template
# ============================================

elif page == "Scan HTML Template":
    st.title("Scan HTML Template")
    st.markdown("### Auto-Generate Patterns from Sample HTML")
    st.markdown("---")

    st.markdown("""
    **How it works:**
    1. **🧪 Test Run (Optional)**: Paste a Google Docs URL and convert it to see the exact HTML structure
    2. Paste **TARGET HTML** - how you want content formatted in WordPress (required)
    3. **SOURCE HTML** will be auto-filled from Test Run, or paste manually (recommended for better accuracy)
    4. AI analyzes both and generates precise transformation patterns
    5. Review and save patterns to your project

    **Tips for best results:**
    - **Use Test Run**: Get the exact HTML structure from Google Docs automatically
    - **Target HTML**: Copy formatted content from your WordPress theme (HTML view)
    - **Source HTML**: Will be populated by Test Run, or paste manually
    - Include examples of all element types (headings, paragraphs, images, lists, tables, etc.)
    - Providing both source and target yields the most accurate regex patterns
    """)

    st.markdown("---")

    # Initialize session state for generated patterns
    if 'generated_patterns' not in st.session_state:
        st.session_state.generated_patterns = None
    if 'patterns_project_id' not in st.session_state:
        st.session_state.patterns_project_id = None

    # Select project
    try:
        projects = list_projects(status='all')

        if not projects:
            st.warning("No projects found. Please create a project first.")
        else:
            project_options = {f"{p['project_name']} ({p['project_id']})": p['project_id'] for p in projects}

            selected_display = st.selectbox(
                "Select Project",
                options=list(project_options.keys()),
                help="Patterns will be saved to this project"
            )
            selected_project_id = project_options[selected_display]

            st.markdown("---")

            # Initialize session state for converted docs HTML
            if 'converted_docs_html' not in st.session_state:
                st.session_state.converted_docs_html = ""

            # Test Google Docs Conversion Section
            with st.expander("🧪 Test Run: Convert Google Docs to HTML (Optional)", expanded=False):
                st.markdown("""
                **Why use this?**
                - See the exact HTML structure that Google Docs exports
                - Automatically cleaned (H1 and everything before removed)
                - Auto-fills the Source HTML field below
                - More accurate pattern generation

                **How it works:**
                1. Paste any Google Docs URL
                2. Click "Convert to HTML"
                3. HTML is converted and cleaned (H1 removed)
                4. Cleaned HTML auto-fills the Source HTML field below

                **What gets cleaned:**
                - Extracts title from H1 (for display)
                - Removes H1 and everything before it
                - This matches the actual publishing workflow
                """)

                test_docs_url = st.text_input(
                    "Google Docs URL",
                    placeholder="https://docs.google.com/document/d/YOUR_DOC_ID/edit",
                    help="Any Google Docs URL (edit, view, or published)"
                )

                col1, col2 = st.columns([1, 3])
                with col1:
                    convert_btn = st.button("Convert to HTML", type="secondary", use_container_width=True)

                if convert_btn and test_docs_url:
                    with st.spinner("Converting Google Docs to HTML..."):
                        try:
                            # Force reload to get latest code
                            import sys
                            import importlib
                            if 'src.tools.google_docs_converter' in sys.modules:
                                importlib.reload(sys.modules['src.tools.google_docs_converter'])

                            from src.tools.google_docs_converter import google_docs_to_html, _get_credentials_paths
                            import os

                            # Debug: Show credential paths (calculated at runtime)
                            credentials_dir, token_path, client_secrets = _get_credentials_paths()
                            st.info(f"🔍 Looking for credentials in: {credentials_dir}")
                            st.info(f"🔍 Client secrets path: {client_secrets}")
                            st.info(f"🔍 Token path: {token_path}")
                            st.info(f"🔍 Client secrets exists: {os.path.exists(client_secrets)}")
                            st.info(f"🔍 Token exists: {os.path.exists(token_path)}")
                            st.info(f"🔍 Client secrets readable: {os.access(client_secrets, os.R_OK)}")

                            result = google_docs_to_html(test_docs_url)

                            if result['success']:
                                # Clean the HTML: remove H1 and everything before it
                                from src.utils.html_extractor import clean_html_for_wordpress, extract_title_from_html

                                raw_html = result['raw_html']
                                title = extract_title_from_html(raw_html)
                                cleaned_html = clean_html_for_wordpress(raw_html)

                                # Store cleaned HTML for pattern generation
                                st.session_state.converted_docs_html = cleaned_html

                                st.success(f"✅ Converted: {result.get('document_name', 'Document')}")
                                if title:
                                    st.info(f"📝 Extracted title: **{title}** (H1 removed from content)")
                                st.info(f"🧹 Cleaned HTML loaded into Source HTML field (removed H1 and everything before it)")

                                # Show before/after preview
                                col1, col2 = st.columns(2)
                                with col1:
                                    with st.expander("Raw HTML (Original)"):
                                        preview = raw_html[:1000] + "..." if len(raw_html) > 1000 else raw_html
                                        st.code(preview, language="html")
                                        st.caption(f"Total length: {len(raw_html)} chars")

                                with col2:
                                    with st.expander("Cleaned HTML (For Patterns)"):
                                        preview = cleaned_html[:1000] + "..." if len(cleaned_html) > 1000 else cleaned_html
                                        st.code(preview, language="html")
                                        st.caption(f"Total length: {len(cleaned_html)} chars")
                            else:
                                st.error(f"❌ Conversion failed: {result.get('error')}")
                                # Show full error details
                                with st.expander("Error Details"):
                                    st.json(result)
                        except Exception as e:
                            st.error(f"❌ Error: {e}")
                            import traceback
                            with st.expander("Full Error Traceback"):
                                st.code(traceback.format_exc())

            st.markdown("---")

            # Target HTML input (required)
            html_sample = st.text_area(
                "Target HTML (Required) - Your Desired Output Format",
                placeholder="<h2 class='entry-title'>Example Heading</h2>\n<p class='article-text'>Example paragraph...</p>",
                height=250,
                help="Paste sample HTML showing how you want the content formatted in WordPress"
            )

            st.markdown("---")

            # Source HTML input (optional but recommended) - auto-filled from conversion if available
            source_html_value = st.session_state.converted_docs_html if st.session_state.converted_docs_html else ""
            source_html = st.text_area(
                "Source HTML (Optional) - From Google Docs",
                value=source_html_value,
                placeholder="<h2>Example Heading</h2>\n<p>Example paragraph...</p>" if not source_html_value else "",
                height=200,
                help="Optional: Paste example HTML from Google Docs or use the Test Run feature above"
            )

            # Clear button for source HTML
            if source_html_value:
                if st.button("Clear Source HTML", type="secondary"):
                    st.session_state.converted_docs_html = ""
                    st.rerun()

            if st.button("Analyze HTML & Generate Patterns", type="primary", disabled=not html_sample):
                if html_sample:
                    with st.spinner("AI is analyzing HTML and generating patterns..."):
                        try:
                            # Get API key
                            api_key = get_secret('ANTHROPIC_API_KEY')
                            if not api_key:
                                st.error("ANTHROPIC_API_KEY not found in secrets or environment variables")
                            else:
                                # Analyze HTML with AI
                                client = anthropic.Anthropic(api_key=api_key)

                                # Build prompt based on whether source HTML is provided
                                if source_html and source_html.strip():
                                    prompt = f"""Generate HTML transformation patterns by analyzing the source and target HTML.

SOURCE HTML (from Google Docs):
```html
{source_html}
```

TARGET HTML (desired WordPress format):
```html
{html_sample}
```

Your task:
1. Identify each HTML element type in the source (p, h2, h3, h4, h5, h6, strong, em, ul, ol, li, a, img, blockquote, table, etc.)
2. For each element, create a regex pattern that matches its structure in the SOURCE HTML
3. Create the target pattern from the TARGET HTML showing how it should be formatted

Return ONLY valid JSON (no markdown, no explanation):
{{
  "patterns": [
    {{
      "element_type": "p",
      "source_pattern": "<p[^>]*>(.*?)</p>",
      "target_pattern": "<p class=\\"found-class\\">\\\\1</p>"
    }}
  ]
}}

CRITICAL RULES (MUST FOLLOW):
1. **<p> tags - Use MINIMAL patterns** with REGEX:
   - Create ONE pattern for ALL <p> tags with "text-align:justify" or "text-align: justify" (case insensitive)
   - Create ONE pattern for ALL <p> tags with "text-align:center" or "text-align: center" (case insensitive)
   - For <p> tags containing <img>, ALWAYS set text-align to center in target_pattern
   - Use regex like: <p[^>]*style="[^"]*text-align:\s*justify[^"]*"[^>]*>(.*?)</p>

2. **<table> tags - ALWAYS set to full width**:
   - Add style="width: 100%" to ALL table tags in target_pattern

3. **<img> tags - Use generic src patterns**:
   - DO NOT include specific src URL values in patterns
   - Use generic regex: <img[^>]*(src="[^"]*")[^>]*> to match ANY image
   - Use capture groups to preserve the src: (src="[^"]*")
   - In target_pattern, use \\1 to preserve the captured src
   - Example: source_pattern: <img[^>]*(src="[^"]*")[^>]*>, target_pattern: <img \\1 class="custom">

4. **Use GENERAL regex patterns - minimize pattern count**:
   - Don't create separate patterns for each variation
   - Use [^>]* to match any attributes
   - Use \\s* to match optional whitespace
   - Example: ONE pattern <p[^>]*style="[^"]*text-align:\s*justify[^"]*"[^>]*> covers ALL justify paragraphs

CRITICAL RULES:
- source_pattern must use REGEX to match the SOURCE HTML structure
- If source has attributes like <p dir="ltr">, create pattern like: <p[^>]*\\s+dir=["\']ltr["\'][^>]*>(.*?)</p>
- If source is plain <p>, use: <p[^>]*>(.*?)</p>
- Use (.*?) to capture content and \\\\1 in target to preserve it
- target_pattern must include ALL classes and attributes from TARGET HTML
- Use double backslashes (\\\\1, \\\\2) for capture groups in JSON
- Return valid JSON only"""
                                else:
                                    prompt = f"""Analyze this TARGET HTML and generate transformation patterns.

TARGET HTML (desired WordPress format):
```html
{html_sample}
```

For each HTML element type found (p, h2, h3, h4, h5, h6, strong, em, ul, ol, li, a, img, blockquote, table), generate a transformation pattern.

Return ONLY valid JSON (no markdown, no explanation):
{{
  "patterns": [
    {{
      "element_type": "p",
      "source_pattern": "<p[^>]*>(.*?)</p>",
      "target_pattern": "<p class=\\"found-class\\">\\\\1</p>"
    }}
  ]
}}

CRITICAL RULES (MUST FOLLOW):
1. **<p> tags - Use MINIMAL patterns** with REGEX:
   - Create ONE pattern for ALL <p> tags with "text-align:justify" or "text-align: justify" (case insensitive)
   - Create ONE pattern for ALL <p> tags with "text-align:center" or "text-align: center" (case insensitive)
   - For <p> tags containing <img>, ALWAYS set text-align to center in target_pattern
   - Use regex like: <p[^>]*style="[^"]*text-align:\s*justify[^"]*"[^>]*>(.*?)</p>

2. **<table> tags - ALWAYS set to full width**:
   - Add style="width: 100%" to ALL table tags in target_pattern

3. **<img> tags - Use generic src patterns**:
   - DO NOT include specific src URL values in patterns
   - Use generic regex: <img[^>]*(src="[^"]*")[^>]*> to match ANY image
   - Use capture groups to preserve the src: (src="[^"]*")
   - In target_pattern, use \\1 to preserve the captured src
   - Example: source_pattern: <img[^>]*(src="[^"]*")[^>]*>, target_pattern: <img \\1 class="custom">

4. **Use GENERAL regex patterns - minimize pattern count**:
   - Don't create separate patterns for each variation
   - Use [^>]* to match any attributes
   - Use \\s* to match optional whitespace
   - Example: ONE pattern <p[^>]*style="[^"]*text-align:\s*justify[^"]*"[^>]*> covers ALL justify paragraphs

RULES:
- source_pattern: Use generic regex like <p[^>]*>(.*?)</p> to match any variant
- target_pattern: Extract exact classes and attributes from the TARGET HTML provided
- Use (.*?) to capture content and \\\\1 in target to preserve it
- Use double backslashes (\\\\1) for capture groups in JSON
- Return valid JSON only"""

                                message = client.messages.create(
                                    model="claude-sonnet-4-5-20250929",
                                    max_tokens=2000,
                                    messages=[{"role": "user", "content": prompt}]
                                )

                                response_text = message.content[0].text.strip()

                                # Remove markdown code blocks if present
                                if response_text.startswith('```'):
                                    lines = response_text.split('\n')
                                    response_text = '\n'.join(lines[1:-1]) if len(lines) > 2 else response_text

                                patterns_data = json.loads(response_text)
                                generated_patterns = patterns_data.get('patterns', [])

                                if generated_patterns:
                                    # Store in session state for persistence across button clicks
                                    st.session_state.generated_patterns = generated_patterns
                                    st.session_state.patterns_project_id = selected_project_id

                                    st.success(f"Generated **{len(generated_patterns)}** pattern(s)!")
                                    st.info("Scroll down to review and save the patterns.")
                                else:
                                    st.warning("No patterns generated. Try providing more HTML examples.")

                        except json.JSONDecodeError as e:
                            st.error(f"Failed to parse AI response: {e}")
                            st.code(response_text)
                        except Exception as e:
                            st.error(f"Error: {e}")
                            import traceback
                            with st.expander("Error Details"):
                                st.code(traceback.format_exc())

            # Display saved patterns from session state (outside button scope)
            if st.session_state.generated_patterns and st.session_state.patterns_project_id == selected_project_id:
                st.markdown("---")
                st.markdown("### Generated Patterns")

                # Show generated patterns
                with st.expander("View Generated Patterns", expanded=True):
                    st.json(st.session_state.generated_patterns)

                # Preview transformations
                st.markdown("### Pattern Preview")
                for pattern in st.session_state.generated_patterns:
                    st.markdown(f"**{pattern['element_type'].upper()}:**")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.caption("Source Pattern:")
                        st.code(pattern['source_pattern'], language="regex")
                    with col2:
                        st.caption("Target Pattern:")
                        st.code(pattern['target_pattern'], language="html")

                # Save/Discard buttons
                st.markdown("---")
                st.markdown("### Save Patterns?")

                col1, col2 = st.columns(2)

                with col1:
                    if st.button("Save to Project", type="primary", use_container_width=True, key="save_patterns_btn"):
                        try:
                            # Get current project config
                            current_project = get_project(st.session_state.patterns_project_id)
                            current_html_configs = current_project.get('html_configs') or {}

                            # Merge new patterns with existing config
                            updated_html_configs = {**current_html_configs}
                            updated_html_configs['patterns'] = st.session_state.generated_patterns

                            # Update project with merged config
                            update_project(
                                st.session_state.patterns_project_id,
                                html_configs=updated_html_configs
                            )

                            # Clear session state
                            st.session_state.generated_patterns = None
                            st.session_state.patterns_project_id = None

                            st.success("Patterns saved to project!")
                            st.balloons()
                            st.info("You can now use these patterns when publishing content!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Failed to save: {e}")
                            import traceback
                            st.code(traceback.format_exc())

                with col2:
                    if st.button("Discard", use_container_width=True, key="discard_patterns_btn"):
                        # Clear session state
                        st.session_state.generated_patterns = None
                        st.session_state.patterns_project_id = None
                        st.info("Patterns discarded.")
                        st.rerun()

    except Exception as e:
        st.error(f"Error loading projects: {e}")

# ============================================
# Page: Publish Content
# ============================================

elif page == "Publish Content":
    st.title("Publish Content to WordPress")
    st.markdown("---")

    # Fetch projects
    try:
        projects = list_projects(status='active')

        if not projects:
            st.warning("No projects found. Please create a project first.")
            st.info("Go to 'Create Project' page to add your WordPress site.")
        else:
            st.markdown("""
            ### How it works:

            1. **Select a project** (your WordPress site)
            2. **Paste any Google Docs URL** (edit, view, or published URL)
            3. **Click Publish** and wait for the magic to happen!

            The system will:
            - Connect to Google Drive API (OAuth authentication)
            - Convert Google Docs to HTML
            - Process and upload images
            - Apply HTML transformations (if configured)
            - Create a draft post in WordPress
            """)

            st.markdown("---")

            # Project selection OUTSIDE form for dynamic updates
            st.markdown("### Select Project")

            project_options = {f"{p['project_name']} ({p['project_id']})": p['project_id'] for p in projects}
            project_options["No Project (Use defaults)"] = None

            selected_display = st.selectbox(
                "Project",
                options=list(project_options.keys()),
                help="Select which WordPress site to publish to",
                key="publish_project_selector"
            )
            selected_project_id = project_options[selected_display]

            # Load project data if selected
            project = None
            if selected_project_id:
                project = get_project(selected_project_id)
                st.info(f"Will publish to: **{project['wordpress_url']}**")

            # Show main keyword input if project uses main_keyword naming (OUTSIDE form)
            main_keyword = ""
            if selected_project_id and project:
                image_configs = project.get('image_configs', {})
                naming_method = image_configs.get('naming_method', 'default')

                if naming_method == 'main_keyword':
                    st.markdown("### Main Keyword for Image Naming")
                    main_keyword = st.text_input(
                        "Main Keyword",
                        placeholder="e.g., quat-tran-sunhouse",
                        help="Images will be named: main-keyword-01, main-keyword-02, etc.",
                        key="publish_main_keyword"
                    )
                    if not main_keyword:
                        st.warning("Please provide a main keyword for image naming")

            st.markdown("---")

            with st.form("publish_form"):
                st.markdown("### Google Docs URL")

                docs_url = st.text_input(
                    "Content Document URL",
                    placeholder="https://docs.google.com/document/d/YOUR_DOC_ID/edit",
                    help="Any Google Docs URL works: edit, view, or published URLs"
                )

                st.markdown("---")

                # Show requirements
                with st.expander("Requirements"):
                    st.markdown("""
                    **Google Docs Setup:**
                    1. Open your document in Google Docs
                    2. Copy the URL from your browser (edit, view, or published URL - all work!)
                    3. First time: Browser will open for Google authentication
                    4. Grant access to your Google account

                    **Note:** OAuth credentials must be configured in `credentials/` folder.

                    **WordPress Setup:**
                    - WordPress REST API must be enabled (default in WordPress 4.7+)
                    - Application Password must be valid
                    - User must have permission to create posts
                    """)

                submit = st.form_submit_button("Publish to WordPress", type="primary", use_container_width=True)

                if submit:
                    if not docs_url:
                        st.error("Please provide a Google Docs URL")

                    if docs_url:
                        # Execute workflow
                        st.markdown("---")
                        st.markdown("### Publishing Progress")

                        progress_bar = st.progress(0)
                        status_text = st.empty()

                        try:
                            status_text.text("Starting workflow...")
                            progress_bar.progress(10)

                            # Execute the actual workflow
                            with st.spinner("Publishing... This may take 1-2 minutes."):
                                result = execute_publishing_workflow(
                                    google_docs_url=docs_url,
                                    project_id=selected_project_id,
                                    main_keyword=main_keyword if main_keyword else None
                                )

                            progress_bar.progress(100)

                            # Show results
                            st.markdown("---")
                            if result['success']:
                                st.success("**Publishing completed successfully!**")

                                # Show details in columns
                                col1, col2, col3 = st.columns(3)

                                with col1:
                                    st.metric("Post Title", result['post_title'])
                                with col2:
                                    st.metric("Images Processed", result['images_processed'])
                                with col3:
                                    st.metric("Time Taken", f"{result['execution_time']:.1f}s")

                                # Show links
                                st.markdown("### Links")
                                st.markdown(f"**View Post:** [{result['post_url']}]({result['post_url']})")
                                if result.get('edit_url'):
                                    st.markdown(f"**Edit Post:** [{result['edit_url']}]({result['edit_url']})")

                                st.info("**Note:** Post was created as a DRAFT. Review and publish from WordPress admin.")

                                # Show full result
                                with st.expander("Full Result Details"):
                                    st.json(result)
                            else:
                                st.error("**Publishing failed!**")
                                st.error(f"**Error:** {result.get('error', 'Unknown error')}")
                                st.error(f"**Failed at step:** {result.get('step_failed', 'Unknown')}")

                                with st.expander("Debug Information"):
                                    st.json(result)

                        except Exception as e:
                            progress_bar.progress(0)
                            st.error(f"**Unexpected error:** {e}")
                            import traceback
                            with st.expander("Error Details"):
                                st.code(traceback.format_exc())

    except Exception as e:
        st.error(f"Error loading projects: {e}")

# ============================================
# Page: Publishing History
# ============================================

elif page == "Publishing History":
    st.title("Publishing History")
    st.markdown("---")

    st.info("Publishing history is stored in the SQLite database (`data/clients.db`).")

    st.markdown("""
    ### View History via Database

    You can query the `publishing_history` table directly:

    ```sql
    SELECT * FROM publishing_history ORDER BY published_at DESC LIMIT 10;
    ```

    ### Coming Soon
    - View recent publishes
    - Filter by project
    - Success/failure statistics
    - Detailed logs
    """)

# ============================================
# Page: Batch Publish
# ============================================

elif page == "Batch Publish":
    st.title("Batch Publish to WordPress")
    st.markdown("---")

    # Initialize session state for batch data - use a simple list structure
    if 'batch_rows' not in st.session_state:
        st.session_state.batch_rows = [
            {'select': True, 'url': '', 'keyword': '', 'status': '⏳ Pending', 'title': '', 'post_url': ''}
            for _ in range(5)
        ]

    # Ensure all rows have keyword field (for backwards compatibility)
    for row in st.session_state.batch_rows:
        if 'keyword' not in row:
            row['keyword'] = ''

    # Fetch projects
    try:
        projects = list_projects(status='active')

        if not projects:
            st.warning("No projects found. Please create a project first.")
        else:
            # Project selection
            col1, col2 = st.columns([2, 1])
            with col1:
                project_options = {f"{p['project_name']} ({p['project_id']})": p['project_id'] for p in projects}
                selected_display = st.selectbox(
                    "Select Project",
                    options=list(project_options.keys()),
                    key="batch_project"
                )
                selected_project_id = project_options[selected_display]
            with col2:
                if selected_project_id:
                    project = get_project(selected_project_id)
                    st.caption(f"📍 {project['wordpress_url']}")

            # Check if project uses main_keyword naming
            uses_keyword_naming = False
            if selected_project_id:
                image_configs = project.get('image_configs', {})
                uses_keyword_naming = image_configs.get('naming_method', 'default') == 'main_keyword'

            st.markdown("---")
            st.markdown("**Paste Google Docs URLs in the table below:**")

            if uses_keyword_naming:
                st.info("🔑 This project uses **Main Keyword** image naming. Enter a keyword for each URL.")

            # Table header - adjust columns based on whether keyword is needed
            if uses_keyword_naming:
                header_cols = st.columns([0.3, 2.5, 1.5, 0.8, 1, 1.5, 0.3])
                header_cols[0].markdown("**✓**")
                header_cols[1].markdown("**Google Docs URL**")
                header_cols[2].markdown("**Main Keyword**")
                header_cols[3].markdown("**Status**")
                header_cols[4].markdown("**Title**")
                header_cols[5].markdown("**Post URL**")
                header_cols[6].markdown("**🗑️**")
            else:
                header_cols = st.columns([0.4, 3.5, 1, 1.3, 1.8, 0.4])
                header_cols[0].markdown("**✓**")
                header_cols[1].markdown("**Google Docs URL**")
                header_cols[2].markdown("**Status**")
                header_cols[3].markdown("**Post Title**")
                header_cols[4].markdown("**Post URL**")
                header_cols[5].markdown("**🗑️**")

            # Track which row to delete (if any)
            row_to_delete = None

            # Render each row
            for i, row in enumerate(st.session_state.batch_rows):
                if uses_keyword_naming:
                    cols = st.columns([0.3, 2.5, 1.5, 0.8, 1, 1.5, 0.3])
                else:
                    cols = st.columns([0.4, 3.5, 1, 1.3, 1.8, 0.4])

                col_idx = 0

                with cols[col_idx]:
                    st.session_state.batch_rows[i]['select'] = st.checkbox(
                        "select",
                        value=row['select'],
                        key=f"sel_{i}",
                        label_visibility="collapsed"
                    )
                col_idx += 1

                with cols[col_idx]:
                    st.session_state.batch_rows[i]['url'] = st.text_input(
                        "url",
                        value=row['url'],
                        key=f"url_{i}",
                        label_visibility="collapsed",
                        placeholder="Paste Google Docs URL here..."
                    )
                col_idx += 1

                if uses_keyword_naming:
                    with cols[col_idx]:
                        st.session_state.batch_rows[i]['keyword'] = st.text_input(
                            "keyword",
                            value=row.get('keyword', ''),
                            key=f"kw_{i}",
                            label_visibility="collapsed",
                            placeholder="e.g., quat-tran"
                        )
                    col_idx += 1

                with cols[col_idx]:
                    st.markdown(row['status'])
                col_idx += 1

                with cols[col_idx]:
                    if row['title']:
                        title_display = row['title'][:15] + "..." if len(row['title']) > 15 else row['title']
                        st.markdown(f"_{title_display}_")
                    else:
                        st.markdown("—")
                col_idx += 1

                with cols[col_idx]:
                    if row['post_url']:
                        st.markdown(f"[View]({row['post_url']})")
                    else:
                        st.markdown("—")
                col_idx += 1

                with cols[col_idx]:
                    if st.button("🗑️", key=f"del_{i}", help="Delete this row"):
                        row_to_delete = i

            # Delete row if requested (after loop to avoid index issues)
            if row_to_delete is not None and len(st.session_state.batch_rows) > 1:
                st.session_state.batch_rows.pop(row_to_delete)
                st.rerun()

            st.markdown("---")

            # Buttons
            col1, col2, col3, col4 = st.columns([1, 1, 1, 1])

            with col1:
                if st.button("➕ Add Row", use_container_width=True):
                    st.session_state.batch_rows.append(
                        {'select': True, 'url': '', 'keyword': '', 'status': '⏳ Pending', 'title': '', 'post_url': ''}
                    )
                    st.rerun()

            with col2:
                if st.button("🗑️ Clear All", use_container_width=True):
                    st.session_state.batch_rows = [
                        {'select': True, 'url': '', 'keyword': '', 'status': '⏳ Pending', 'title': '', 'post_url': ''}
                        for _ in range(5)
                    ]
                    st.rerun()

            with col3:
                # Count valid URLs
                valid_count = sum(1 for r in st.session_state.batch_rows if r['select'] and r['url'].strip())
                st.caption(f"📊 {valid_count} selected")

            with col4:
                process_btn = st.button("▶️ Process", type="primary", use_container_width=True)

            if process_btn:
                # Get rows to process
                rows_to_process = [(i, r) for i, r in enumerate(st.session_state.batch_rows)
                                   if r['select'] and r['url'].strip()]

                if not rows_to_process:
                    st.warning("No URLs selected. Add URLs and check the Select box.")
                else:
                    progress_bar = st.progress(0)
                    status_text = st.empty()

                    total = len(rows_to_process)
                    success_count = 0
                    failed_count = 0

                    for j, (idx, row) in enumerate(rows_to_process):
                        url = row['url'].strip()
                        keyword = row.get('keyword', '').strip()
                        progress_bar.progress((j + 1) / total)
                        status_text.text(f"Processing {j + 1}/{total}...")

                        # Update status
                        st.session_state.batch_rows[idx]['status'] = '🔄 Processing...'

                        try:
                            result = execute_publishing_workflow(
                                google_docs_url=url,
                                project_id=selected_project_id,
                                main_keyword=keyword if keyword else None
                            )

                            if result['success']:
                                st.session_state.batch_rows[idx]['status'] = '✅ Success'
                                st.session_state.batch_rows[idx]['title'] = result.get('post_title', '')
                                st.session_state.batch_rows[idx]['post_url'] = result.get('post_url', '')
                                success_count += 1
                            else:
                                error_msg = result.get('error', 'Unknown')[:25]
                                st.session_state.batch_rows[idx]['status'] = f'❌ Failed'
                                failed_count += 1

                        except Exception as e:
                            st.session_state.batch_rows[idx]['status'] = f'❌ Error'
                            failed_count += 1

                    progress_bar.progress(1.0)
                    status_text.empty()

                    if success_count > 0:
                        st.success(f"✅ Published {success_count} post(s)!")
                    if failed_count > 0:
                        st.error(f"❌ {failed_count} failed")

                    st.rerun()

    except Exception as e:
        st.error(f"Error: {e}")

# ============================================
# Footer
# ============================================

st.sidebar.markdown("---")
st.sidebar.markdown("### Tips")
st.sidebar.markdown("""
1. **Any Google Docs URL works** (edit, view, or published)
2. **Use WordPress App Password** (not regular password)
3. **Posts are created as drafts** for safety
4. **First run requires Google OAuth** (browser opens once)
""")
