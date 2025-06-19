import streamlit as st
from datetime import datetime
import os
from database import (
    init_db,
    insert_upload,
    validate_admin,
    get_all_uploads,
    UPLOAD_FOLDER
)
st.set_page_config(page_title="LMS Portal", layout="centered",page_icon="📚")

# Hiding Streamlit UI elements
hide_st_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    }
    </style>
"""
st.markdown(hide_st_style, unsafe_allow_html=True)

# Initialize database
init_db()

# ---------------------
# Session State Setup
# ---------------------
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'admin_user' not in st.session_state:
    st.session_state.admin_user = None

# ---------------------
# Student Upload Section
# ---------------------
st.header("LMS :red[(Learning Management System)] ")
st.subheader("Egra Vidyasagar National Youth Computer Centre")
def student_page():
    st.title("📚 Student File Upload")

    name = st.text_input("Enter your name")
    student_id = st.text_input("Enter your student ID")
    files = st.file_uploader("Upload Practical Word Files", type=['docx'], accept_multiple_files=True)

    if st.button("Upload"):
        if not name or not student_id or not files:
            st.error("Please fill in all fields and upload at least one file.")
        else:
            for file in files:
                timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                filename = f"{student_id}_{timestamp}_{file.name}"
                filepath = os.path.join(UPLOAD_FOLDER, filename)

                with open(filepath, "wb") as f:
                    f.write(file.getbuffer())

                insert_upload(name, student_id, file.name, filepath, timestamp)

            st.success(f"Successfully uploaded {len(files)} file(s).")

# ---------------------
# Admin Login & Dashboard
# ---------------------
def admin_page():
    st.title("🔐 Master Dashboard")

    if st.session_state.logged_in:
        st.success(f"Logged in as: {st.session_state.admin_user}")
        if st.button("🚪 Logout"):
            st.session_state.logged_in = False
            st.session_state.admin_user = None
            st.rerun()
        show_admin_dashboard()
        return

    # Login Form
    username = st.text_input("Admin Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if validate_admin(username, password):
            st.session_state.logged_in = True
            st.session_state.admin_user = username
            st.success("Login successful!")
            st.rerun()
        else:
            st.error("Invalid username or password.")

# ---------------------
# Admin Dashboard View
# ---------------------
def show_admin_dashboard():
    st.subheader("📂 Uploaded Files")

    uploads = get_all_uploads()

    if not uploads:
        st.info("No uploads found.")
        return
    
    # Show summary
    student_ids = [row[2] for row in uploads]
    total_unique_students = len(set(student_ids))
    total_files = len(uploads)

    st.markdown(f"📊 **Total students who uploaded files:** `{total_unique_students}`")
    st.markdown(f"📄 **Total uploaded files:** `{total_files}`")

    # Extract unique student names and IDs
    student_names = sorted(set(row[1] for row in uploads))
    student_ids = sorted(set(row[2] for row in uploads))

    # Dropdown filters
    selected_name = st.selectbox("🎓 Filter by Student Name", options=["All"] + student_names)
    selected_id = st.selectbox("🆔 Filter by Student ID", options=["All"] + student_ids)

    # Apply filters
    filtered_uploads = uploads
    if selected_name != "All":
        filtered_uploads = [row for row in filtered_uploads if row[1] == selected_name]
    if selected_id != "All":
        filtered_uploads = [row for row in filtered_uploads if row[2] == selected_id]

    # Display filtered results
    if not filtered_uploads:
        st.warning("No uploads match the selected filters.")
        return

    for row in filtered_uploads:
        st.markdown(f"**Student Name:** {row[1]} | **ID:** {row[2]}")
        st.markdown(f"**File:** {row[3]} | **Uploaded at:** {row[5]}")
        with open(row[4], "rb") as f:
            st.download_button(label="📥 Download", data=f, file_name=row[3], key=row[0])


# ---------------------
# Navigation
# ---------------------
tab1, tab2 = st.tabs(["📘Student Exam Files upload","🏫Master Login"])

with tab1:
    student_page()
with tab2:
    admin_page()
