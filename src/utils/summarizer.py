from transformers import pipeline

class Summarizer:
    def __init__(self, model_name: str = "MBZUAI/LaMini-Flan-T5-248M"):
        self.model_name = model_name
        self.pipe = None
        self._load_model()

    def _load_model(self):
        try:
            print(f"Loading summarization model {self.model_name}...")
            self.pipe = pipeline("summarization", model=self.model_name, max_length=512)
            print(f"Model {self.model_name} loaded.")
        except Exception as e:
            print(f"Failed to load model: {e}")
            self.pipe = None

    def summarize(self, text: str, sentences_count: int = 5) -> str:
        """
        Generates an abstractive summary using LLM.
        """
        if self.pipe:
            # Chunking strategy to handle long documents
            # Local LLM window is usually 512 tokens (~2000 chars), we play safe with 1024 chars chunks
            max_chunk_size = 1024
            chunks = [text[i:i+max_chunk_size] for i in range(0, len(text), max_chunk_size)]
            
            summaries = []
            for chunk in chunks:
                try:
                    # Truncation=True allows the model to handle slight overflows gracefully
                    output = self.pipe(chunk, max_length=150, min_length=30, do_sample=False, truncation=True)
                    summaries.append(output[0]['summary_text'])
                except Exception as e:
                    print(f"Error summarizing chunk: {e}")
                    continue
            
            final_summary = " ".join(summaries)
            return final_summary
        else:
            return "Summarization model not loaded."
