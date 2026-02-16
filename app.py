import streamlit as st
import os
import json
from src.utils import load_student_profile, format_profile_for_ai, get_all_profiles
from src.chains import get_tutor_response, get_advisor_response
from src.safety import check_safety_risk
from src.ingestion import ingest_new_files  # <--- NEW IMPORT

# 1. CONFIG & STYLING
st.set_page_config(page_title="EduGuide AI", page_icon="🎓", layout="wide")

st.markdown("""
<style>
    .stAppHeader { background: linear-gradient(90deg, #000428 0%, #004e92 100%); color: white; }
    .stChatMessage .stMarkdown { color: black !important; }
    .stChatMessage p { color: black !important; }
    [data-testid="stChatMessage"]:nth-child(odd) { background-color: #BBDEFB !important; border-left: 5px solid #1976D2; border-radius: 15px; padding: 15px; margin-bottom: 10px; }
    [data-testid="stChatMessage"]:nth-child(even) { background-color: #F5F5F5 !important; border-left: 5px solid #616161; border-radius: 15px; padding: 15px; margin-bottom: 10px; }
    [data-testid="stSidebar"] { background-color: #1a1a2e; }
</style>
""", unsafe_allow_html=True)

# 2. SIDEBAR LOGIC
with st.sidebar:
    st.title("🎓 EduGuide Settings")
    
    # --- SECTION A: CUSTOM DATA UPLOAD ---
    with st.expander("📂 Upload Your Data", expanded=True):
        
        # 1. Student Profile Upload (JSON)
        uploaded_json = st.file_uploader("Upload Grades (JSON)", type="json")
        
        # 2. Course Material Upload (PDF)
        uploaded_pdfs = st.file_uploader("Upload Textbooks (PDF)", type="pdf", accept_multiple_files=True)
        if uploaded_pdfs and st.button("Process Books"):
            with st.spinner("Reading books & building Brain..."):
                status = ingest_new_files(uploaded_pdfs)
                st.success(status)

    st.divider()

    # --- SECTION B: PROFILE SELECTION ---
    st.subheader("👤 Active Profile")
    
    # Logic: If user uploaded a JSON, use it. Otherwise, use the Dropdown.
    if uploaded_json is not None:
        # Load from the uploaded file directly
        student_data = json.load(uploaded_json)
        st.info(f"Using Uploaded Profile: {student_data.get('name', 'Custom User')}")
    else:
        # Fallback to Demo Profiles
        profile_files = get_all_profiles()
        if profile_files:
            file_to_name = {}
            for file in profile_files:
                file_path = os.path.join("data/student_profiles", file)
                prof = load_student_profile(file_path)
                file_to_name[file] = prof.get("name", file)

            selected_file = st.selectbox(
                "Select Demo Student:", 
                options=profile_files,
                format_func=lambda x: file_to_name.get(x, x)
            )
            profile_path = os.path.join("data/student_profiles", selected_file)
            student_data = load_student_profile(profile_path)
        else:
            student_data = {}

    # Format the data for the AI
    formatted_profile = format_profile_for_ai(student_data)
        
    # Display Stats
    col1, col2 = st.columns(2)
    col1.metric("GPA", student_data.get("gpa", "N/A"))
    col2.metric("Year", student_data.get("year", "N/A"))
    
    status = student_data.get("academic_standing", "Unknown")
    if str(student_data.get("gpa", 0)) < "2.5": # String comparison is safer for N/A cases
        st.error(f"⚠ {status}")
    else:
        st.success(f"✅ {status}")

    st.divider()
    
    # --- SECTION C: MODE & CHAT CONTROLS ---
    mode = st.radio("Assistant Role:", ["📚 Socratic Tutor", "🎓 Academic Advisor"])
    
    if st.button("🧹 Clear Chat", type="primary"):
        st.session_state.messages = []
        st.rerun()

# 3. MAIN CHAT APP
st.title("EduGuide Assistant")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Ask a question..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            safety_msg = check_safety_risk(prompt)
            if safety_msg:
                response = safety_msg
                st.error(response)
            else:
                try:
                    if "Tutor" in mode:
                        response = get_tutor_response(prompt)
                    else:
                        response = get_advisor_response(prompt, formatted_profile)
                    st.markdown(response)
                except Exception as e:
                    response = f"❌ Error: {str(e)}"
                    st.error(response)
                    
            st.session_state.messages.append({"role": "assistant", "content": response})