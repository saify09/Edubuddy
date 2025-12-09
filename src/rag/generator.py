import os
from transformers import pipeline, TextIteratorStreamer
from threading import Thread

class Generator:
    def __init__(self, model_name: str = "MBZUAI/LaMini-Flan-T5-248M"):
        self.model_name = model_name
        self.pipe = None
        self._load_model()

    def _load_model(self):
        """
        Loads the local LLM using Transformers pipeline.
        """
        try:
            print(f"Loading model {self.model_name}...")
            # Use text2text-generation for T5 models
            self.pipe = pipeline("text2text-generation", model=self.model_name, max_length=512)
            print(f"Model {self.model_name} loaded successfully.")
        except Exception as e:
            print(f"Failed to load model: {e}")
            self.pipe = None

    def generate_answer(self, query: str, context_chunks: list, stream: bool = False):
        """
        Generates an answer based on the query and retrieved context.
        If stream=True, returns a generator yielding tokens.
        """
        context_text = "\n\n".join([c['text'] for c in context_chunks])
        
        if self.pipe:
            # Truncate context to ~500 chars to fit within 512 tokens (leaving space for query)
            if len(context_text) > 500:
                context_text = context_text[:500] + "...(truncated)"
            
            # Prompt engineering for T5
            prompt = f"Answer the following question based on the context below:\n\nContext:\n{context_text}\n\nQuestion: {query}\n\nAnswer:"
            
            if stream:
                # Enable truncation to be safe, though manual truncation above should handle most cases
                generation_kwargs = dict(max_length=256, do_sample=False, streamer=streamer)
                
                thread = Thread(target=self._run_pipeline, args=(prompt, generation_kwargs))
                thread.start()
                
                return streamer
            else:
                output = self.pipe(prompt, max_length=256, do_sample=False, truncation=True)
                return output[0]['generated_text']
        else:
            if stream:
                # Mock streamer for error case
                def mock_stream():
                    yield "**LLM not loaded.**\n\nContext:\n"
                    yield context_text
                return mock_stream()
            return f"**LLM not loaded.**\n\nContext:\n{context_text}"

    def _run_pipeline(self, prompt, generation_kwargs):
        """Helper to run pipeline in thread with error catching."""
        streamer = generation_kwargs.get("streamer")
        try:
            # Pass prompt as 'text_inputs' or positional
            # For text2text-generation, the argument is usually just the input string or list
            self.pipe(prompt, **generation_kwargs)
        except Exception as e:
            print(f"ERROR: Pipeline generation failed: {e}")
            # If we have the streamer, send an error message so the UI sees it
            if streamer:
                streamer.put("**Error during generation.**")
        finally:
            # CRITICAL: Always end the streamer to prevent UI from hanging
            if streamer:
                streamer.end()
