# 🎓 EduGuide AI Assistant

**EduGuide** is an intelligent academic support system designed to bridge the gap between "homework help" and "student success."

Unlike generic chatbots, EduGuide utilizes a **Dual-Brain Architecture**:
1. **The Socratic Tutor (RAG):** Uses Retrieval-Augumented Generation to answer course-specific questions using only verified textbooks and syllabi.
2. **The Academic Advisor(COntext-Aware):** Analyzes real-time student data(grades, attendance, major) to provide strategic, empathetic intervention.

## 🚀 Key Features

* **📘 Zero-Hallucination Tutoring:** Answers are grounded in uploaded PDF course materials.
* **📊 Context-Aware Advising:** Detects failing grades/attendance issues and adjusts advice accordingly.
* **🛡️ Safety Guardrails:** Hard-coded intervention layer that detects crisis keywords (e.g., "depression") and routes students to campus resources immediately.
* **🎨 Dynamic UI:** Interface changes based on student standing (e.g., visual cues for "Dean's List" vs. "Probation").

## 🛠️ Tech Stack

* **Frontend:** Streamlit (Python)
* **Orchestration:** LangChain
* **LLM:** Google Gemini Pro
* **Vector Database:** FAISS (Local)
* **EMBEDDINGS:** Google Gemini EMbeddings (`models/gemini-embedding-001`)

## 📦 Installation & Setup

1. **Clone/Download the Repository**
```bash
git clone <your-repo-url>
cd EduGuide
```

2. **Create Virtual Environment (Python 3.11 Recommended)**
```bash
python3.11 -m venv venv
source venv/bin/activate # Windows: venv\Scripts\activate
```

3. **Install Dependencies**
```bash
pip install -r requirements.tsx
```

4. **Configure API Keys**
Create a `.env` file in the root directory:
```env
GOOGLE_api_key=your_gemini_api_key_here
```

## 🏃‍♂️ How to Run

**Step 1: Build the Knowledge Base**
Process the PDF textbooks into the Vector Store. (Run this once).
```bash
python src/ingestion.py
```

**Step 2: Launch the Application**
Start the web interface.
```bash
python -m streamlit run app.py
```

