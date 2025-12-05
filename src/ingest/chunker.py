from typing import List, Dict, Any

def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
    """
    Splits text into chunks of `chunk_size` characters with `overlap`.
    """
    if not text:
        return []
    
    chunks = []
    start = 0
    text_len = len(text)

    while start < text_len:
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        
        # Move start forward by chunk_size - overlap
        # If we are at the end, break
        if end >= text_len:
            break
            
        start += (chunk_size - overlap)
        
    return chunks

def process_file_content(file_name: str, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[Dict[str, Any]]:
    """
    Chunks text and returns a list of chunk objects with metadata.
    """
    raw_chunks = chunk_text(text, chunk_size, overlap)
    chunks_with_metadata = []
    
    for i, chunk in enumerate(raw_chunks):
        chunks_with_metadata.append({
            "id": f"{file_name}_{i}",
            "text": chunk,
            "metadata": {
                "source": file_name,
                "chunk_index": i
            }
        })
        
    return chunks_with_metadata
