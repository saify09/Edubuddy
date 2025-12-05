1.  **Clone the repository** (or extract the zip).
2.  **Create a virtual environment**:
    ```bash
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # Linux/Mac
    source venv/bin/activate
    ```
3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
4.  **Run the application**:
    ```bash
    streamlit run app.py
    ```

## Project Structure
- `app.py`: Main application entry point.
- `src/`: Core logic modules (ingestion, embedding, RAG).
- `ui/`: UI components.
- `data/`: Local data storage (indices, logs).
