import os
from transformers import pipeline
import torch

class SpeechTranscriber:
    def __init__(self, model_name: str = "openai/whisper-tiny"):
        self.model_name = model_name
        self.pipe = None
        self._load_model()

    def _load_model(self):
        try:
            print(f"Loading speech model {self.model_name}...")
            # Check if GPU is available
            device = "cuda:0" if torch.cuda.is_available() else "cpu"
            self.pipe = pipeline(
                "automatic-speech-recognition", 
                model=self.model_name, 
                device=device
            )
            print(f"Speech model {self.model_name} loaded on {device}.")
        except Exception as e:
            print(f"Failed to load speech model: {e}")
            self.pipe = None

    def transcribe(self, audio_path: str) -> str:
        """
        Transcribes audio file to text using local Whisper model.
        """
        if not self.pipe:
            return "Error: Speech model not loaded."
            
        try:
            # Whisper pipeline handles loading and processing
            result = self.pipe(audio_path)
            return result['text']
        except Exception as e:
            print(f"Transcription error: {e}")
            return f"Error transcribing audio: {e}"
