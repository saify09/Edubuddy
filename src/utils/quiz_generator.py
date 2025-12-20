import random
import re
from typing import List, Dict

class QuizGenerator:
    def __init__(self, generator):
        self.generator = generator

    def generate_mcq(self, documents: List[Dict], num_questions: int = 5) -> List[Dict]:
        """
        Generates MCQs using the LLM with fallback to simple Cloze generation.
        """
        if not documents:
            return []

        # Filter and select docs
        valid_docs = [d for d in documents if len(d['text']) > 100]
        if not valid_docs:
            valid_docs = documents

        selected_docs = random.sample(valid_docs, min(num_questions, len(valid_docs)))
        
        quiz = []
        for doc in selected_docs:
            text = doc['text'][:500] # Limit context
            source = doc.get('source', 'Unknown')
            
            # 1. Try LLM Generation
            try:
                prompt = (
                    "Create a multiple choice question (MCQ) from the context. "
                    "Format: Question: <question> Option A: <opt1> Option B: <opt2> Option C: <opt3> Answer: <opt_text>"
                )
                
                # Pass text as context so Generator formats it correctly
                context = [{'text': text}]
                response = self.generator.generate_answer(prompt, context, stream=False)
                
                # Regex Parsing (Handles both multiline and single line)
                # Look for Question: ... Option A: ...
                q_match = re.search(r"Question:\s*(.*?)\s*Option A:", response, re.IGNORECASE | re.DOTALL)
                opt_a_match = re.search(r"Option A:\s*(.*?)\s*Option B:", response, re.IGNORECASE | re.DOTALL)
                opt_b_match = re.search(r"Option B:\s*(.*?)\s*Option C:", response, re.IGNORECASE | re.DOTALL)
                # Option C might be followed by Answer or End
                opt_c_match = re.search(r"Option C:\s*(.*?)\s*(Answer:|$)", response, re.IGNORECASE | re.DOTALL)
                ans_match = re.search(r"Answer:\s*(.*)", response, re.IGNORECASE | re.DOTALL)
                
                if q_match and opt_a_match and opt_b_match and opt_c_match:
                    question = q_match.group(1).strip()
                    options = [
                        opt_a_match.group(1).strip(),
                        opt_b_match.group(1).strip(),
                        opt_c_match.group(1).strip()
                    ]
                    answer = ans_match.group(1).strip() if ans_match else options[0] # Default to first if missing
                    
                    # Clean answer if it says "Option A"
                    if "Option A" in answer: answer = options[0]
                    elif "Option B" in answer: answer = options[1]
                    elif "Option C" in answer: answer = options[2]
                    
                    # Ensure answer is in options
                    if answer not in options:
                        options.append(answer)
                        random.shuffle(options)
                    
                    quiz.append({
                        "question": question,
                        "options": options,
                        "answer": answer,
                        "source": source
                    })
                    continue # Success, move to next doc

            except Exception as e:
                print(f"LLM Quiz Gen failed: {e}")
                # Fallback to logic below

            # 2. Fallback: Simple Cloze (Fill-in-the-blank)
            # Pick a sentence and blank out a word
            sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', text)
            suitable = [s for s in sentences if 30 < len(s) < 200]
            if suitable:
                sentence = random.choice(suitable)
                words = [w for w in sentence.split() if w.isalpha() and len(w) > 4]
                if words:
                    target_word = random.choice(words)
                    question_text = sentence.replace(target_word, "______")
                    
                    # Fake options from text
                    all_words = [w for w in text.split() if w.isalpha() and len(w) > 4 and w != target_word]
                    distractors = random.sample(all_words, 3) if len(all_words) >= 3 else ["Option A", "Option B", "Option C"]
                    opts = distractors + [target_word]
                    random.shuffle(opts)
                    
                    quiz.append({
                        "question": question_text,
                        "options": opts,
                        "answer": target_word,
                        "source": source
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
