import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.utils import load_student_profile, format_profile_for_ai
from src.chains import get_tutor_response, get_advisor_response


# 1. Load the mock profile
# Make sure this matches the file name you created in Day 1/2
PROFILE_PATH = "data/student_profiles/student_data.json" 

if not os.path.exists(PROFILE_PATH):
    # Fallback if you didn't create it yet
    print(f"⚠️ File not found: {PROFILE_PATH}. Creating a dummy one...")
    import json
    dummy_data = {"name": "Test User", "major": "CS", "gpa": 2.0, "courses": {"Math": {"grade": "F", "attendance": "40%"}}}
    with open(PROFILE_PATH, "w") as f:
        json.dump(dummy_data, f)

profile_data = load_student_profile(PROFILE_PATH)
formatted_profile = format_profile_for_ai(profile_data)

print("🧠 EDUGUIDE BRAIN INITIALIZED")
print("------------------------------------------------")

while True:
    print("\nSelect Mode:")
    print("1. 📚 Tutor (Ask about your PDF)")
    print("2. 🎓 Advisor (Ask about your Grades/Advice)")
    print("q. Quit")
    
    choice = input("Choice (1/2/q): ")
    
    if choice == 'q':
        break
        
    question = input("Your Question: ")
    print("\nThinking...")
    
    try:
        if choice == '1':
            # Run the RAG Chain
            response = get_tutor_response(question)
            print(f"\n[Tutor]: {response}")
            
        elif choice == '2':
            # Run the Advisor Chain (Injecting the profile)
            response = get_advisor_response(question, formatted_profile)
            print(f"\n[Advisor]: {response}")
            
        else:
            print("Invalid choice.")
            
    except Exception as e:
        print(f"❌ Error: {e}")