# 🎓 EduBuddy - AI-Powered Learning Assistant

**EduBuddy** is a comprehensive, AI-driven educational platform designed to enhance the learning experience through Retrieval-Augmented Generation (RAG), strict topic-based quizzing, and personalized progress tracking.

---

## 🚀 Key Features

### 🔐 **Secure & Generalized Authentication**
*   **Universal Access**: Signup as a **Student**, **Teacher**, or **Professional**.
*   **Privacy First**: All uploaded files are processed in **ephemeral memory** and securely wiped upon logout or reset.
*   **Facebook-Style Sidebar**: Edit your profile, bio, and view your stats.

### 📚 **RAG-Powered Study Companion**
*   **Smart Ingestion**: Upload PDFs, DOCX, or Images. The system automatically extracts chapters and topics (even from deep within large headers).
*   **Topic-Scoped Chat**: Chat with a specific topic or the entire document.
*   **Strict Summarizer**: Get summaries strictly based on the selected topic content.

### 🧠 **Intelligent Assessment**
*   **Topic-Specific Quizzes**: Generate MCQs for specific chapters.
*   **Strict Certification**: Unlock the **Course Certificate** only after scoring **>70% in ALL topics**.
*   **Detailed Analytics**: Track learning speed, weak areas, and score trends.

### 🛡️ **Admin Dashboard**
*   **Analytics**: View time-series login trends and file ingestion statistics.
*   **User Management**: Block/Unblock users.
*   **Data Control**: Manually wipe persistent analytics data with a single click.

---

## 🛠️ Installation & Setup

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/saify09/Final_Project.git
    cd Final_Project
    ```

2.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the Application**
    ```bash
    streamlit run app.py
    ```

---

## 📂 Project Structure

```
final project/
├── app.py                 # Main Streamlit Application Entry Point
├── requirements.txt       # Python Dependencies
├── src/
│   ├── auth/              # User Management & Authentication Logic
│   ├── embed/             # Vector Store & Embedding Logic (FAISS)
│   ├── ingest/            # Document Parsing (PDF/DOCX/OCR) & Topic Extraction
│   ├── rag/               # Retrieval & Generation (LLM Integration)
│   ├── ui/                # specialized UI Components (Sidebar, Auth, Admin)
│   └── utils/             # Helpers (Reporter, Analytics, Quiz Gen)
└── README.md              # Project Documentation
```

---

## 💡 Usage Guide

1.  **Sign Up**: Create an account with your Profession and Bio.
2.  **Upload**: Go to the **Home** tab and upload your study materials.
3.  **Study**: Use the **Study** tab to chat with your documents or get summaries.
4.  **Quiz**: Test your knowledge in the **Quiz** tab.
5.  **Progress**: Track your scores. Once you pass all topics (>70%), download your **Certificate**!

---

## 🔒 Privacy Notice
*   **File Content**: Stored in RAM only. Wiped on Logout/Reset.
*   **User Data**: Stored locally in `edubuddy_users.db` (hashed passwords).
*   **Analytics**: Metadata (filenames, timestamps) is logged for the Admin but can be deleted via the Dashboard.

---

**Developed by Saifuddin Hanif** | Final Project
