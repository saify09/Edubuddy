from src.ingest.text_parser import parse_file
from src.ingest.chunker import process_file_content
from src.ingest.topic_extractor import TopicExtractor
from src.utils.analytics_logger import AnalyticsLogger
import os

class Ingestor:
    def __init__(self):
        self.topic_extractor = TopicExtractor()
        self.logger = AnalyticsLogger()

    def ingest(self, file_paths: list) -> list:
        all_chunks = []
        for file_path in file_paths:
            # 1. Parse Text
            text = parse_file(file_path)
            if not text:
                continue
                
            # 2. Extract Topics
            # Check file type for media
            ext = os.path.splitext(file_path)[1].lower()
            if ext in ['.png', '.jpg', '.jpeg', '.mp4', '.avi']:
                # Try to extract topic from OCR text first
                segments = self.topic_extractor.extract_segments(text)
                
                # If no segments found (or just General), fallback to filename logic
                if not segments or (len(segments) == 1 and segments[0]['topic'] == 'General'):
                    topic_name = os.path.basename(file_path)
                    
                    # Check for generic filenames
                    lower_name = topic_name.lower()
                    if any(x in lower_name for x in ['screenshot', 'whatsapp', 'untitled', 'image', 'video', 'capture']):
                        topic_name = "Uncategorized Media"
                        
                    segments = [{'topic': topic_name, 'content': text}]
            else:
                segments = self.topic_extractor.extract_segments(text)
                if not segments:
                    # Fallback to filename if no segments found
                    topic_name = os.path.basename(file_path)
                    segments = [{'topic': topic_name, 'content': text}]
            
            # 3. Chunk per Topic
            for segment in segments:
                topic = segment['topic']
                content = segment['content']
                
                # Chunk the segment content
                chunks = process_file_content(file_path, content)
                
                # Add topic to metadata
                for chunk in chunks:
                    if 'metadata' not in chunk:
                        chunk['metadata'] = {}
                    chunk['metadata']['topic'] = topic
                    
                all_chunks.extend(chunks)
            
            # Log success
            try:
                file_size = os.path.getsize(file_path)
                self.logger.log_ingestion(os.path.basename(file_path), file_size, "success")
            except:
                pass
                
        return all_chunks
