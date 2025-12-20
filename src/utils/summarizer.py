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

    def summarize(self, text: str, sentences_count: int = 5, topic: str = None) -> str:
        """
        Generates an abstractive summary using LLM.
        """
        if self.pipe:
            # Chunk text if too long
            if len(text) > 1500:
                text = text[:1500]
            
            if topic and topic != "All Topics":
                # Inject topic focus into the input text for T5
                input_text = f"Summarize this text focusing on {topic}: {text}"
            else:
                input_text = text
            
            output = self.pipe(input_text, max_length=256, min_length=50, do_sample=False)
            return output[0]['summary_text']
        else:
            return "Summarization model not loaded."
