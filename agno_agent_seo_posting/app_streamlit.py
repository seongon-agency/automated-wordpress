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

# Load environment variables
load_dotenv()

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
if st.sidebar.button("Publish New Content", use_container_width=True):
    st.session_state.current_page = "Publish Content"
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

    1. **Create a Project** - Add your WordPress site details
    2. **Prepare Content** - Write content in Google Docs and publish to web
    3. **Publish** - Select project and paste Google Docs URL
    4. **Done!** - Get the WordPress post URL

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

        col1, col2 = st.columns(2)

        with col1:
            image_width = st.number_input(
                "Target Image Width (px)",
                min_value=100,
                max_value=2000,
                value=800,
                help="Images will be resized to this width"
            )

            image_quality = st.slider(
                "Image Quality (%)",
                min_value=50,
                max_value=100,
                value=92,
                help="Higher = better quality but larger file size"
            )

        with col2:
            image_format = st.selectbox(
                "Image Format",
                options=["JPEG", "PNG", "WEBP"],
                index=0,
                help="Output format for processed images"
            )

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
                    image_configs = {
                        "target_width": image_width,
                        "image_quality": image_quality,
                        "image_format": image_format
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

            st.markdown("---")
            st.markdown(f"### Editing: **{current_project['project_name']}**")

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

                current_image_config = current_project.get('image_configs') or {}

                col1, col2 = st.columns(2)

                with col1:
                    new_image_width = st.number_input(
                        "Target Image Width (px)",
                        min_value=100,
                        max_value=2000,
                        value=current_image_config.get('target_width', 800),
                        help="Images will be resized to this width"
                    )

                    new_image_quality = st.slider(
                        "Image Quality (%)",
                        min_value=50,
                        max_value=100,
                        value=current_image_config.get('image_quality', 92),
                        help="Higher = better quality but larger file size"
                    )

                with col2:
                    new_image_format = st.selectbox(
                        "Image Format",
                        options=["JPEG", "PNG", "WEBP"],
                        index=["JPEG", "PNG", "WEBP"].index(current_image_config.get('image_format', 'JPEG')),
                        help="Output format for processed images"
                    )

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
                        updates = {
                            'project_name': new_project_name,
                            'wordpress_url': new_wp_url,
                            'wordpress_username': new_wp_username,
                            'image_configs': {
                                'target_width': new_image_width,
                                'image_quality': new_image_quality,
                                'image_format': new_image_format
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

                # Show current patterns
                with st.expander("View Current Patterns"):
                    st.json(current_patterns)

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
                                api_key = os.getenv('ANTHROPIC_API_KEY')
                                if not api_key:
                                    st.error("ANTHROPIC_API_KEY not found in environment variables")
                                else:
                                    # Modify patterns
                                    result = modify_patterns_with_ai(
                                        current_patterns=current_patterns,
                                        instruction=instruction,
                                        api_key=api_key
                                    )

                                    if result['success']:
                                        st.success("Patterns modified successfully!")

                                        # Show what changed
                                        st.info(f"**Changes Made:** {result['changes_made']}")

                                        # Show new patterns
                                        new_patterns = result['patterns']
                                        with st.expander("Updated Patterns"):
                                            st.json(new_patterns)

                                        # Ask for confirmation
                                        st.markdown("---")
                                        st.markdown("### Save Changes?")

                                        col1, col2 = st.columns(2)

                                        with col1:
                                            if st.button("Save to Project", type="primary", use_container_width=True):
                                                try:
                                                    # Update project
                                                    update_project(
                                                        selected_project_id,
                                                        html_configs={'patterns': new_patterns}
                                                    )
                                                    st.success("Patterns saved to project!")
                                                    st.balloons()
                                                except Exception as e:
                                                    st.error(f"Failed to save: {e}")

                                        with col2:
                                            if st.button("Discard Changes", use_container_width=True):
                                                st.info("Changes discarded. Patterns not saved.")

                                    else:
                                        st.error(f"AI modification failed: {result.get('error', 'Unknown error')}")

                            except Exception as e:
                                st.error(f"Error: {e}")
                                import traceback
                                with st.expander("Error Details"):
                                    st.code(traceback.format_exc())

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
    1. Paste sample HTML from your WordPress theme
    2. AI analyzes the HTML structure
    3. Automatically generates transformation patterns
    4. Save patterns to your project

    **What to paste:**
    - Copy formatted content from your WordPress post editor (HTML view)
    - Include examples of all element types (headings, paragraphs, images, lists, etc.)
    - The more complete the sample, the better the patterns!
    """)

    st.markdown("---")

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

            # HTML input
            html_sample = st.text_area(
                "Paste HTML Sample",
                placeholder="<h2>Example Heading</h2>\n<p class='article-text'>Example paragraph...</p>",
                height=300,
                help="Paste sample HTML that shows your desired formatting"
            )

            if st.button("Analyze HTML & Generate Patterns", type="primary", disabled=not html_sample):
                if html_sample:
                    with st.spinner("AI is analyzing HTML and generating patterns..."):
                        try:
                            # Get API key
                            api_key = os.getenv('ANTHROPIC_API_KEY')
                            if not api_key:
                                st.error("ANTHROPIC_API_KEY not found in environment variables")
                            else:
                                # Analyze HTML with AI
                                client = anthropic.Anthropic(api_key=api_key)

                                prompt = f"""Analyze this HTML sample and generate transformation patterns.

HTML Sample:
```html
{html_sample}
```

For each HTML element type you find (p, h2, h3, h4, strong, em, ul, ol, li, a, img, table), generate a transformation pattern.

Return ONLY a valid JSON object in this exact format (no markdown, no explanation):
{{
  "patterns": [
    {{
      "element_type": "p",
      "source_pattern": "<p[^>]*>(.*?)</p>",
      "target_pattern": "<p class=\\"found-class\\" style=\\"found-style\\">\\\\1</p>"
    }}
  ]
}}

Important:
- Use double backslashes (\\\\1) for capture groups in JSON
- Preserve content with (.*?) in source_pattern
- Include ALL attributes found in the sample in target_pattern
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
                                    st.success(f"Generated **{len(generated_patterns)}** pattern(s)!")

                                    # Show generated patterns
                                    with st.expander("Generated Patterns", expanded=True):
                                        st.json(generated_patterns)

                                    # Preview transformations
                                    st.markdown("---")
                                    st.markdown("### Pattern Preview")

                                    for pattern in generated_patterns:
                                        st.markdown(f"**{pattern['element_type'].upper()}:**")
                                        st.code(pattern['target_pattern'], language="html")

                                    # Save button
                                    st.markdown("---")
                                    st.markdown("### Save Patterns?")

                                    col1, col2 = st.columns(2)

                                    with col1:
                                        if st.button("Save to Project", type="primary", use_container_width=True):
                                            try:
                                                # Update project with new patterns
                                                update_project(
                                                    selected_project_id,
                                                    html_configs={'patterns': generated_patterns}
                                                )
                                                st.success("Patterns saved to project!")
                                                st.balloons()
                                                st.info("You can now use these patterns when publishing content!")
                                            except Exception as e:
                                                st.error(f"Failed to save: {e}")

                                    with col2:
                                        if st.button("Discard", use_container_width=True):
                                            st.info("Patterns discarded. Not saved to project.")
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
            2. **Paste a Google Docs URL** (must be published to web)
            3. **Click Publish** and wait for the magic to happen!

            The system will:
            - Convert Google Docs to HTML
            - Process and upload images
            - Apply HTML transformations (if configured)
            - Create a draft post in WordPress
            """)

            st.markdown("---")

            with st.form("publish_form"):
                st.markdown("### Select Project")

                project_options = {f"{p['project_name']} ({p['project_id']})": p['project_id'] for p in projects}
                project_options["No Project (Use defaults)"] = None

                selected_display = st.selectbox(
                    "Project",
                    options=list(project_options.keys()),
                    help="Select which WordPress site to publish to"
                )
                selected_project_id = project_options[selected_display]

                if selected_project_id:
                    # Show project details
                    project = get_project(selected_project_id)
                    st.info(f"Will publish to: **{project['wordpress_url']}**")

                st.markdown("### Google Docs URL")

                docs_url = st.text_input(
                    "Content Document URL",
                    placeholder="https://docs.google.com/document/d/e/YOUR_DOC_ID/pub",
                    help="Document must be published to web (File → Share → Publish to web). URL must end with /pub"
                )

                st.markdown("---")

                # Show requirements
                with st.expander("Requirements"):
                    st.markdown("""
                    **Google Docs Setup:**
                    1. Open your document in Google Docs
                    2. Go to **File → Share → Publish to web**
                    3. Click **Publish**
                    4. Copy the URL (should end with `/pub`)

                    **WordPress Setup:**
                    - WordPress REST API must be enabled (default in WordPress 4.7+)
                    - Application Password must be valid
                    - User must have permission to create posts
                    """)

                submit = st.form_submit_button("Publish to WordPress", type="primary", use_container_width=True)

                if submit:
                    if not docs_url:
                        st.error("Please provide a Google Docs URL")
                    elif not docs_url.endswith('/pub'):
                        st.warning("Warning: URL doesn't end with /pub. Make sure document is published to web!")

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
                                    project_id=selected_project_id
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
# Footer
# ============================================

st.sidebar.markdown("---")
st.sidebar.markdown("### Tips")
st.sidebar.markdown("""
1. **Google Docs must be published** (not just shared)
2. **Use WordPress App Password** (not regular password)
3. **Posts are created as drafts** for safety
4. **Check WordPress admin** after publishing
""")
