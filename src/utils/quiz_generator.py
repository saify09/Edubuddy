import random
import re
from typing import List, Dict

class QuizGenerator:
    def __init__(self, generator=None):
        self.generator = generator

    def generate_mcq(self, documents: List[Dict], num_questions: int = 5) -> List[Dict]:
        """
        Generates MCQs using the LLM for deep context understanding.
        """
        if not documents:
            return []

        # Filter for substantial content
        valid_docs = [d for d in documents if len(d['text']) > 200]
        if not valid_docs:
            valid_docs = documents

        # Select distinct documents to avoid repetitive questions
        selected_docs = random.sample(valid_docs, min(num_questions, len(valid_docs)))
        
        quiz = []
        for doc in selected_docs:
            source = doc.get('source', 'Unknown')
            context_text = doc['text'][:1000] # Provide enough context
            
            # Prompt the LLM
            prompt = (
                f"You are a quiz master. Create a multiple-choice question based STRICTLY on the text below.\n"
                f"Text: {context_text}\n\n"
                f"Format your output exactly as:\n"
                f"Question: [Question text]\n"
                f"A) [Option A]\n"
                f"B) [Option B]\n"
                f"C) [Option C]\n"
                f"D) [Option D]\n"
                f"Answer: [Correct Option Letter]\n"
            )

            try:
                # Use the generator (greedy search for stability)
                if self.generator:
                    output = self.generator.pipe(prompt, max_length=256, do_sample=False, num_beams=1)[0]['generated_text']
                else:
                    break # Safety fallback
                
                # Parse the output
                 # Simple parsing logic (robustness can be improved)
                lines = output.split('\n')
                question = ""
                options = []
                answer = ""
                
                # Naive parsing (assumes LLM follows format closely, typically true for T5-Flan/LaMini)
                # If parsing fails, we skip this question
                # (For robust implementation, we might need regex)
                
                # Regex parsing attempt
                q_match = re.search(r"Question:\s*(.+)", output)
                a_match = re.search(r"A\)\s*(.+)", output)
                b_match = re.search(r"B\)\s*(.+)", output)
                c_match = re.search(r"C\)\s*(.+)", output)
                d_match = re.search(r"D\)\s*(.+)", output)
                ans_match = re.search(r"Answer:\s*([A-D])", output, re.IGNORECASE)

                if q_match and a_match and b_match and c_match and d_match and ans_match:
                    question_text = q_match.group(1).strip()
                    options_list = [
                        a_match.group(1).strip(),
                        b_match.group(1).strip(),
                        c_match.group(1).strip(),
                        d_match.group(1).strip()
                    ]
                    correct_letter = ans_match.group(1).upper()
                    correct_index = {'A': 0, 'B': 1, 'C': 2, 'D': 3}.get(correct_letter, 0)
                    correct_answer = options_list[correct_index]
                    
                    quiz.append({
                        "question": question_text,
                        "options": options_list,
                        "answer": correct_answer,
                        "source": source
                    })
            except Exception as e:
                print(f"Quiz Gen Error: {e}")
                continue
                
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
