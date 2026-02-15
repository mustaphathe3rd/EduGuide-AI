import json
import os

def load_student_profile(filepath):
    """
    Loads the student's data from a JSON file.
    """
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
        return data
    except Exception as e:
        return {"error": str(e)}

def format_profile_for_ai(profile):
    """
    Converts the JSON object into a readable string for the AI.
    """
    if "error" in profile:
        return "No profile data available."
    
    text = f"Student Name: {profile.get('name', 'Unknown')}\n"
    text += f"Major: {profile.get('major', 'Undeclared')}\n"
    text += f"Year: {profile.get('year', 'N/A')}\n"
    text += f"GPA: {profile.get('gpa', 'N/A')} ({profile.get('academic_standing')})\n"
    text += "Current Courses:\n"
    
    courses = profile.get("courses", {})
    for code, details in courses.items():
        text += f"- {code} ({details.get('name')}): Grade {details.get('grade')}, Attendance {details.get('attendance')}\n"
        
    return text

def get_all_profiles():
    """
    Scans the data/student_profiles folder and returns a list of filenames.
    """
    profile_dir = "data/student_profiles"
    if not os.path.exists(profile_dir):
        return []
    return [f for f in os.listdir(profile_dir) if f.endswith('.json')]