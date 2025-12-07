from sentence_transformers import SentenceTransformer
from typing import List
import numpy as np

class Embedder:
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        self.model = SentenceTransformer(model_name)

    def embed_text(self, text: str) -> np.ndarray:
        """
        Embeds a single string.
        """
        return self.model.encode([text])[0]

    def embed_chunks(self, chunks: List[str]) -> np.ndarray:
        """
        Embeds a list of strings.
        """
        return self.model.encode(chunks)
