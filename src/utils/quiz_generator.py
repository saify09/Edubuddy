import random
import re
from typing import List, Dict

class QuizGenerator:
    def __init__(self):
        pass

    def generate_mcq(self, documents: List[Dict], num_questions: int = 5) -> List[Dict]:
        """
        Generates MCQs from a list of document chunks (dicts with 'text' and 'source').
        Returns questions with 'source' metadata.
        """
        if not documents:
            return []

        # Filter chunks that are long enough
        valid_docs = [d for d in documents if len(d['text']) > 50]
        if not valid_docs:
            valid_docs = documents

        selected_docs = random.sample(valid_docs, min(num_questions, len(valid_docs)))
        
        quiz = []
        for doc in selected_docs:
            text = doc['text']
            source = doc.get('source', 'Unknown')
            
            sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', text)
            # Pick a suitable sentence
            suitable_sentences = [s for s in sentences if len(s) > 30 and len(s) < 300]
            if not suitable_sentences:
                continue
                
            sentence = random.choice(suitable_sentences)
            words = sentence.split()
            
            # Simple heuristic: pick a long word as the answer
            candidates = [w for w in words if len(w) > 5 and w.isalpha()]
            if not candidates:
                continue
                
            answer = random.choice(candidates)
            question_text = sentence.replace(answer, "______")
            
            # Generate distractors from ALL docs to ensure variety
            all_text = " ".join([d['text'] for d in documents])
            all_words = [w for w in all_text.split() if len(w) > 5 and w.isalpha() and w != answer]
            distractors = random.sample(all_words, 3) if len(all_words) >= 3 else ["Option A", "Option B", "Option C"]
            
            options = distractors + [answer]
            random.shuffle(options)
            
            quiz.append({
                "question": question_text,
                "options": options,
                "answer": answer,
                "source": source  # Track the source document
            })
            
        return quiz

    def generate_short_answer(self, text: str, num_questions: int = 5) -> List[Dict]:
        """
        Generates short answer questions (placeholder logic).
        """
        # For now, just return sentences as "Explain this..."
        sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', text)
        sentences = [s for s in sentences if len(s) > 60]
        
        if len(sentences) < num_questions:
            selected = sentences
        else:
            selected = random.sample(sentences, num_questions)
            
        quiz = []
        for s in selected:
            quiz.append({
                "question": f"Explain the context of: '{s[:30]}...'",
                "answer": s
            })
        return quiz
