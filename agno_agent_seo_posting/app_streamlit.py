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
    page_title="Hệ Thống Đăng Bài WordPress",
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

st.sidebar.title("Hệ Thống Đăng Bài WordPress")
st.sidebar.caption("Phát triển nội bộ • Tích hợp AI")

st.sidebar.markdown("")

# Quick action button
if st.sidebar.button("Đăng Bài Nhanh", type="primary", use_container_width=True):
    st.session_state.current_page = "Publish Content"

st.sidebar.markdown("---")

# Navigation sections
st.sidebar.subheader("Tổng Quan")
if st.sidebar.button("Bảng Điều Khiển", use_container_width=True,
                      disabled=(st.session_state.current_page == "Home")):
    st.session_state.current_page = "Home"

st.sidebar.markdown("")
st.sidebar.subheader("Dự Án")
col1, col2 = st.sidebar.columns(2)
with col1:
    if st.button("Xem", use_container_width=True, key="view_projects"):
        st.session_state.current_page = "Projects"
with col2:
    if st.button("Tạo Mới", use_container_width=True, key="new_project"):
        st.session_state.current_page = "Create Project"

if st.sidebar.button("Chỉnh Sửa Cài Đặt Dự Án", use_container_width=True):
    st.session_state.current_page = "Edit Project"

st.sidebar.markdown("")
st.sidebar.subheader("Cấu Hình AI")
if st.sidebar.button("Sửa HTML Patterns (Ngôn Ngữ Tự Nhiên)", use_container_width=True):
    st.session_state.current_page = "AI Pattern Editor"
if st.sidebar.button("Quét & Tạo Patterns", use_container_width=True):
    st.session_state.current_page = "Scan HTML Template"

st.sidebar.markdown("")
st.sidebar.subheader("Đăng Bài")
if st.sidebar.button("Đăng Một Bài", use_container_width=True):
    st.session_state.current_page = "Publish Content"
if st.sidebar.button("Đăng Hàng Loạt", use_container_width=True):
    st.session_state.current_page = "Batch Publish"
if st.sidebar.button("Xem Lịch Sử Đăng Bài", use_container_width=True):
    st.session_state.current_page = "Publishing History"

st.sidebar.markdown("---")

# Quick stats in sidebar
try:
    projects = list_projects(status='all')
    col1, col2 = st.sidebar.columns(2)
    with col1:
        st.metric("Dự Án", len(projects))
    with col2:
        st.metric("Trạng Thái", "Sẵn Sàng")
except:
    pass

st.sidebar.markdown("---")
st.sidebar.caption("**Mẹo:** Dùng Đăng Bài Nhanh để truy cập nhanh")
st.sidebar.caption("**Công nghệ:** Supabase • Python • Claude AI")

# Set page from session state
page = st.session_state.current_page

# ============================================
# Page: Home
# ============================================

if page == "Home":
    st.title("Hệ Thống Đăng Bài SEO WordPress")
    st.markdown("### Phiên Bản Phát Triển Nội Bộ")
    st.markdown("---")

    st.markdown("""
    ## Chào Mừng!

    Đây là **phiên bản phát triển nội bộ** của Hệ Thống Đăng Bài SEO WordPress.

    ### Tính Năng Hệ Thống:

    1. **Quản Lý Dự Án**
       - Tạo và quản lý các dự án WordPress
       - Mỗi dự án lưu thông tin đăng nhập WordPress và các mẫu chuyển đổi HTML
       - Hỗ trợ nhiều trang WordPress

    2. **Đăng Nội Dung**
       - Đăng Google Docs lên WordPress
       - Tự động chuyển đổi HTML theo mẫu dự án
       - Xử lý và tải ảnh lên thư viện media WordPress
       - Tạo bài viết nháp theo mặc định để an toàn

    3. **Quy Trình Hoàn Chỉnh**
       - Chuyển đổi Google Docs → HTML
       - Xử lý ảnh (tải xuống, thay đổi kích thước, tải lên)
       - Áp dụng chuyển đổi HTML
       - Đăng lên WordPress
       - Theo dõi lịch sử đăng bài

    ### Bắt Đầu Nhanh:

    1. **Cài Đặt Google OAuth** - Đặt file `client_secret.json` vào thư mục `credentials/`
    2. **Tạo Dự Án** - Thêm thông tin trang WordPress của bạn
    3. **Chuẩn Bị Nội Dung** - Viết nội dung trong Google Docs
    4. **Đăng Bài** - Chọn dự án và dán URL Google Docs (edit/view/published)
    5. **Hoàn Tất!** - Nhận link bài viết WordPress

    ---
    """)

    # Show quick stats
    col1, col2, col3 = st.columns(3)

    with col1:
        try:
            projects = list_projects(status='all')
            st.metric("Tổng Số Dự Án", len(projects))
        except:
            st.metric("Tổng Số Dự Án", "0")

    with col2:
        st.metric("Trạng Thái Hệ Thống", "Sẵn Sàng")

    with col3:
        st.metric("Phiên Bản", "1.0.0")

    st.markdown("---")

    st.info("**Sử dụng thanh bên trái để điều hướng** giữa các trang")

# ============================================
# Page: Projects
# ============================================

elif page == "Projects":
    st.title("Danh Sách Dự Án")
    st.markdown("---")

    # Fetch all projects
    try:
        projects = list_projects(status='all')

        if projects:
            st.success(f"Tìm thấy {len(projects)} dự án")

            for project in projects:
                with st.expander(f"{project['project_name']} ({project['project_id']})"):
                    col1, col2 = st.columns([3, 1])

                    with col1:
                        st.markdown(f"**ID Dự Án:** `{project['project_id']}`")
                        st.markdown(f"**URL WordPress:** {project['wordpress_url']}")
                        st.markdown(f"**Tên Đăng Nhập:** {project['wordpress_username']}")
                        st.markdown(f"**Trạng Thái:** {project['status']}")
                        st.markdown(f"**Ngày Tạo:** {project.get('created_at', 'N/A')}")

                        # Show HTML patterns count
                        html_configs = project.get('html_configs')
                        if html_configs and html_configs.get('patterns'):
                            st.markdown(f"**HTML Patterns:** {len(html_configs['patterns'])} đã cấu hình")
                        else:
                            st.markdown("**HTML Patterns:** Chưa cấu hình")

                        # Show image config
                        image_configs = project.get('image_configs')
                        if image_configs:
                            st.markdown(f"**Chiều Rộng Ảnh:** {image_configs.get('target_width', 800)}px")
                            st.markdown(f"**Chất Lượng Ảnh:** {image_configs.get('image_quality', 92)}")
                        else:
                            st.markdown("**Cài Đặt Ảnh:** Sử dụng mặc định")

                    with col2:
                        if st.button("Xóa", key=f"del_{project['project_id']}"):
                            try:
                                delete_project(project['project_id'])
                                st.success("Đã xóa dự án!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Xóa thất bại: {e}")

        else:
            st.info("Không tìm thấy dự án nào. Hãy tạo dự án đầu tiên!")

    except Exception as e:
        st.error(f"Lỗi khi tải dự án: {e}")

# ============================================
# Page: Create Project
# ============================================

elif page == "Create Project":
    st.title("Tạo Dự Án Mới")
    st.markdown("---")

    st.markdown("""
    ### Dự Án Là Gì?

    Một **dự án** đại diện cho một trang WordPress nơi bạn sẽ đăng nội dung. Mỗi dự án lưu trữ:
    - URL trang WordPress và thông tin đăng nhập
    - Các mẫu chuyển đổi HTML (tùy chọn)
    - Cài đặt xử lý ảnh (tùy chọn)

    Sau khi cấu hình, bạn có thể đăng nhiều bài viết lên cùng một dự án mà không cần cấu hình lại.
    """)

    st.markdown("---")

    # Image resize method selection OUTSIDE form so it updates immediately
    # Initialize session state for resize method if not set
    if 'create_resize_method' not in st.session_state:
        st.session_state.create_resize_method = "Chiều Rộng Cố Định"

    st.markdown("### Phương Thức Thay Đổi Kích Thước Ảnh")
    resize_options = ["Chiều Rộng Cố Định", "Kích Thước Gốc Google Docs", "Không Thay Đổi (Chất Lượng Gốc)"]
    current_index = resize_options.index(st.session_state.create_resize_method) if st.session_state.create_resize_method in resize_options else 0
    resize_method = st.radio(
        "Chọn cách thay đổi kích thước ảnh",
        options=resize_options,
        index=current_index,
        help="Chiều Rộng Cố Định: Tùy chỉnh kích thước theo chiều rộng (và chiều cao tùy chọn). Kích Thước Gốc Google Docs: Sử dụng kích thước từ Google Docs. Không Thay Đổi: Tải ảnh gốc không xử lý (chất lượng tốt nhất).",
        key="create_resize_method_selector"
    )
    # Update session state
    st.session_state.create_resize_method = resize_method

    with st.form("create_project_form"):
        st.markdown("### Thông Tin Cơ Bản")

        project_id = st.text_input(
            "ID Dự Án *",
            placeholder="vd: blog_cua_toi_2024",
            help="Định danh duy nhất (chữ thường, chỉ dùng gạch dưới). Không thể thay đổi sau khi tạo."
        )

        project_name = st.text_input(
            "Tên Dự Án *",
            placeholder="vd: Blog Tuyệt Vời Của Tôi",
            help="Tên hiển thị cho dự án này"
        )

        st.markdown("### Cấu Hình WordPress")

        wp_url = st.text_input(
            "URL Trang WordPress *",
            placeholder="https://trang-wordpress-cua-ban.com",
            help="URL đầy đủ đến trang WordPress của bạn (không có dấu / ở cuối)"
        )

        wp_username = st.text_input(
            "Tên Đăng Nhập WordPress *",
            placeholder="admin",
            help="Tên đăng nhập WordPress của bạn"
        )

        wp_password = st.text_input(
            "Mật Khẩu Ứng Dụng WordPress *",
            type="password",
            placeholder="xxxx xxxx xxxx xxxx",
            help="KHÔNG phải mật khẩu thông thường! Lấy từ: WordPress Admin → Users → Profile → Application Passwords"
        )

        st.markdown("### Cài Đặt Ảnh (Tùy Chọn)")

        # Show different settings based on resize method from session state
        if st.session_state.create_resize_method == "Chiều Rộng Cố Định":
            st.markdown("#### Cài Đặt Kích Thước Tùy Chỉnh")
            st.info("💡 Nếu chỉ nhập chiều rộng, chiều cao sẽ được tính tự động theo tỷ lệ. Nếu nhập cả hai, ảnh sẽ được thay đổi kích thước chính xác theo giá trị đã nhập.")

            col1, col2 = st.columns(2)

            with col1:
                image_width = st.number_input(
                    "Chiều Rộng Ảnh (px) *",
                    min_value=100,
                    max_value=2000,
                    value=800,
                    key="create_fixed_width",
                    help="Bắt buộc: Chiều rộng mục tiêu cho ảnh"
                )

                image_height = st.number_input(
                    "Chiều Cao Ảnh (px)",
                    min_value=0,
                    max_value=2000,
                    value=0,
                    key="create_fixed_height",
                    help="Tùy chọn: Để trống (0) để giữ tỷ lệ tự động, hoặc nhập giá trị cụ thể"
                )

            with col2:
                image_quality = st.slider(
                    "Chất Lượng Ảnh (%)",
                    min_value=50,
                    max_value=100,
                    value=92,
                    key="create_fixed_quality",
                    help="Cao hơn = chất lượng tốt hơn nhưng file lớn hơn"
                )

                image_format = st.selectbox(
                    "Định Dạng Ảnh",
                    options=["JPEG", "PNG", "WEBP"],
                    index=0,
                    key="create_fixed_format",
                    help="Định dạng đầu ra cho ảnh đã xử lý"
                )

        elif st.session_state.create_resize_method == "Kích Thước Gốc Google Docs":
            st.markdown("#### Cài Đặt Kích Thước Gốc Google Docs")
            st.info("🎯 Ảnh sẽ được thay đổi kích thước theo đúng kích thước từ Google Docs (chiều rộng và chiều cao từ thẻ <img>)")

            col1, col2 = st.columns(2)

            with col1:
                image_quality = st.slider(
                    "Chất Lượng Ảnh (%)",
                    min_value=50,
                    max_value=100,
                    value=92,
                    key="create_gdocs_quality",
                    help="Cao hơn = chất lượng tốt hơn nhưng file lớn hơn"
                )

            with col2:
                image_format = st.selectbox(
                    "Định Dạng Ảnh",
                    options=["JPEG", "PNG", "WEBP"],
                    index=0,
                    key="create_gdocs_format",
                    help="Định dạng đầu ra cho ảnh đã xử lý"
                )

            # Set defaults for backend (not used in google_docs_original mode)
            image_width = 800
            image_height = None

        else:
            # No Resize (Original Quality)
            st.markdown("#### Cài Đặt Chất Lượng Gốc")
            st.success("✨ Ảnh sẽ được tải lên đúng như trong Google Docs - không thay đổi kích thước, không nén lại. Chất lượng tốt nhất!")
            st.info("Lưu ý: Ảnh gốc có thể lớn. Đảm bảo WordPress của bạn có thể xử lý được.")

            # Set defaults (not used in no_resize mode)
            image_width = 800
            image_height = None
            image_quality = 100
            image_format = "PNG"

        st.markdown("### Đặt Tên Ảnh")

        naming_method = st.selectbox(
            "Phương Thức Đặt Tên Ảnh",
            options=["Mặc Định (tên_dự_án)", "Theo Alt Text", "Theo Từ Khóa Chính"],
            index=0,
            key="create_naming_method",
            help="Cách đặt tên cho ảnh tải xuống"
        )

        if naming_method == "Theo Alt Text":
            st.info("📝 Ảnh sẽ được đặt tên bằng N từ đầu tiên của alt text (định dạng slug). Ảnh không có alt text sẽ được đặt tên 'unnamed-image-1', 'unnamed-image-2', v.v.")
            alt_text_words = st.number_input(
                "Số từ từ alt text",
                min_value=1,
                max_value=20,
                value=5,
                key="create_alt_text_words",
                help="Số từ từ alt text dùng làm tên file"
            )
        elif naming_method == "Theo Từ Khóa Chính":
            st.info("🔑 Ảnh sẽ được đặt tên bằng từ khóa chính bạn cung cấp khi đăng bài (vd: 'tu-khoa-chinh-01', 'tu-khoa-chinh-02')")
            alt_text_words = 5  # default, not used
        else:
            st.info("📁 Ảnh sẽ được đặt tên bằng ID dự án (vd: 'ten_du_an_1', 'ten_du_an_2')")
            alt_text_words = 5  # default, not used

        st.markdown("### Tùy Chọn Caption")

        enable_auto_captions = st.checkbox(
            "Bật Caption WordPress Tự Động",
            value=True,
            help="Tự động bọc ảnh với shortcode [caption] của WordPress. Tắt nếu bạn muốn kiểm soát định dạng caption bằng HTML patterns."
        )

        st.markdown("### Ghi Chú (Tùy Chọn)")

        notes = st.text_area(
            "Ghi Chú Dự Án",
            placeholder="Ghi chú về dự án này...",
            help="Ghi chú tùy chọn để tham khảo"
        )

        st.markdown("---")
        submit = st.form_submit_button("Tạo Dự Án", type="primary", use_container_width=True)

        if submit:
            # Validation
            if not all([project_id, project_name, wp_url, wp_username, wp_password]):
                st.error("Vui lòng điền đầy đủ các trường bắt buộc (đánh dấu *)")
            else:
                try:
                    # Prepare image configs
                    # Convert UI label to backend key (from session state)
                    if st.session_state.create_resize_method == "Chiều Rộng Cố Định":
                        resize_method_key = "fixed_width"
                    elif st.session_state.create_resize_method == "Kích Thước Gốc Google Docs":
                        resize_method_key = "google_docs_original"
                    else:
                        resize_method_key = "no_resize"

                    # Convert naming method to backend key
                    naming_method_key = "default"
                    if naming_method == "Theo Alt Text":
                        naming_method_key = "alt_text"
                    elif naming_method == "Theo Từ Khóa Chính":
                        naming_method_key = "main_keyword"

                    # Convert image_height of 0 to None (for proportional resizing)
                    target_height = image_height if image_height and image_height > 0 else None

                    image_configs = {
                        "resize_method": resize_method_key,
                        "target_width": image_width,
                        "target_height": target_height,
                        "image_quality": image_quality,
                        "image_format": image_format,
                        "enable_auto_captions": enable_auto_captions,
                        "naming_method": naming_method_key,
                        "alt_text_words": alt_text_words
                    }

                    # Create project
                    with st.spinner("Đang tạo dự án..."):
                        result = create_project(
                            project_id=project_id,
                            project_name=project_name,
                            wordpress_url=wp_url,
                            wordpress_username=wp_username,
                            wordpress_app_password=wp_password,
                            image_configs=image_configs,
                            notes=notes if notes else None
                        )

                    st.success("Tạo dự án thành công!")
                    st.info("Bạn có thể đăng nội dung lên dự án này. Đi đến trang 'Đăng Một Bài'.")

                    # Show summary
                    st.json(result)

                except Exception as e:
                    st.error(f"Tạo dự án thất bại: {e}")

# ============================================
# Page: Edit Project
# ============================================

elif page == "Edit Project":
    st.title("Chỉnh Sửa Dự Án")
    st.markdown("---")

    st.markdown("""
    ### Cập Nhật Cài Đặt Dự Án

    Chỉnh sửa thông tin đăng nhập WordPress, cài đặt ảnh, hoặc các cấu hình dự án khác.
    """)

    st.markdown("---")

    # Fetch projects
    try:
        projects = list_projects(status='all')

        if not projects:
            st.warning("Không tìm thấy dự án. Vui lòng tạo dự án trước.")
        else:
            # Select project to edit
            project_options = {f"{p['project_name']} ({p['project_id']})": p['project_id'] for p in projects}

            selected_display = st.selectbox(
                "Chọn Dự Án Để Chỉnh Sửa",
                options=list(project_options.keys()),
                help="Chọn dự án cần chỉnh sửa"
            )
            selected_project_id = project_options[selected_display]

            # Load current project data
            current_project = get_project(selected_project_id)

            # Reset session state if project changed
            if 'edit_project_id' not in st.session_state or st.session_state.edit_project_id != selected_project_id:
                st.session_state.edit_project_id = selected_project_id
                # Clear cached values so they reload from database
                keys_to_clear = [
                    'edit_resize_method',
                    'edit_naming_method_state'
                ]
                for key in keys_to_clear:
                    if key in st.session_state:
                        del st.session_state[key]

            st.markdown("---")
            st.markdown(f"### Đang Chỉnh Sửa: **{current_project['project_name']}**")

            # Image resize method selection OUTSIDE form so it updates immediately
            current_image_config = current_project.get('image_configs') or {}
            current_resize_method = current_image_config.get('resize_method', 'fixed_width')

            # Map backend key to UI label
            resize_method_map = {
                'fixed_width': 'Chiều Rộng Cố Định',
                'google_docs_original': 'Kích Thước Gốc Google Docs',
                'no_resize': 'Không Thay Đổi (Chất Lượng Gốc)'
            }
            current_resize_method_label = resize_method_map.get(current_resize_method, 'Chiều Rộng Cố Định')

            # Initialize session state for resize method if not set
            if 'edit_resize_method' not in st.session_state:
                st.session_state.edit_resize_method = current_resize_method_label

            st.markdown("#### Phương Thức Thay Đổi Kích Thước Ảnh")
            edit_resize_options = ["Chiều Rộng Cố Định", "Kích Thước Gốc Google Docs", "Không Thay Đổi (Chất Lượng Gốc)"]
            current_edit_index = edit_resize_options.index(st.session_state.edit_resize_method) if st.session_state.edit_resize_method in edit_resize_options else 0
            new_resize_method = st.radio(
                "Chọn cách thay đổi kích thước ảnh",
                options=edit_resize_options,
                index=current_edit_index,
                help="Chiều Rộng Cố Định: Tùy chỉnh kích thước theo chiều rộng (và chiều cao tùy chọn). Kích Thước Gốc Google Docs: Sử dụng kích thước từ Google Docs. Không Thay Đổi: Tải ảnh gốc (chất lượng tốt nhất)."
            )
            # Update session state
            st.session_state.edit_resize_method = new_resize_method

            # Image naming method selection OUTSIDE form so it updates immediately
            st.markdown("#### Phương Thức Đặt Tên Ảnh")

            # Get current naming method from database
            current_naming_method = current_image_config.get('naming_method', 'default')

            # Map backend key to UI label
            naming_method_map = {
                'default': 'Mặc Định (tên_dự_án)',
                'alt_text': 'Theo Alt Text',
                'main_keyword': 'Theo Từ Khóa Chính'
            }
            current_naming_method_label = naming_method_map.get(current_naming_method, 'Mặc Định (tên_dự_án)')

            # Initialize session state for naming method if not set
            if 'edit_naming_method_state' not in st.session_state:
                st.session_state.edit_naming_method_state = current_naming_method_label

            edit_naming_options = ["Mặc Định (tên_dự_án)", "Theo Alt Text", "Theo Từ Khóa Chính"]
            current_naming_index = edit_naming_options.index(st.session_state.edit_naming_method_state) if st.session_state.edit_naming_method_state in edit_naming_options else 0

            new_naming_method_outside = st.radio(
                "Chọn cách đặt tên ảnh",
                options=edit_naming_options,
                index=current_naming_index,
                help="Mặc Định: Sử dụng tên dự án. Theo Alt Text: Sử dụng alt text của ảnh. Theo Từ Khóa Chính: Bạn cung cấp từ khóa khi đăng bài."
            )
            # Update session state
            st.session_state.edit_naming_method_state = new_naming_method_outside

            # Show info based on selection
            if new_naming_method_outside == "Theo Alt Text":
                st.info("📝 Ảnh sẽ được đặt tên bằng N từ đầu tiên của alt text (định dạng slug).")
            elif new_naming_method_outside == "Theo Từ Khóa Chính":
                st.info("🔑 Ảnh sẽ được đặt tên bằng từ khóa chính bạn cung cấp khi đăng bài (vd: 'tu-khoa-chinh-01', 'tu-khoa-chinh-02')")
            else:
                st.info("📁 Ảnh sẽ được đặt tên bằng ID dự án (vd: 'ten_du_an_1', 'ten_du_an_2')")

            with st.form("edit_project_form"):
                st.markdown("#### Thông Tin Cơ Bản")

                new_project_name = st.text_input(
                    "Tên Dự Án",
                    value=current_project['project_name'],
                    help="Tên hiển thị cho dự án này"
                )

                st.markdown("#### Cấu Hình WordPress")

                new_wp_url = st.text_input(
                    "URL Trang WordPress",
                    value=current_project['wordpress_url'],
                    help="URL đầy đủ đến trang WordPress của bạn"
                )

                new_wp_username = st.text_input(
                    "Tên Đăng Nhập WordPress",
                    value=current_project['wordpress_username'],
                    help="Tên đăng nhập WordPress của bạn"
                )

                new_wp_password = st.text_input(
                    "Mật Khẩu Ứng Dụng WordPress",
                    type="password",
                    placeholder="Để trống để giữ mật khẩu hiện tại",
                    help="Nhập mật khẩu mới hoặc để trống để giữ nguyên"
                )

                st.markdown("#### Cài Đặt Ảnh")

                # Show different settings based on resize method from session state
                if st.session_state.edit_resize_method == "Chiều Rộng Cố Định":
                    st.markdown("##### Cài Đặt Kích Thước Tùy Chỉnh")
                    st.info("💡 Nếu chỉ nhập chiều rộng, chiều cao sẽ được tính tự động theo tỷ lệ. Nếu nhập cả hai, ảnh sẽ được thay đổi kích thước chính xác theo giá trị đã nhập.")

                    col1, col2 = st.columns(2)

                    with col1:
                        new_image_width = st.number_input(
                            "Chiều Rộng Ảnh (px) *",
                            min_value=100,
                            max_value=2000,
                            value=current_image_config.get('target_width', 800),
                            key="edit_fixed_width",
                            help="Bắt buộc: Chiều rộng mục tiêu cho ảnh"
                        )

                        new_image_height = st.number_input(
                            "Chiều Cao Ảnh (px)",
                            min_value=0,
                            max_value=2000,
                            value=current_image_config.get('target_height') or 0,
                            key="edit_fixed_height",
                            help="Tùy chọn: Để trống (0) để giữ tỷ lệ tự động, hoặc nhập giá trị cụ thể"
                        )

                    with col2:
                        new_image_quality = st.slider(
                            "Chất Lượng Ảnh (%)",
                            min_value=50,
                            max_value=100,
                            value=current_image_config.get('image_quality', 92),
                            key="edit_fixed_quality",
                            help="Cao hơn = chất lượng tốt hơn nhưng file lớn hơn"
                        )

                        new_image_format = st.selectbox(
                            "Định Dạng Ảnh",
                            options=["JPEG", "PNG", "WEBP"],
                            index=["JPEG", "PNG", "WEBP"].index(current_image_config.get('image_format', 'JPEG')),
                            key="edit_fixed_format",
                            help="Định dạng đầu ra cho ảnh đã xử lý"
                        )

                elif st.session_state.edit_resize_method == "Kích Thước Gốc Google Docs":
                    st.markdown("##### Cài Đặt Kích Thước Gốc Google Docs")
                    st.info("🎯 Ảnh sẽ được thay đổi kích thước theo đúng kích thước từ Google Docs (chiều rộng và chiều cao từ thẻ <img>)")

                    col1, col2 = st.columns(2)

                    with col1:
                        new_image_quality = st.slider(
                            "Chất Lượng Ảnh (%)",
                            min_value=50,
                            max_value=100,
                            value=current_image_config.get('image_quality', 92),
                            key="edit_gdocs_quality",
                            help="Cao hơn = chất lượng tốt hơn nhưng file lớn hơn"
                        )

                    with col2:
                        new_image_format = st.selectbox(
                            "Định Dạng Ảnh",
                            options=["JPEG", "PNG", "WEBP"],
                            index=["JPEG", "PNG", "WEBP"].index(current_image_config.get('image_format', 'JPEG')),
                            key="edit_gdocs_format",
                            help="Định dạng đầu ra cho ảnh đã xử lý"
                        )

                    # Keep existing values (not used in google_docs_original mode)
                    new_image_width = current_image_config.get('target_width', 800)
                    new_image_height = None

                else:
                    # No Resize (Original Quality)
                    st.markdown("##### Cài Đặt Chất Lượng Gốc")
                    st.success("✨ Ảnh sẽ được tải lên đúng như trong Google Docs - không thay đổi kích thước, không nén lại. Chất lượng tốt nhất!")
                    st.info("Lưu ý: Ảnh gốc có thể lớn. Đảm bảo WordPress của bạn có thể xử lý được.")

                    # Set defaults (not used in no_resize mode)
                    new_image_width = current_image_config.get('target_width', 800)
                    new_image_height = None
                    new_image_quality = 100
                    new_image_format = current_image_config.get('image_format', 'PNG')

                # Alt text words setting (for Alt Text Based naming)
                if st.session_state.edit_naming_method_state == "Theo Alt Text":
                    new_alt_text_words = st.number_input(
                        "Số từ từ alt text",
                        min_value=1,
                        max_value=20,
                        value=current_image_config.get('alt_text_words', 5),
                        key="edit_alt_text_words",
                        help="Số từ từ alt text dùng làm tên file"
                    )
                else:
                    new_alt_text_words = current_image_config.get('alt_text_words', 5)  # keep existing

                st.markdown("#### Tùy Chọn Caption")

                new_enable_auto_captions = st.checkbox(
                    "Bật Caption WordPress Tự Động",
                    value=current_image_config.get('enable_auto_captions', True),
                    help="Tự động bọc ảnh với shortcode [caption] của WordPress. Tắt nếu bạn muốn kiểm soát định dạng caption bằng HTML patterns."
                )

                st.markdown("#### Ghi Chú")

                new_notes = st.text_area(
                    "Ghi Chú Dự Án",
                    value=current_project.get('notes', ''),
                    help="Ghi chú tùy chọn để tham khảo"
                )

                st.markdown("---")
                submit = st.form_submit_button("Lưu Thay Đổi", type="primary", use_container_width=True)

                if submit:
                    try:
                        # Prepare updates
                        # Convert UI label to backend key (from session state)
                        if st.session_state.edit_resize_method == "Chiều Rộng Cố Định":
                            new_resize_method_key = "fixed_width"
                        elif st.session_state.edit_resize_method == "Kích Thước Gốc Google Docs":
                            new_resize_method_key = "google_docs_original"
                        else:
                            new_resize_method_key = "no_resize"

                        # Convert naming method to backend key (from session state)
                        new_naming_method_key = "default"
                        if st.session_state.edit_naming_method_state == "Theo Alt Text":
                            new_naming_method_key = "alt_text"
                        elif st.session_state.edit_naming_method_state == "Theo Từ Khóa Chính":
                            new_naming_method_key = "main_keyword"

                        # Convert image_height of 0 to None (for proportional resizing)
                        target_height_value = new_image_height if new_image_height and new_image_height > 0 else None

                        updates = {
                            'project_name': new_project_name,
                            'wordpress_url': new_wp_url,
                            'wordpress_username': new_wp_username,
                            'image_configs': {
                                'resize_method': new_resize_method_key,
                                'target_width': new_image_width,
                                'target_height': target_height_value,
                                'image_quality': new_image_quality,
                                'image_format': new_image_format,
                                'enable_auto_captions': new_enable_auto_captions,
                                'naming_method': new_naming_method_key,
                                'alt_text_words': new_alt_text_words
                            },
                            'notes': new_notes if new_notes else None
                        }

                        # Only update password if provided
                        if new_wp_password:
                            updates['wordpress_app_password'] = new_wp_password

                        # Update project
                        with st.spinner("Đang lưu thay đổi..."):
                            result = update_project(selected_project_id, **updates)

                        # Clear session state keys so next load reads from database
                        keys_to_clear = [
                            'edit_naming_method_state',
                            'edit_resize_method',
                            'edit_project_id'
                        ]
                        for key in keys_to_clear:
                            if key in st.session_state:
                                del st.session_state[key]

                        # Show success and rerun to reload fresh data
                        st.toast("Cập nhật dự án thành công!", icon="✅")
                        st.rerun()

                    except Exception as e:
                        st.error(f"Cập nhật dự án thất bại: {e}")

    except Exception as e:
        st.error(f"Lỗi khi tải dự án: {e}")

# ============================================
# Page: AI Pattern Editor
# ============================================

elif page == "AI Pattern Editor":
    st.title("Trình Chỉnh Sửa Pattern AI")
    st.markdown("### Chỉnh Sửa HTML Patterns Bằng Ngôn Ngữ Tự Nhiên")
    st.markdown("---")

    st.markdown("""
    Sử dụng **ngôn ngữ tự nhiên được hỗ trợ bởi AI** để chỉnh sửa các mẫu chuyển đổi HTML của dự án.

    **Ví dụ:**
    - "Làm tất cả tiêu đề h2 màu xanh"
    - "Thêm class 'highlight' cho tất cả đoạn văn"
    - "Làm các link mở ở tab mới"
    - "Xóa tất cả style khỏi ảnh"
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
            st.warning("Không tìm thấy dự án. Vui lòng tạo dự án trước.")
        else:
            # Select project
            project_options = {f"{p['project_name']} ({p['project_id']})": p['project_id'] for p in projects}

            selected_display = st.selectbox(
                "Chọn Dự Án",
                options=list(project_options.keys()),
                help="Chọn dự án cần chỉnh sửa patterns"
            )
            selected_project_id = project_options[selected_display]

            # Load project
            project = get_project(selected_project_id)
            html_configs = project.get('html_configs') or {}
            current_patterns = html_configs.get('patterns', [])

            st.markdown("---")

            if not current_patterns:
                st.warning("Dự án này chưa có HTML patterns nào. Sử dụng 'Quét HTML Template' để tạo patterns trước.")
            else:
                st.success(f"Dự án có **{len(current_patterns)}** pattern(s) đã cấu hình")

                # Show current patterns with delete buttons
                with st.expander("Xem & Quản Lý Patterns Hiện Tại", expanded=True):
                    st.markdown("**Nhấn nút xóa để xóa một pattern**")

                    for idx, pattern in enumerate(current_patterns):
                        col1, col2 = st.columns([10, 1])

                        with col1:
                            st.markdown(f"**Pattern {idx + 1}: `{pattern.get('element_type', 'unknown')}`**")
                            st.code(f"Source: {pattern.get('source_pattern', 'N/A')}\nTarget: {pattern.get('target_pattern', 'N/A')}", language="html")

                        with col2:
                            if st.button("🗑️", key=f"delete_pattern_{idx}", help=f"Xóa pattern {idx + 1}"):
                                # Remove pattern from list
                                updated_patterns = [p for i, p in enumerate(current_patterns) if i != idx]

                                # Update database
                                try:
                                    from src.database import update_project

                                    updated_html_configs = {**html_configs, 'patterns': updated_patterns}
                                    update_project(selected_project_id, html_configs=updated_html_configs)

                                    st.success(f"Đã xóa Pattern {idx + 1} ({pattern.get('element_type')}) thành công!")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Xóa pattern thất bại: {e}")

                        if idx < len(current_patterns) - 1:
                            st.markdown("---")

                st.markdown("---")
                st.markdown("### Hướng Dẫn Bằng Ngôn Ngữ Tự Nhiên")

                # Natural language input
                instruction = st.text_area(
                    "Bạn muốn thay đổi gì?",
                    placeholder="vd: Làm tất cả tiêu đề h2 màu xanh và thêm margin dưới",
                    help="Mô tả thay đổi bạn muốn bằng tiếng Việt hoặc tiếng Anh"
                )

                if st.button("Áp Dụng Thay Đổi Với AI", type="primary", disabled=not instruction):
                    if instruction:
                        with st.spinner("AI đang phân tích yêu cầu và chỉnh sửa patterns..."):
                            try:
                                # Import the pattern modifier
                                from src.utils.pattern_modifier import modify_patterns_with_ai

                                # Get API key
                                api_key = get_secret('ANTHROPIC_API_KEY')
                                if not api_key:
                                    st.error("Không tìm thấy ANTHROPIC_API_KEY trong secrets hoặc biến môi trường")
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

                                        st.success("Chỉnh sửa patterns thành công!")
                                        st.info("Cuộn xuống để xem lại và lưu thay đổi.")

                                    else:
                                        st.error(f"Chỉnh sửa AI thất bại: {result.get('error', 'Lỗi không xác định')}")

                            except Exception as e:
                                st.error(f"Lỗi: {e}")
                                import traceback
                                with st.expander("Chi Tiết Lỗi"):
                                    st.code(traceback.format_exc())

            # Display modified patterns from session state (outside button scope)
            if st.session_state.modified_patterns and st.session_state.modified_patterns_project_id == selected_project_id:
                st.markdown("---")
                st.markdown("### Patterns Đã Chỉnh Sửa")

                # Show what changed
                if st.session_state.pattern_changes_made:
                    st.info(f"**Thay đổi đã thực hiện:** {st.session_state.pattern_changes_made}")

                # Show new patterns
                with st.expander("Xem Patterns Đã Cập Nhật", expanded=True):
                    st.json(st.session_state.modified_patterns)

                # Save/Discard buttons
                st.markdown("---")
                st.markdown("### Lưu Thay Đổi?")

                col1, col2 = st.columns(2)

                with col1:
                    if st.button("Lưu Vào Dự Án", type="primary", use_container_width=True, key="save_modified_patterns_btn"):
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

                            st.success("Đã lưu patterns vào dự án!")
                            st.balloons()
                            st.info("Bạn có thể sử dụng các patterns này khi đăng nội dung!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Lưu thất bại: {e}")
                            import traceback
                            st.code(traceback.format_exc())

                with col2:
                    if st.button("Hủy Thay Đổi", use_container_width=True, key="discard_modified_patterns_btn"):
                        # Clear session state
                        st.session_state.modified_patterns = None
                        st.session_state.modified_patterns_project_id = None
                        st.session_state.pattern_changes_made = None
                        st.info("Đã hủy thay đổi. Patterns không được lưu.")
                        st.rerun()

    except Exception as e:
        st.error(f"Lỗi khi tải dự án: {e}")

# ============================================
# Page: Scan HTML Template
# ============================================

elif page == "Scan HTML Template":
    st.title("Quét HTML Template")
    st.markdown("### Tự Động Tạo Patterns Từ HTML Mẫu")
    st.markdown("---")

    st.markdown("""
    **Cách hoạt động:**
    1. **🧪 Chạy Thử (Tùy Chọn)**: Dán URL Google Docs để xem cấu trúc HTML chính xác
    2. Dán **HTML MỤC TIÊU** - định dạng bạn muốn trong WordPress (bắt buộc)
    3. **HTML NGUỒN** sẽ được tự động điền từ Chạy Thử, hoặc dán thủ công (khuyến nghị để chính xác hơn)
    4. AI phân tích cả hai và tạo các mẫu chuyển đổi chính xác
    5. Xem lại và lưu patterns vào dự án

    **Mẹo để có kết quả tốt nhất:**
    - **Dùng Chạy Thử**: Lấy cấu trúc HTML chính xác từ Google Docs tự động
    - **HTML Mục Tiêu**: Copy nội dung đã định dạng từ theme WordPress (chế độ xem HTML)
    - **HTML Nguồn**: Sẽ được điền từ Chạy Thử, hoặc dán thủ công
    - Bao gồm ví dụ của tất cả loại phần tử (tiêu đề, đoạn văn, ảnh, danh sách, bảng, v.v.)
    - Cung cấp cả nguồn và mục tiêu sẽ cho regex patterns chính xác nhất
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
            st.warning("Không tìm thấy dự án. Vui lòng tạo dự án trước.")
        else:
            project_options = {f"{p['project_name']} ({p['project_id']})": p['project_id'] for p in projects}

            selected_display = st.selectbox(
                "Chọn Dự Án",
                options=list(project_options.keys()),
                help="Patterns sẽ được lưu vào dự án này"
            )
            selected_project_id = project_options[selected_display]

            st.markdown("---")

            # Initialize session state for converted docs HTML
            if 'converted_docs_html' not in st.session_state:
                st.session_state.converted_docs_html = ""

            # Test Google Docs Conversion Section
            with st.expander("🧪 Chạy Thử: Chuyển Đổi Google Docs Sang HTML (Tùy Chọn)", expanded=False):
                st.markdown("""
                **Tại sao dùng tính năng này?**
                - Xem cấu trúc HTML chính xác mà Google Docs xuất ra
                - Tự động làm sạch (H1 và mọi thứ trước đó được loại bỏ)
                - Tự động điền vào trường HTML Nguồn bên dưới
                - Tạo pattern chính xác hơn

                **Cách hoạt động:**
                1. Dán URL Google Docs bất kỳ
                2. Nhấn "Chuyển Đổi Sang HTML"
                3. HTML được chuyển đổi và làm sạch (H1 được loại bỏ)
                4. HTML đã làm sạch tự động điền vào trường HTML Nguồn bên dưới

                **Những gì được làm sạch:**
                - Trích xuất tiêu đề từ H1 (để hiển thị)
                - Loại bỏ H1 và mọi thứ trước đó
                - Điều này phù hợp với quy trình đăng bài thực tế
                """)

                test_docs_url = st.text_input(
                    "URL Google Docs",
                    placeholder="https://docs.google.com/document/d/YOUR_DOC_ID/edit",
                    help="URL Google Docs bất kỳ (edit, view, hoặc published)"
                )

                col1, col2 = st.columns([1, 3])
                with col1:
                    convert_btn = st.button("Chuyển Đổi Sang HTML", type="secondary", use_container_width=True)

                if convert_btn and test_docs_url:
                    with st.spinner("Đang chuyển đổi Google Docs sang HTML..."):
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
                            st.info(f"🔍 Đang tìm credentials tại: {credentials_dir}")
                            st.info(f"🔍 Đường dẫn client secrets: {client_secrets}")
                            st.info(f"🔍 Đường dẫn token: {token_path}")
                            st.info(f"🔍 Client secrets tồn tại: {os.path.exists(client_secrets)}")
                            st.info(f"🔍 Token tồn tại: {os.path.exists(token_path)}")
                            st.info(f"🔍 Client secrets có thể đọc: {os.access(client_secrets, os.R_OK)}")

                            result = google_docs_to_html(test_docs_url)

                            if result['success']:
                                # Clean the HTML: remove H1 and everything before it
                                from src.utils.html_extractor import clean_html_for_wordpress, extract_title_from_html

                                raw_html = result['raw_html']
                                title = extract_title_from_html(raw_html)
                                cleaned_html = clean_html_for_wordpress(raw_html)

                                # Store cleaned HTML for pattern generation
                                st.session_state.converted_docs_html = cleaned_html

                                st.success(f"✅ Đã chuyển đổi: {result.get('document_name', 'Document')}")
                                if title:
                                    st.info(f"📝 Tiêu đề đã trích xuất: **{title}** (H1 đã được loại bỏ khỏi nội dung)")
                                st.info(f"🧹 HTML đã làm sạch được tải vào trường HTML Nguồn (đã loại bỏ H1 và mọi thứ trước đó)")

                                # Show before/after preview
                                col1, col2 = st.columns(2)
                                with col1:
                                    with st.expander("HTML Gốc"):
                                        preview = raw_html[:1000] + "..." if len(raw_html) > 1000 else raw_html
                                        st.code(preview, language="html")
                                        st.caption(f"Tổng độ dài: {len(raw_html)} ký tự")

                                with col2:
                                    with st.expander("HTML Đã Làm Sạch (Cho Patterns)"):
                                        preview = cleaned_html[:1000] + "..." if len(cleaned_html) > 1000 else cleaned_html
                                        st.code(preview, language="html")
                                        st.caption(f"Tổng độ dài: {len(cleaned_html)} ký tự")
                            else:
                                st.error(f"❌ Chuyển đổi thất bại: {result.get('error')}")
                                # Show full error details
                                with st.expander("Chi Tiết Lỗi"):
                                    st.json(result)
                        except Exception as e:
                            st.error(f"❌ Lỗi: {e}")
                            import traceback
                            with st.expander("Chi Tiết Lỗi Đầy Đủ"):
                                st.code(traceback.format_exc())

            st.markdown("---")

            # Target HTML input (required)
            html_sample = st.text_area(
                "HTML Mục Tiêu (Bắt Buộc) - Định Dạng Đầu Ra Mong Muốn",
                placeholder="<h2 class='entry-title'>Tiêu Đề Ví Dụ</h2>\n<p class='article-text'>Đoạn văn ví dụ...</p>",
                height=250,
                help="Dán HTML mẫu thể hiện cách bạn muốn nội dung được định dạng trong WordPress"
            )

            st.markdown("---")

            # Source HTML input (optional but recommended) - auto-filled from conversion if available
            source_html_value = st.session_state.converted_docs_html if st.session_state.converted_docs_html else ""
            source_html = st.text_area(
                "HTML Nguồn (Tùy Chọn) - Từ Google Docs",
                value=source_html_value,
                placeholder="<h2>Tiêu Đề Ví Dụ</h2>\n<p>Đoạn văn ví dụ...</p>" if not source_html_value else "",
                height=200,
                help="Tùy chọn: Dán HTML mẫu từ Google Docs hoặc dùng tính năng Chạy Thử ở trên"
            )

            # Clear button for source HTML
            if source_html_value:
                if st.button("Xóa HTML Nguồn", type="secondary"):
                    st.session_state.converted_docs_html = ""
                    st.rerun()

            if st.button("Phân Tích HTML & Tạo Patterns", type="primary", disabled=not html_sample):
                if html_sample:
                    with st.spinner("AI đang phân tích HTML và tạo patterns..."):
                        try:
                            # Get API key
                            api_key = get_secret('ANTHROPIC_API_KEY')
                            if not api_key:
                                st.error("Không tìm thấy ANTHROPIC_API_KEY trong secrets hoặc biến môi trường")
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

                                    st.success(f"Đã tạo **{len(generated_patterns)}** pattern(s)!")
                                    st.info("Cuộn xuống để xem lại và lưu patterns.")
                                else:
                                    st.warning("Không tạo được patterns. Thử cung cấp thêm ví dụ HTML.")

                        except json.JSONDecodeError as e:
                            st.error(f"Không thể phân tích phản hồi AI: {e}")
                            st.code(response_text)
                        except Exception as e:
                            st.error(f"Lỗi: {e}")
                            import traceback
                            with st.expander("Chi Tiết Lỗi"):
                                st.code(traceback.format_exc())

            # Display saved patterns from session state (outside button scope)
            if st.session_state.generated_patterns and st.session_state.patterns_project_id == selected_project_id:
                st.markdown("---")
                st.markdown("### Patterns Đã Tạo")

                # Show generated patterns
                with st.expander("Xem Patterns Đã Tạo", expanded=True):
                    st.json(st.session_state.generated_patterns)

                # Preview transformations
                st.markdown("### Xem Trước Pattern")
                for pattern in st.session_state.generated_patterns:
                    st.markdown(f"**{pattern['element_type'].upper()}:**")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.caption("Pattern Nguồn:")
                        st.code(pattern['source_pattern'], language="regex")
                    with col2:
                        st.caption("Pattern Mục Tiêu:")
                        st.code(pattern['target_pattern'], language="html")

                # Save/Discard buttons
                st.markdown("---")
                st.markdown("### Lưu Patterns?")

                col1, col2 = st.columns(2)

                with col1:
                    if st.button("Lưu Vào Dự Án", type="primary", use_container_width=True, key="save_patterns_btn"):
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

                            st.success("Đã lưu patterns vào dự án!")
                            st.balloons()
                            st.info("Bạn có thể sử dụng các patterns này khi đăng nội dung!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Lưu thất bại: {e}")
                            import traceback
                            st.code(traceback.format_exc())

                with col2:
                    if st.button("Hủy", use_container_width=True, key="discard_patterns_btn"):
                        # Clear session state
                        st.session_state.generated_patterns = None
                        st.session_state.patterns_project_id = None
                        st.info("Đã hủy patterns.")
                        st.rerun()

    except Exception as e:
        st.error(f"Lỗi khi tải dự án: {e}")

# ============================================
# Page: Publish Content
# ============================================

elif page == "Publish Content":
    st.title("Đăng Nội Dung Lên WordPress")
    st.markdown("---")

    # Fetch projects
    try:
        projects = list_projects(status='active')

        if not projects:
            st.warning("Không tìm thấy dự án. Vui lòng tạo dự án trước.")
            st.info("Đi đến trang 'Tạo Dự Án Mới' để thêm trang WordPress của bạn.")
        else:
            st.markdown("""
            ### Cách hoạt động:

            1. **Chọn dự án** (trang WordPress của bạn)
            2. **Dán URL Google Docs bất kỳ** (edit, view, hoặc published URL)
            3. **Nhấn Đăng Bài** và chờ phép màu xảy ra!

            Hệ thống sẽ:
            - Kết nối với Google Drive API (xác thực OAuth)
            - Chuyển đổi Google Docs sang HTML
            - Xử lý và tải ảnh lên
            - Áp dụng chuyển đổi HTML (nếu đã cấu hình)
            - Tạo bài viết nháp trên WordPress
            """)

            st.markdown("---")

            # Project selection OUTSIDE form for dynamic updates
            st.markdown("### Chọn Dự Án")

            project_options = {f"{p['project_name']} ({p['project_id']})": p['project_id'] for p in projects}
            project_options["Không Chọn Dự Án (Dùng mặc định)"] = None

            selected_display = st.selectbox(
                "Dự Án",
                options=list(project_options.keys()),
                help="Chọn trang WordPress để đăng bài",
                key="publish_project_selector"
            )
            selected_project_id = project_options[selected_display]

            # Load project data if selected
            project = None
            if selected_project_id:
                project = get_project(selected_project_id)
                st.info(f"Sẽ đăng lên: **{project['wordpress_url']}**")

            # Show main keyword input if project uses main_keyword naming (OUTSIDE form)
            main_keyword = ""
            if selected_project_id and project:
                image_configs = project.get('image_configs', {})
                naming_method = image_configs.get('naming_method', 'default')

                if naming_method == 'main_keyword':
                    st.markdown("### Từ Khóa Chính Để Đặt Tên Ảnh")
                    main_keyword = st.text_input(
                        "Từ Khóa Chính",
                        placeholder="vd: quat-tran-sunhouse",
                        help="Ảnh sẽ được đặt tên: tu-khoa-chinh-01, tu-khoa-chinh-02, v.v.",
                        key="publish_main_keyword"
                    )
                    if not main_keyword:
                        st.warning("Vui lòng cung cấp từ khóa chính để đặt tên ảnh")

            st.markdown("---")

            with st.form("publish_form"):
                st.markdown("### URL Google Docs")

                docs_url = st.text_input(
                    "URL Tài Liệu Nội Dung",
                    placeholder="https://docs.google.com/document/d/YOUR_DOC_ID/edit",
                    help="URL Google Docs bất kỳ: edit, view, hoặc published URLs"
                )

                st.markdown("---")

                # Show requirements
                with st.expander("Yêu Cầu"):
                    st.markdown("""
                    **Cài Đặt Google Docs:**
                    1. Mở tài liệu trong Google Docs
                    2. Copy URL từ trình duyệt (edit, view, hoặc published URL - đều hoạt động!)
                    3. Lần đầu: Trình duyệt sẽ mở để xác thực Google
                    4. Cấp quyền truy cập tài khoản Google của bạn

                    **Lưu ý:** OAuth credentials phải được cấu hình trong thư mục `credentials/`.

                    **Cài Đặt WordPress:**
                    - WordPress REST API phải được bật (mặc định trong WordPress 4.7+)
                    - Application Password phải hợp lệ
                    - Người dùng phải có quyền tạo bài viết
                    """)

                submit = st.form_submit_button("Đăng Lên WordPress", type="primary", use_container_width=True)

                if submit:
                    if not docs_url:
                        st.error("Vui lòng cung cấp URL Google Docs")

                    if docs_url:
                        # Execute workflow
                        st.markdown("---")
                        st.markdown("### Tiến Trình Đăng Bài")

                        progress_bar = st.progress(0)
                        status_text = st.empty()

                        try:
                            status_text.text("Đang bắt đầu quy trình...")
                            progress_bar.progress(10)

                            # Execute the actual workflow
                            with st.spinner("Đang đăng bài... Có thể mất 1-2 phút."):
                                result = execute_publishing_workflow(
                                    google_docs_url=docs_url,
                                    project_id=selected_project_id,
                                    main_keyword=main_keyword if main_keyword else None
                                )

                            progress_bar.progress(100)

                            # Show results
                            st.markdown("---")
                            if result['success']:
                                st.success("**Đăng bài hoàn tất thành công!**")

                                # Show details in columns
                                col1, col2, col3 = st.columns(3)

                                with col1:
                                    st.metric("Tiêu Đề Bài", result['post_title'])
                                with col2:
                                    st.metric("Số Ảnh Đã Xử Lý", result['images_processed'])
                                with col3:
                                    st.metric("Thời Gian", f"{result['execution_time']:.1f}s")

                                # Show links
                                st.markdown("### Liên Kết")
                                st.markdown(f"**Xem Bài Viết:** [{result['post_url']}]({result['post_url']})")
                                if result.get('edit_url'):
                                    st.markdown(f"**Chỉnh Sửa Bài:** [{result['edit_url']}]({result['edit_url']})")

                                st.info("**Lưu ý:** Bài viết được tạo dưới dạng NHÁP. Xem lại và xuất bản từ WordPress admin.")

                                # Show full result
                                with st.expander("Chi Tiết Kết Quả Đầy Đủ"):
                                    st.json(result)
                            else:
                                st.error("**Đăng bài thất bại!**")
                                st.error(f"**Lỗi:** {result.get('error', 'Lỗi không xác định')}")
                                st.error(f"**Thất bại tại bước:** {result.get('step_failed', 'Không xác định')}")

                                with st.expander("Thông Tin Debug"):
                                    st.json(result)

                        except Exception as e:
                            progress_bar.progress(0)
                            st.error(f"**Lỗi không mong muốn:** {e}")
                            import traceback
                            with st.expander("Chi Tiết Lỗi"):
                                st.code(traceback.format_exc())

    except Exception as e:
        st.error(f"Lỗi khi tải dự án: {e}")

# ============================================
# Page: Publishing History
# ============================================

elif page == "Publishing History":
    st.title("Lịch Sử Đăng Bài")
    st.markdown("---")

    st.info("Lịch sử đăng bài được lưu trong cơ sở dữ liệu Supabase.")

    st.markdown("""
    ### Xem Lịch Sử Qua Cơ Sở Dữ Liệu

    Bạn có thể truy vấn bảng `publishing_history` trực tiếp:

    ```sql
    SELECT * FROM publishing_history ORDER BY published_at DESC LIMIT 10;
    ```

    ### Sắp Ra Mắt
    - Xem các bài đăng gần đây
    - Lọc theo dự án
    - Thống kê thành công/thất bại
    - Nhật ký chi tiết
    """)

# ============================================
# Page: Batch Publish
# ============================================

elif page == "Batch Publish":
    st.title("Đăng Hàng Loạt Lên WordPress")
    st.markdown("---")

    # Initialize session state for batch data - use a simple list structure
    if 'batch_rows' not in st.session_state:
        st.session_state.batch_rows = [
            {'select': True, 'url': '', 'keyword': '', 'status': '⏳ Đang Chờ', 'title': '', 'post_url': ''}
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
            st.warning("Không tìm thấy dự án. Vui lòng tạo dự án trước.")
        else:
            # Project selection
            col1, col2 = st.columns([2, 1])
            with col1:
                project_options = {f"{p['project_name']} ({p['project_id']})": p['project_id'] for p in projects}
                selected_display = st.selectbox(
                    "Chọn Dự Án",
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
            st.markdown("**Dán các URL Google Docs vào bảng bên dưới:**")

            if uses_keyword_naming:
                st.info("🔑 Dự án này sử dụng **Từ Khóa Chính** để đặt tên ảnh. Nhập từ khóa cho mỗi URL.")

            # Table header - adjust columns based on whether keyword is needed
            if uses_keyword_naming:
                header_cols = st.columns([0.3, 2.5, 1.5, 0.8, 1, 1.5, 0.3])
                header_cols[0].markdown("**✓**")
                header_cols[1].markdown("**URL Google Docs**")
                header_cols[2].markdown("**Từ Khóa Chính**")
                header_cols[3].markdown("**Trạng Thái**")
                header_cols[4].markdown("**Tiêu Đề**")
                header_cols[5].markdown("**URL Bài Viết**")
                header_cols[6].markdown("**🗑️**")
            else:
                header_cols = st.columns([0.4, 3.5, 1, 1.3, 1.8, 0.4])
                header_cols[0].markdown("**✓**")
                header_cols[1].markdown("**URL Google Docs**")
                header_cols[2].markdown("**Trạng Thái**")
                header_cols[3].markdown("**Tiêu Đề Bài**")
                header_cols[4].markdown("**URL Bài Viết**")
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
                        placeholder="Dán URL Google Docs vào đây..."
                    )
                col_idx += 1

                if uses_keyword_naming:
                    with cols[col_idx]:
                        st.session_state.batch_rows[i]['keyword'] = st.text_input(
                            "keyword",
                            value=row.get('keyword', ''),
                            key=f"kw_{i}",
                            label_visibility="collapsed",
                            placeholder="vd: quat-tran"
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
                        st.markdown(f"[Xem]({row['post_url']})")
                    else:
                        st.markdown("—")
                col_idx += 1

                with cols[col_idx]:
                    if st.button("🗑️", key=f"del_{i}", help="Xóa dòng này"):
                        row_to_delete = i

            # Delete row if requested (after loop to avoid index issues)
            if row_to_delete is not None and len(st.session_state.batch_rows) > 1:
                st.session_state.batch_rows.pop(row_to_delete)
                st.rerun()

            st.markdown("---")

            # Buttons
            col1, col2, col3, col4 = st.columns([1, 1, 1, 1])

            with col1:
                if st.button("➕ Thêm Dòng", use_container_width=True):
                    st.session_state.batch_rows.append(
                        {'select': True, 'url': '', 'keyword': '', 'status': '⏳ Đang Chờ', 'title': '', 'post_url': ''}
                    )
                    st.rerun()

            with col2:
                if st.button("🗑️ Xóa Tất Cả", use_container_width=True):
                    st.session_state.batch_rows = [
                        {'select': True, 'url': '', 'keyword': '', 'status': '⏳ Đang Chờ', 'title': '', 'post_url': ''}
                        for _ in range(5)
                    ]
                    st.rerun()

            with col3:
                # Count valid URLs
                valid_count = sum(1 for r in st.session_state.batch_rows if r['select'] and r['url'].strip())
                st.caption(f"📊 {valid_count} đã chọn")

            with col4:
                process_btn = st.button("▶️ Xử Lý", type="primary", use_container_width=True)

            if process_btn:
                # Get rows to process
                rows_to_process = [(i, r) for i, r in enumerate(st.session_state.batch_rows)
                                   if r['select'] and r['url'].strip()]

                if not rows_to_process:
                    st.warning("Chưa chọn URL nào. Thêm URL và đánh dấu ô Chọn.")
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
                        status_text.text(f"Đang xử lý {j + 1}/{total}...")

                        # Update status
                        st.session_state.batch_rows[idx]['status'] = '🔄 Đang Xử Lý...'

                        try:
                            result = execute_publishing_workflow(
                                google_docs_url=url,
                                project_id=selected_project_id,
                                main_keyword=keyword if keyword else None
                            )

                            if result['success']:
                                st.session_state.batch_rows[idx]['status'] = '✅ Thành Công'
                                st.session_state.batch_rows[idx]['title'] = result.get('post_title', '')
                                st.session_state.batch_rows[idx]['post_url'] = result.get('post_url', '')
                                success_count += 1
                            else:
                                error_msg = result.get('error', 'Unknown')[:25]
                                st.session_state.batch_rows[idx]['status'] = f'❌ Thất Bại'
                                failed_count += 1

                        except Exception as e:
                            st.session_state.batch_rows[idx]['status'] = f'❌ Lỗi'
                            failed_count += 1

                    progress_bar.progress(1.0)
                    status_text.empty()

                    if success_count > 0:
                        st.success(f"✅ Đã đăng {success_count} bài viết!")
                    if failed_count > 0:
                        st.error(f"❌ {failed_count} thất bại")

                    st.rerun()

    except Exception as e:
        st.error(f"Lỗi: {e}")

# ============================================
# Footer
# ============================================

st.sidebar.markdown("---")
st.sidebar.markdown("### Mẹo")
st.sidebar.markdown("""
1. **URL Google Docs bất kỳ đều hoạt động** (edit, view, hoặc published)
2. **Sử dụng App Password của WordPress** (không phải mật khẩu thông thường)
3. **Bài viết được tạo dưới dạng nháp** để an toàn
4. **Lần chạy đầu tiên cần Google OAuth** (trình duyệt mở một lần)
""")
