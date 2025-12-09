import streamlit as st
import os
import pandas as pd
import numpy as np
import toml

# Import UI components
from src.ui.auth_ui import render_auth
from src.ui.sidebar import render_sidebar
from src.ui.styles import load_css
from src.ui.admin_ui import render_admin_dashboard

# --- Page Config ---
st.set_page_config(
    page_title="EduBuddy",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)
st.markdown(load_css(), unsafe_allow_html=True)

# --- Session State Init ---
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user' not in st.session_state:
    st.session_state.user = None
if 'processed_files' not in st.session_state:
    st.session_state.processed_files = []
if 'vector_store' not in st.session_state:
    st.session_state.vector_store = None
if 'quiz_history' not in st.session_state:
    st.session_state.quiz_history = []
if 'quiz_history_detailed' not in st.session_state:
    st.session_state.quiz_history_detailed = []
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'selected_topic' not in st.session_state:
    st.session_state.selected_topic = "All Topics"

def main():
    if not st.session_state.authenticated:
        render_auth()
        return

    # Render Profile Sidebar
    render_sidebar()
    
    # --- Top Navigation Tabs ---
    options = ["Home", "Study", "Quiz", "Progress"]
    if st.session_state.user and st.session_state.user.get('username') == 'admin':
        options.append("Admin")
        
    tabs = st.tabs(options)
    
    for i, tab in enumerate(tabs):
        with tab:
            page = options[i]
            if page == "Home":
                render_home()
            elif page == "Study":
                render_study()
            elif page == "Quiz":
                render_quiz()
            elif page == "Progress":
                render_progress()
            elif page == "Admin":
                render_admin_dashboard()

def render_home():
    col1, col2 = st.columns([2, 1])
    with col1:
        st.info("Upload your study materials here. We support PDF, DOCX, Images, and Videos.")
        
    input_method = st.radio("Choose Input Method:", ["📁 Upload Files", "📷 Use Webcam"], horizontal=True)
    
    # Cached Embedder Loader
    @st.cache_resource
    def get_embedder():
        from src.embed.embedder import Embedder
        return Embedder()

    if input_method == "📁 Upload Files":
        uploaded_files = st.file_uploader("Upload Files", 
                                        type=['pdf', 'docx', 'txt', 'md', 'png', 'jpg', 'jpeg', 'mp4', 'avi'], 
                                        accept_multiple_files=True)
        if st.button("Process & Index Files", type="primary", width="stretch"):
            if uploaded_files:
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                try:
                    status_text.text("📂 Saving files securely...")
                    
                    import tempfile
                    import shutil
                    
                    # Use a local temporary directory to avoid cross-drive Watchdog errors
                    local_temp_dir = os.path.join(os.getcwd(), "temp_ingest")
                    if not os.path.exists(local_temp_dir):
                        os.makedirs(local_temp_dir)

                    # Use custom cleanup instead of TemporaryDirectory context manager if needed, 
                    # but context manager with 'dir=' works best.
                    with tempfile.TemporaryDirectory(dir=local_temp_dir) as temp_dir:
                        saved_paths = []
                        for uf in uploaded_files:
                            path = os.path.join(temp_dir, uf.name)
                            with open(path, "wb") as f:
                                f.write(uf.getbuffer())
                            saved_paths.append(path)
                        
                        progress_bar.progress(20)
                        
                        # Ingest
                        status_text.text("📖 Parsing and Chunking content...")
                        from src.ingest.ingestor import Ingestor
                        ingestor = Ingestor()
                        chunks = ingestor.ingest(saved_paths)
                        
                        # Note: We can't store 'saved_paths' in session_state if they are deleted.
                        # We should store just the names or metadata.
                        st.session_state.processed_files = [os.path.basename(p) for p in saved_paths]
                        
                        progress_bar.progress(50)
                        
                        # Embed & Store
                        status_text.text("🧠 Generating Embeddings (this may take a moment)...")
                        from src.embed.indexer import VectorStore
                        
                        embedder = get_embedder()
                        texts = [c['text'] for c in chunks]
                        embeddings = embedder.embed_chunks(texts)
                        
                        progress_bar.progress(80)
                        
                        status_text.text("💾 Storing in Vector Database...")
                        vector_store = VectorStore()
                        vector_store.add_embeddings(embeddings, chunks)
                        
                        st.session_state.vector_store = vector_store
                        
                        progress_bar.progress(100)
                        status_text.text("✅ Done!")
                        st.success(f"Successfully processed {len(saved_paths)} files!")
                        st.balloons()
                    

                    
                except Exception as e:
                    st.error(f"An error occurred: {e}")
                    
            else:
                st.warning("Please upload files first.")
        
        st.divider()
        if st.button("🗑️ Reset / Clear All Data", type="secondary", width="stretch", help="Clears all uploaded files, quizzes, and chat history."):
            # Clear critical session state vars
            keys_to_clear = ['processed_files', 'vector_store', 'quiz_history', 'quiz_history_detailed', 'messages', 'selected_topic']
            for key in keys_to_clear:
                if key in st.session_state:
                    del st.session_state[key]
            
            # Re-init empty state
            st.session_state.processed_files = []
            st.session_state.vector_store = None
            st.session_state.quiz_history = []
            st.session_state.quiz_history_detailed = []
            st.session_state.messages = []
            st.session_state.selected_topic = "All Topics"
            
            st.success("App reset successfully!")
            st.rerun()

    else: # Webcam
        picture = st.camera_input("Take a picture of your notes")
        
        if picture:
            if st.button("Process Captured Image", type="primary", width="stretch"):
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                try:
                    status_text.text("📸 Processing image...")
                    # Save to temp
                    if not os.path.exists("temp"):
                        os.makedirs("temp")
                    
                    import time
                    path = os.path.join("temp", f"webcam_{int(time.time())}.jpg")
                    with open(path, "wb") as f:
                        f.write(picture.getbuffer())
                    
                    saved_paths = [path]
                    progress_bar.progress(30)
                    
                    # Ingest
                    status_text.text("📖 Extracting text from image...")
                    from src.ingest.ingestor import Ingestor
                    ingestor = Ingestor()
                    chunks = ingestor.ingest(saved_paths)
                    
                    progress_bar.progress(60)
                    
                    # Embed & Store
                    status_text.text("🧠 Generating Embeddings...")
                    from src.embed.indexer import VectorStore
                    
                    embedder = get_embedder()
                    texts = [c['text'] for c in chunks]
                    embeddings = embedder.embed_chunks(texts)
                    
                    progress_bar.progress(90)
                    
                    vector_store = VectorStore()
                    vector_store.add_embeddings(embeddings, chunks)
                    
                    st.session_state.vector_store = vector_store
                    if st.session_state.processed_files:
                        st.session_state.processed_files.extend(saved_paths)
                    else:
                        st.session_state.processed_files = saved_paths
                        
                    progress_bar.progress(100)
                    status_text.text("✅ Done!")
                    st.success("Successfully processed captured image!")
                    st.balloons()
                except Exception as e:
                    st.error(f"An error occurred: {e}")
        
    st.divider()
    if st.session_state.processed_files:
        st.markdown("### 📚 Indexed Documents")
        for f in st.session_state.processed_files:
            st.text(f"📄 {os.path.basename(f)}")

def render_study():
    st.header("💬 AI Study Companion")
    user_query = None
    
    if not st.session_state.vector_store:
        st.warning("Please upload and process documents in the Home tab first.")
        return

    # Layout: Sidebar for Topics/Controls, Main for Chat
    col_controls, col_chat = st.columns([1, 3])
    
    with col_controls:
        st.subheader("📚 Study Material")
        
        # Extract unique topics
        all_topics = sorted(list(set([m['metadata']['topic'] for m in st.session_state.vector_store.metadata if 'topic' in m.get('metadata', {})])))
        if not all_topics:
            all_topics = ["General"]
            
        # Robo Button (Chat with Full Doc)
        if st.button("🤖 Chat with Full Doc", type="primary", width="stretch"):
            st.session_state.selected_topic = "All Topics"
            
        st.divider()
        
        # Collapsible Chapter List
        with st.expander("📖 Chapters / Topics", expanded=True):
            for topic in all_topics:
                if st.button(f"{topic}", key=f"btn_{topic}", width="stretch"):
                    st.session_state.selected_topic = topic
                
        # Current Selection Display
        if 'selected_topic' not in st.session_state:
            st.session_state.selected_topic = "All Topics"
            
        st.info(f"Current Scope: **{st.session_state.selected_topic}**")
        
        st.divider()
        
        # Summarizer
        st.subheader("📝 Summarizer")
        if st.button("Summarize Current Scope", width="stretch"):
            with st.spinner("Generating Summary..."):
                # Filter text by topic
                if st.session_state.selected_topic == "All Topics":
                    docs = st.session_state.vector_store.metadata
                else:
                    docs = [m for m in st.session_state.vector_store.metadata if m.get('metadata', {}).get('topic') == st.session_state.selected_topic]
                
                if docs:
                    all_text = " ".join([m['text'] for m in docs])
                    
                    @st.cache_resource
                    def get_summarizer():
                        from src.utils.summarizer import Summarizer
                        return Summarizer()
                        
                    summarizer = get_summarizer()
                    summary = summarizer.summarize(all_text[:5000])
                    st.session_state.current_summary = summary
                else:
                    st.warning("No content found for this topic.")

        if 'current_summary' in st.session_state:
            st.text_area("Summary Result", st.session_state.current_summary, height=200)

    with col_chat:
        # Header with Robot Icon
        st.markdown(f"### 🤖 EduBot: {st.session_state.selected_topic}")
        
        # --- Chat Interface ---
        if "messages" not in st.session_state:
            st.session_state.messages = []

        # Display chat messages with avatars
        for message in st.session_state.messages:
            avatar = "🤖" if message["role"] == "assistant" else "👤"
            with st.chat_message(message["role"], avatar=avatar):
                st.markdown(message["content"])

        # Chat Input Area
        col_mic, col_dummy = st.columns([0.5, 0.5])
        with col_mic:
            audio_value = st.audio_input("🎤", label_visibility="collapsed") if hasattr(st, 'audio_input') else None
        
        if audio_value:
            # Save audio to temp file
            if not os.path.exists("temp"):
                os.makedirs("temp")
            
            import time
            audio_path = os.path.join("temp", f"voice_input_{int(time.time())}.wav")
            with open(audio_path, "wb") as f:
                f.write(audio_value.getbuffer())
            
            # Transcribe
            from src.utils.speech import SpeechTranscriber
            
            @st.cache_resource
            def get_transcriber():
                return SpeechTranscriber()
                
            transcriber = get_transcriber()
            transcription = transcriber.transcribe(audio_path)
            
            if transcription and not transcription.startswith("Error"):
                user_query = transcription
                st.success(f"🎤 Transcribed: {user_query}")
            
            # Cleanup temp file
            try:
                os.remove(audio_path)
            except:
                pass
        
        # Main Chat Input
        prompt_text = st.chat_input("Ask a question about your documents...")
        
        # Prioritize text input if available, else check if mic provided input
        if prompt_text:
            user_query = prompt_text

        # Unified Processing
        if user_query:
            # Add user message to history
            st.session_state.messages.append({"role": "user", "content": user_query})
            with st.chat_message("user", avatar="👤"):
                st.markdown(user_query)

            # Generate response
            with st.chat_message("assistant", avatar="🤖"):
                with st.spinner("Thinking..."):
                    # Cache the heavy models
                    @st.cache_resource
                    def get_models_v3(): 
                        from src.embed.embedder import Embedder
                        from src.rag.generator import Generator
                        return Embedder(), Generator()

                    embedder, generator = get_models_v3()
                    
                    from src.rag.retriever import Retriever
                    retriever = Retriever(embedder, st.session_state.vector_store)
                    
                    # Retrieve context
                    context = retriever.retrieve(user_query)
                    
                    # Debug: Check if context is retrieved
                    if not context:
                        st.warning("⚠️ No relevant context found in documents.")
                        context = [{"text": "No context found."}]
                    else:
                        st.caption(f"🔍 Found {len(context)} relevant chunks.")

                    # Generate response with streaming
                    stream = generator.generate_answer(user_query, context, stream=True)
                    response = st.write_stream(stream)
            
            # Save assistant response to history
            st.session_state.messages.append({"role": "assistant", "content": response})

def render_quiz():
    st.header("🧠 Knowledge Check")
    if not st.session_state.vector_store:
        st.warning("Please upload documents first.")
        return

    # --- Topic Selection ---
    all_topics = sorted(list(set([m['metadata']['topic'] for m in st.session_state.vector_store.metadata if 'topic' in m.get('metadata', {})])))
    if not all_topics:
        all_topics = ["General"]
    
    selected_topic = st.selectbox("Generate Quiz for:", ["All Topics"] + all_topics, key="quiz_topic")

    if st.button("Generate New Quiz", type="primary"):
        with st.spinner("Generating quiz questions..."):
            # Filter docs
            if selected_topic == "All Topics":
                docs = st.session_state.vector_store.metadata
            else:
                docs = [m for m in st.session_state.vector_store.metadata if m.get('metadata', {}).get('topic') == selected_topic]
            
            if not docs:
                st.error("No content found for this topic.")
            else:
                from src.utils.quiz_generator import QuizGenerator
                qg = QuizGenerator()
                st.session_state.current_quiz = qg.generate_mcq(docs, num_questions=5)
                st.session_state.quiz_answers = {}
                st.session_state.quiz_submitted = False

    if 'current_quiz' in st.session_state:
        if not st.session_state.current_quiz:
            st.warning("Could not generate quiz. Documents might be too short or lack sufficient content.")
            return

        if st.session_state.get('quiz_submitted', False):
            # --- Results View (Read-Only) ---
            st.success("Quiz Submitted!")
            results = st.session_state.get('last_quiz_results', {})
            if results:
                st.markdown(f"### 🏁 Final Score: {results['score']}/{results['total']} ({results['percentage']:.1f}%)")
                if results['score'] > 3:
                    st.balloons()
                
                st.divider()
                for i, q in enumerate(st.session_state.current_quiz):
                    user_ans = st.session_state.quiz_answers.get(i)
                    correct_ans = q['answer']
                    is_correct = user_ans == correct_ans
                    
                    st.markdown(f"**Q{i+1}: {q['question']}**")
                    if is_correct:
                        st.success(f"Your Answer: {user_ans} ✅")
                    else:
                        st.error(f"Your Answer: {user_ans} ❌")
                        st.markdown(f"**Correct Answer:** {correct_ans}")
                    
                    if 'source' in q:
                        st.caption(f"Source: {q['source']}")
                    st.divider()
            
            if st.button("Start New Quiz", type="primary"):
                del st.session_state.current_quiz
                st.session_state.quiz_submitted = False
                st.rerun()

        else:
            # --- Active Quiz Form ---
            with st.form("quiz_form"):
                score = 0
                for i, q in enumerate(st.session_state.current_quiz):
                    st.markdown(f"**Q{i+1}: {q['question']}**")
                    if 'source' in q:
                        st.caption(f"Source: {q['source']}")
                        
                    user_choice = st.radio(f"Select answer for Q{i+1}:", q['options'], key=f"q_{i}")
                    st.session_state.quiz_answers[i] = user_choice
                    st.divider()
                
                submitted = st.form_submit_button("Submit Quiz", type="primary")
                
                if submitted:
                    for i, q in enumerate(st.session_state.current_quiz):
                        user_choice = st.session_state.quiz_answers.get(i)
                        correct_choice = q['answer']
                        
                        is_correct = False
                        if user_choice == correct_choice:
                            score += 1
                            is_correct = True
                        else:
                            is_correct = False
                        
                        st.session_state.quiz_history_detailed.append({
                            "question": q['question'],
                            "is_correct": is_correct,
                            "source": q.get('source', 'Unknown'),
                            "topic": selected_topic,
                            "timestamp": pd.Timestamp.now()
                        })
                    
                    # Store percentage
                    percentage = (score / len(st.session_state.current_quiz)) * 100
                    st.session_state.quiz_history.append(percentage)
                    
                    # Save results state
                    st.session_state.last_quiz_results = {
                        "score": score,
                        "total": len(st.session_state.current_quiz),
                        "percentage": percentage
                    }
                    st.session_state.quiz_submitted = True
                    st.rerun()

def render_progress():
    st.header("📈 Learning Progress")
    
    if not st.session_state.quiz_history:
        st.info("Take some quizzes to see your progress!")
        return
        
    # Analytics
    from src.utils.analytics import AnalyticsEngine
    import plotly.express as px
    
    data = st.session_state.quiz_history
    df = pd.DataFrame(data, columns=["Score"])
    df['Attempt'] = range(1, len(df) + 1)
    
    # Forecast
    forecast = AnalyticsEngine.forecast_next_score(data)
    
    # Metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("Average Score", f"{np.mean(data):.1f}%", delta=f"{data[-1] - np.mean(data):.1f}%" if len(data) > 1 else None)
    col2.metric("Highest Score", f"{np.max(data)}%")
    col3.metric("Predicted Next", f"{forecast['predicted_score']:.1f}%" if forecast['predicted_score'] else "N/A", delta=forecast['trend'])
    
    # Charts
    st.subheader("Performance Trend")
    fig = px.line(df, x='Attempt', y='Score', title='Quiz Scores Over Time', markers=True)
    fig.add_hline(y=70, line_dash="dash", line_color="green", annotation_text="Passing Score (70%)")
    st.plotly_chart(fig, width="stretch", key="progress_chart")

    # --- Advanced Analytics ---
    st.divider()
    st.subheader("🧠 Deep Dive Analytics")
    
    # Calculate Metrics
    weak_areas = AnalyticsEngine.analyze_weak_areas(st.session_state.quiz_history_detailed)
    learning_metrics = AnalyticsEngine.calculate_learning_metrics(forecast.get('slope', 0), np.mean(data))
    
    # Multi-Subject Analytics (New)
    st.markdown("### 📚 Subject-wise Performance")
    if st.session_state.quiz_history_detailed:
        df_detailed = pd.DataFrame(st.session_state.quiz_history_detailed)
        if 'topic' in df_detailed.columns:
            topic_perf = df_detailed.groupby('topic')['is_correct'].mean() * 100
            topic_perf = topic_perf.reset_index(name='Score')
            
            fig_topic = px.bar(
                topic_perf, 
                x='topic', 
                y='Score', 
                title='Average Score by Subject',
                color='Score',
                color_continuous_scale='RdYlGn',
                range_color=[0, 100],
                text_auto='.1f'
            )
            fig_topic.update_layout(
                xaxis_title="Subject", 
                yaxis_title="Average Score (%)",
                yaxis=dict(
                    range=[0, 100],
                    tickmode='array',
                    tickvals=[0, 20, 40, 60, 80, 100]
                ),
                coloraxis_colorbar=dict(
                    title="Score Meter"
                )
            )
            st.plotly_chart(fig_topic, width="stretch", key="topic_chart")
        else:
            st.info("Not enough detailed data for subject analysis yet.")
    
    st.divider()
    
    # Download Section
    col_d1, col_d2 = st.columns(2)

    with col_d1:
        st.subheader("📄 Progress Report")
        if st.button("Generate PDF Report"):
            from src.utils.reporter import generate_pdf_report
            # Prepare analytics dict
            analytics_data = {
                "average": f"{np.mean(data):.2f}",
                "predicted_score": f"{forecast['predicted_score']}" if forecast['predicted_score'] is not None else "N/A",
                "trend": forecast['trend'],
                "weak_areas": weak_areas,
                "learning_metrics": learning_metrics
            }
            
            # Use session state info or defaults
            user = st.session_state.user
            s_name = f"{user.get('first_name', '')} {user.get('last_name', '')}"
            s_prof = user.get('profession', 'N/A')
            
            pdf_bytes = generate_pdf_report(s_name, s_prof, st.session_state.quiz_history, analytics_data)
            st.download_button(
                label="⬇️ Download Report",
                data=pdf_bytes,
                file_name="progress_report.pdf",
                mime="application/pdf"
            )

    with col_d2:
        # Certificate
        st.subheader("🎓 Course Certificate")
        
        # Check strict eligibility: >70% in ALL topics
        all_passed = False
        failed_topics = []
        
        if st.session_state.quiz_history_detailed:
            df_det = pd.DataFrame(st.session_state.quiz_history_detailed)
            if 'topic' in df_det.columns:
                # Get list of all available topics from vector store
                all_available_topics = set([m['metadata']['topic'] for m in st.session_state.vector_store.metadata if 'topic' in m.get('metadata', {})])
                if not all_available_topics:
                    all_available_topics = {"General"}
                
                # Calculate score per topic
                topic_scores = df_det.groupby('topic')['is_correct'].mean() * 100
                
                # Check each available topic
                for topic in all_available_topics:
                    if topic not in topic_scores.index:
                        failed_topics.append(f"{topic} (Not attempted)")
                    elif topic_scores[topic] < 70:
                        failed_topics.append(f"{topic} ({topic_scores[topic]:.1f}%)")
                
                if not failed_topics:
                    all_passed = True
            else:
                failed_topics.append("No detailed quiz data available.")
        else:
            failed_topics.append("No quizzes taken.")

        if all_passed:
            st.success("🎉 Congratulations! You have passed all topics.")
            if st.button("🏆 Generate Certificate"):
                from src.utils.reporter import generate_certificate
                user = st.session_state.user
                s_name = f"{user.get('first_name', '')} {user.get('last_name', '')}"
                
                # Use document name if available, else generic
                doc_name = "Comprehensive Assessment"
                if st.session_state.processed_files:
                     doc_name = ", ".join(st.session_state.processed_files[:2])
                     if len(st.session_state.processed_files) > 2:
                         doc_name += "..."

                cert_bytes = generate_certificate(s_name, document_name=doc_name)
                
                st.download_button(
                    label="⬇️ Download Certificate",
                    data=cert_bytes,
                    file_name="certificate.pdf",
                    mime="application/pdf"
                )
        else:
            st.warning("🔒 Certificate Locked")
            st.caption("You must score at least 70% in ALL topics to unlock.")
            st.error(f"Pending Requirements:\n" + "\n".join([f"- {t}" for t in failed_topics]))


            st.caption("Keep learning to unlock your certificate!")

if __name__ == "__main__":
    main()
