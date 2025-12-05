import re
from typing import List, Dict, Tuple

class TopicExtractor:
    def __init__(self):
        # Regex patterns for common header formats
        self.header_patterns = [
            r'^Chapter\s+\d+.*$',           # Chapter 1: Introduction
            r'^\d+\.\s+[A-Z][a-zA-Z\s]+$',  # 1. Introduction
            # r'^[A-Z][A-Z\s]{5,}$',          # REMOVED: INTRODUCTION (Too many false positives like AAPL JNJ)
            r'^(Introduction|Preliminaries|Appendix|Index|Glossary|Bibliography|References)$', # Specific common headers
            r'^Table of Contents$',         # TOC
            r'^Contents$',                  # TOC variant
            r'^Module\s+\d+.*$',            # Module 1
            r'^Unit\s+\d+.*$',              # Unit 1
            r'^Section\s+\d+.*$',           # Section 1
            r'^Topic\s+\d+.*$'              # Topic 1
        ]

    def extract_segments(self, text: str) -> List[Dict[str, str]]:
        """
        Splits text into segments based on detected topics/chapters.
        Returns: List of {'topic': 'Topic Name', 'content': '...'}
        """
        # 1. Try to extract headers from TOC first
        toc_headers = self._extract_toc_headers(text)
        
        if toc_headers:
            # Use specific TOC headers for splitting
            raw_segments = self._split_by_specific_headers(text, toc_headers)
        else:
            # Fallback to generic patterns
            raw_segments = self._split_by_headers(text)
        
        if len(raw_segments) <= 1:
            return [] 
            
        # Post-processing: Merge small segments
        # If we used TOC headers, we trust them more, so we skip aggressive merging
        # unless the content is extremely empty.
        merge_threshold = 0 if toc_headers else 300
        
        merged_segments = []
        current_seg = raw_segments[0]
        
        for next_seg in raw_segments[1:]:
            # If current segment is too short (likely a false positive header or just intro text), merge it
            if len(current_seg['content']) < merge_threshold:
                if merged_segments:
                    merged_segments[-1]['content'] += "\n" + current_seg['topic'] + "\n" + current_seg['content']
                    current_seg = next_seg
                else:
                    next_seg['content'] = current_seg['topic'] + "\n" + current_seg['content'] + "\n" + next_seg['content']
                    current_seg = next_seg
            else:
                merged_segments.append(current_seg)
                current_seg = next_seg
                
        merged_segments.append(current_seg)
        return merged_segments

    def _extract_toc_headers(self, text: str) -> List[str]:
        """Scans text for a Table of Contents and extracts chapter titles."""
        lines = text.split('\n')
        toc_headers = []
        in_toc = False
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line: continue
            
            # Detect TOC start
            if re.match(r'^(Table of Contents|Contents|Index)$', line, re.IGNORECASE):
                in_toc = True
                continue
            
            if in_toc:
                # Stop if we hit a long block of text or end of likely TOC
                # Stop if we hit end of likely TOC (e.g. very long line that is NOT a TOC entry)
                # We won't use hard length limit anymore, but we check if it matches TOC pattern.
                if len(line) > 300: # Increase limit significantly just in case
                    in_toc = False
                    continue # Don't break, just stop current TOC block. Allows finding real TOC later if first was false positive.
                
                # Heuristic: TOC entries often end with a number (page num) or look like "1. Title"
                # Match "1. Title ... 5" or "Chapter 1: Title"
                # We want to extract the "Title" part to use as a header later.
                
                # Regex for TOC line: (Number/Bullet) (Title) (Dots/Spaces) (PageNum)
                # Updated to handle spaced dots ". . . ." common in PDFs
                match = re.match(r'^(\d+\.?\s+|Chapter\s+\d+:?\s+|Module\s+\d+:?\s+)(.+?)(?:\s*(?:\. ?){2,}\s*|\s{2,})?(\d+)?$', line)
                if match:
                    # Construct the full header string to look for in body
                    # We might just use the title, but better to use the full prefix + title for uniqueness
                    prefix = match.group(1).strip()
                    title = match.group(2).strip()
                    full_header = f"{prefix} {title}"
                    # Clean up dots/page nums if they got into title
                    full_header = re.sub(r'[\.\s]{3,}.*$', '', full_header).strip()
                    toc_headers.append(full_header)
                
                # Stop scanning TOC if we have too many empty lines or weird content? 
                # For now, let's limit TOC scan to ~50 lines after start
                if len(toc_headers) > 30:
                    break
                    
        return toc_headers

    def _split_by_specific_headers(self, text: str, headers: List[str]) -> List[Dict[str, str]]:
        """Splits text using a specific list of known headers."""
        lines = text.split('\n')
        segments = []
        current_topic = "Introduction"
        current_content = []
        
        # Create a regex pattern that matches any of the known headers exactly
        escaped_headers = [re.escape(h) for h in headers]
        # Sort by length descending to match longest headers first
        escaped_headers.sort(key=len, reverse=True)
        pattern = r'^(' + '|'.join(escaped_headers) + r').*$'
        
        for line in lines:
            line = line.strip()
            if not line:
                current_content.append(line)
                continue
                
            # SKIP TOC lines (e.g. "1. Intro . . . . 5")
            # If the line ends with digits or has many dots, it's likely a TOC entry, not a chapter start
            if re.search(r'\.{3,}\s*\d+$', line) or re.search(r'\.{4,}', line):
                current_content.append(line)
                continue

            # Check if line matches one of our specific headers
            if re.match(pattern, line, re.IGNORECASE):
                # Extra sanity check: Line shouldn't be too long compared to header
                # (avoids matching "Chapter 1" inside a very long sentence starting with it)
                if len(line) > 100:
                    current_content.append(line)
                    continue

                 # Save previous segment
                if current_content:
                    segments.append({
                        'topic': current_topic,
                        'content': '\n'.join(current_content)
                    })
                
                # Start new segment
                current_topic = line
                current_content = []
            else:
                current_content.append(line)
        
        if current_content:
            segments.append({
                'topic': current_topic,
                'content': '\n'.join(current_content)
            })
            
        return segments

    def _split_by_headers(self, text: str) -> List[Dict[str, str]]:
        lines = text.split('\n')
        segments = []
        current_topic = "Introduction" 
        current_content = []
        
        for line in lines:
            line = line.strip()
            if not line:
                current_content.append(line)
                continue
                
            if self._is_header(line):
                # Save previous segment
                if current_content:
                    segments.append({
                        'topic': current_topic,
                        'content': '\n'.join(current_content)
                    })
                
                # Start new segment
                current_topic = line
                current_content = []
            else:
                current_content.append(line)
        
        if current_content:
            segments.append({
                'topic': current_topic,
                'content': '\n'.join(current_content)
            })
            
        return segments

    def _is_header(self, line: str) -> bool:
        if len(line) > 80: # Stricter length check
            return False
            
        # Must not end with punctuation like . or , (unless it's a number like 1.)
        if line[-1] in [',', ';', ':']:
            return False
            
        # Blacklist specific patterns (garbage headers)
        if '|' in line: # e.g. "10 | Chapter 1"
            return False
        if re.match(r'^\d+\s+[A-Za-z]+', line) and '.' not in line[:5]: # e.g. "1005 Gravenstein" - No dot after number
            return False
        if "Page" in line and len(line) < 15: # e.g. "Page 1"
            return False
            
        for pattern in self.header_patterns:
            if re.match(pattern, line, re.IGNORECASE): # Re-added IGNORECASE for words like "Introduction"
                return True
        return False
