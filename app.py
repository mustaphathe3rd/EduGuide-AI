import streamlit as st
import os
from src.utils import load_student_profile, format_profile_for_ai, get_all_profiles
from src.chains import get_tutor_response, get_advisor_response
from src.safety import check_safety_risk  # <--- NEW IMPORT

# 1. CONFIG & STYLING
st.set_page_config(page_title="EduGuide AI", page_icon="🎓", layout="wide")

# Custom CSS for Color
st.markdown("""
<style>
    /* Gradient Background for Headers */
    .stAppHeader {
        background: linear-gradient(90deg, #0f2027 0%, #203a43 50%, #2c5364 100%);
        color: white;
    }
    
    /* Chat Message Styling - Force Black Text on Colored Bubbles */
    .stChatMessage {
        border-radius: 15px;
        padding: 10px;
        color: black !important; /* Force text to be black so it's readable */
    }
    
    /* User Bubble (Bright Blue) */
    [data-testid="stChatMessage"]:nth-child(odd) {
        background-color: #bbdefb; 
        border-left: 5px solid #1976d2;
    }
    
    /* AI Bubble (Bright Purple) */
    [data-testid="stChatMessage"]:nth-child(even) {
        background-color: #e1bee7;
        border-left: 5px solid #7b1fa2;
    }
    
    /* Sidebar Styling - Dark Gradient */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e1e2f 0%, #252540 100%);
        color: white !important;
    }
    
    /* Fix Sidebar Text Contrast */
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

# 2. SIDEBAR LOGIC
with st.sidebar:
    st.title("🎓 EduGuide Settings")
    
    st.subheader("👤 Student Profile")
    
    # Get all files
    profile_files = get_all_profiles()
    
    if profile_files:
        # NEW LOGIC: Create a mapping of {filename: Student Name}
        file_to_name = {}
        for file in profile_files:
            file_path = os.path.join("data/student_profiles", file)
            profile_data = load_student_profile(file_path)
            # Use the name from the JSON, or fallback to filename if missing
            file_to_name[file] = profile_data.get("name", file)

        # Update Selectbox to show names, but return the filename
        selected_file = st.selectbox(
            "Active Student:", 
            options=profile_files,
            format_func=lambda x: file_to_name.get(x, x) # <--- This handles the display
        )

        # Load the selected profile logic (Same as before)
        profile_path = os.path.join("data/student_profiles", selected_file)
        student_data = load_student_profile(profile_path)
        formatted_profile = format_profile_for_ai(student_data)
        
        # Colorful Metrics
        col1, col2 = st.columns(2)
        col1.metric("GPA", student_data.get("gpa", "N/A"))
        col2.metric("Year", student_data.get("year", "N/A"))
        
        status = student_data.get("academic_standing", "Unknown")
        if student_data.get("gpa", 0) < 2.5:
            st.error(f"⚠ {status}")
        else:
            st.success(f"✅ {status}")
            
    else:
        st.error("No profiles found!")
        formatted_profile = ""

    st.divider()
    
    st.subheader("🧠 Mode Selection")
    mode = st.radio("Assistant Role:", ["📚 Socratic Tutor", "🎓 Academic Advisor"])
    
    if st.button("🧹 Clear Chat", type="primary"):
        st.session_state.messages = []
        st.rerun()

# 3. MAIN APP
st.title("EduGuide Assistant")
st.caption("Your AI-powered Academic Success Partner")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display History
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 4. CHAT LOGIC (WITH SAFETY CHECK)
if prompt := st.chat_input("Ask a question..."):
    # User Message
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Assistant Response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            
            # A. SAFETY CHECK FIRST
            safety_msg = check_safety_risk(prompt)
            
            if safety_msg:
                # If unsafe, print warning and stop
                response = safety_msg
                st.error(response) # Make it red
            
            # B. STANDARD AI RESPONSE
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