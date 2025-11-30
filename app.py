import streamlit as st
import sys
# print("DEBUG: Streamlit imported", flush=True)
import os
import pandas as pd
import numpy as np
# print("DEBUG: Pandas imported")
import plotly.express as px
import plotly.graph_objects as go
from ui.styles import load_css
from ui.components import header, card_start, card_end, student_info_sidebar
from src.ingest.text_parser import parse_file
from src.ingest.chunker import process_file_content
from src.embed.embedder import Embedder
from src.embed.indexer import VectorStore
from src.rag.retriever import Retriever
from src.rag.generator import Generator
from src.rag.pipeline import RAGPipeline
from src.utils.summarizer import Summarizer
from src.utils.quiz_generator import QuizGenerator
from src.utils.reporter import generate_pdf_report

from src.utils.analytics import AnalyticsEngine

# Page Config
st.set_page_config(page_title="EduBuddy", page_icon="🎓", layout="wide")
st.markdown(load_css(), unsafe_allow_html=True)

@st.cache_resource
def load_generator():
    return Generator()

@st.cache_resource
def load_summarizer():
    return Summarizer()

# Session State Initialization
if 'vector_store' not in st.session_state:
    st.session_state.vector_store = VectorStore()
if 'embedder' not in st.session_state:
    st.session_state.embedder = Embedder() # Load once
if 'rag_pipeline' not in st.session_state:
    retriever = Retriever(st.session_state.embedder, st.session_state.vector_store)
    with st.spinner("Loading LLM... This may take a while for the first time."):
        generator = load_generator()
    st.session_state.rag_pipeline = RAGPipeline(retriever, generator)
if 'processed_files' not in st.session_state:
    st.session_state.processed_files = []
if 'quiz_history' not in st.session_state:
    st.session_state.quiz_history = []
if 'quiz_history_detailed' not in st.session_state:
    st.session_state.quiz_history_detailed = []

def main():
    student_info_sidebar()
    
    # Top Navigation (Web-like Tabs)
    tab_home, tab_study, tab_quiz, tab_progress = st.tabs(["🏠 Home", "💬 Study", "🧠 Quiz", "📈 Progress"])

    with tab_home:
        render_home()
    
    with tab_study:
        render_study()
        
    with tab_quiz:
        render_quiz()
        
    with tab_progress:
        render_progress()

def render_home():
    print("DEBUG: Rendering Home Page", flush=True)
    header("🎓 EduBuddy", "Your AI-Powered Offline Learning Companion")
    
    st.markdown("### 📂 Upload Study Materials")
    
    # Input Method Toggle
    input_method = st.radio("Choose Input Method:", ["📁 Upload Files", "📷 Use Webcam"], horizontal=True)
    
    files_to_process = []
    
    if input_method == "📁 Upload Files":
        uploaded_files = st.file_uploader("Upload Files (PDF, DOCX, TXT, Images, Videos)", accept_multiple_files=True, type=['pdf', 'docx', 'txt', 'md', 'py', 'png', 'jpg', 'jpeg', 'mp4', 'avi', 'mov'])
        if uploaded_files:
            files_to_process.extend(uploaded_files)
            
    elif input_method == "📷 Use Webcam":
        camera_image = st.camera_input("Take a picture of notes")
        if camera_image:
            camera_image.name = "camera_capture.jpg"
            files_to_process.append(camera_image)
    
    if files_to_process:
        if st.button("Process & Index Files"):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for i, uploaded_file in enumerate(files_to_process):
                if uploaded_file.name in st.session_state.processed_files:
                    continue
                
                status_text.text(f"Processing {uploaded_file.name}...")
                
                # Save temp file
                with open(uploaded_file.name, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                # Parse
                text = parse_file(uploaded_file.name)
                
                # Chunk
                chunks = process_file_content(uploaded_file.name, text)
                
                # Embed & Index
                embeddings = st.session_state.embedder.embed_chunks([c['text'] for c in chunks])
                st.session_state.vector_store.add_embeddings(embeddings, chunks)
                
                st.session_state.processed_files.append(uploaded_file.name)
                
                # Cleanup
                os.remove(uploaded_file.name)
                progress_bar.progress((i + 1) / len(files_to_process))
            
            status_text.success("All files processed and indexed successfully!")
            st.session_state.vector_store.save("data/index")
            # Auto-navigation removed as requested

    st.markdown("---")
    st.markdown("### 📚 Knowledge Base Stats")
    col1, col2 = st.columns(2)
    col1.metric("Documents Indexed", len(st.session_state.processed_files))
    col2.metric("Total Chunks", len(st.session_state.vector_store.metadata))

def render_study():
    st.header("💬 Study Assistant")
    
    if not st.session_state.processed_files:
        st.warning("Please upload documents in Home first.")
        return

    query = st.text_input("Ask a question about your documents:")
    if query:
        with st.spinner("Thinking..."):
            result = st.session_state.rag_pipeline.answer(query)
            
        st.markdown("### Answer")
        st.success(result['answer'])
        
        with st.expander("View Sources"):
            for doc in result['source_documents']:
                st.markdown(f"**Source:** {doc['source']} (Score: {doc['score']:.4f})")
                st.text(doc['text'][:200] + "...")

    st.divider()
    st.subheader("📝 Document Summarizer")
    doc_to_summarize = st.selectbox("Select document to summarize", st.session_state.processed_files)
    if doc_to_summarize and st.button("Generate Summary"):
        # We need to re-read or store full text. For now, let's just retrieve all chunks for this doc from metadata
        doc_text = " ".join([m['text'] for m in st.session_state.vector_store.metadata if m['source'] == doc_to_summarize])
        
        with st.spinner("Generating summary..."):
            summ = load_summarizer()
            summary = summ.summarize(doc_text, sentences_count=5)
        st.info(summary)

def render_quiz():
    st.header("🧠 Knowledge Quiz")
    
    if not st.session_state.processed_files:
        st.warning("Please upload documents first.")
        return

    if st.button("Generate New Quiz"):
        with st.spinner("Generating quiz questions..."):
            # Pass full metadata (list of dicts) to generator
            all_docs = st.session_state.vector_store.metadata
            qg = QuizGenerator()
            st.session_state.current_quiz = qg.generate_mcq(all_docs, num_questions=5)
            st.session_state.quiz_answers = {}

    if 'current_quiz' in st.session_state:
        with st.form("quiz_form"):
            score = 0
            for i, q in enumerate(st.session_state.current_quiz):
                st.markdown(f"**Q{i+1}: {q['question']}**")
                choice = st.radio(f"Select answer for Q{i+1}", q['options'], key=f"q_{i}")
                st.session_state.quiz_answers[i] = choice
            
            submitted = st.form_submit_button("Submit Quiz")
            if submitted:
                st.write("### Quiz Results:")
                for i, q in enumerate(st.session_state.current_quiz):
                    user_choice = st.session_state.quiz_answers.get(i)
                    correct_choice = q['answer']
                    
                    st.markdown(f"**Q{i+1}: {q['question']}**")
                    if user_choice == correct_choice:
                        st.success(f"✅ Correct! Answer: {correct_choice}")
                        score += 1
                        is_correct = True
                    else:
                        st.error(f"❌ Wrong! You selected: {user_choice}. Correct Answer: {correct_choice}")
                        is_correct = False
                    
                    # Log detailed result
                    st.session_state.quiz_history_detailed.append({
                        "question": q['question'],
                        "is_correct": is_correct,
                        "source": q.get('source', 'Unknown'),
                        "timestamp": pd.Timestamp.now()
                    })
                
                if score > 3:
                    st.balloons()
                st.info(f"**Final Score: {score}/{len(st.session_state.current_quiz)}**")
                st.session_state.quiz_history.append(score)

def render_progress():
    st.header("📈 Learning Progress")
    
    if not st.session_state.quiz_history:
        st.info("Take some quizzes to see your progress!")
        return

    # Mock data for visualization if history is short
    data = st.session_state.quiz_history
    if len(data) < 2:
        st.write("Not enough data for trend analysis.")
    
    df = pd.DataFrame({"Quiz Attempt": range(1, len(data) + 1), "Score": data})
    
    # Forecasting
    forecast = AnalyticsEngine.forecast_next_score(data)
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Average Score", f"{np.mean(data):.2f}")
    col2.metric("Predicted Next Score", f"{forecast['predicted_score']}" if forecast['predicted_score'] is not None else "N/A", delta=forecast['trend'])
    col3.metric("Total Quizzes", len(data))
    
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        st.subheader("Score Trend")
        fig = px.line(df, x="Quiz Attempt", y="Score", markers=True, title="Quiz Scores Over Time")
        # Add trend line if possible or just rely on the metric
        st.plotly_chart(fig, use_container_width=True)
        
    with col_chart2:
        st.subheader("Performance Distribution")
        fig2 = px.histogram(df, x="Score", nbins=5, title="Score Distribution")
        st.plotly_chart(fig2, use_container_width=True)

    # --- Advanced Analytics ---
    st.divider()
    st.subheader("🧠 Deep Dive Analytics")
    
    # Calculate Metrics
    weak_areas = AnalyticsEngine.analyze_weak_areas(st.session_state.quiz_history_detailed)
    learning_metrics = AnalyticsEngine.calculate_learning_metrics(forecast.get('slope', 0), np.mean(data))
    
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.markdown("#### ⚠️ Weak Topics (Needs Revision)")
        if weak_areas:
            for source, error_rate in weak_areas.items():
                st.progress(error_rate, text=f"{source} (Error Rate: {int(error_rate*100)}%)")
        else:
            st.success("No weak areas detected yet! Keep it up.")
            
    with col_b:
        st.markdown("#### 🚀 Learning Velocity")
        st.metric("Learning Speed", learning_metrics['learning_speed'])
        st.metric("Time to Mastery", learning_metrics['time_to_mastery'])
        
        if weak_areas:
            st.info(f"💡 Recommendation: Review **{list(weak_areas.keys())[0]}** before next quiz.")

    st.divider()
    if st.button("📄 Download Progress Report (PDF)"):
        # Prepare analytics dict
        analytics_data = {
            "average": f"{np.mean(data):.2f}",
            "predicted_score": f"{forecast['predicted_score']}" if forecast['predicted_score'] is not None else "N/A",
            "trend": forecast['trend'],
            "weak_areas": weak_areas,
            "learning_metrics": learning_metrics
        }
        
        # Use session state info or defaults
        s_name = st.session_state.get("student_name", "Student")
        s_roll = st.session_state.get("roll_no", "N/A")
        
        pdf_bytes = generate_pdf_report(s_name, s_roll, st.session_state.quiz_history, analytics_data)
        st.download_button(
            label="Click to Download",
            data=pdf_bytes,
            file_name="EduBuddy_Report.pdf",
            mime="application/pdf"
        )

if __name__ == "__main__":
    main()
