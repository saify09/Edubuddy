import random
import re
from typing import List, Dict

class QuizGenerator:
    def __init__(self, generator):
        self.generator = generator

    def generate_mcq(self, documents: List[Dict], num_questions: int = 5) -> List[Dict]:
        """
        Generates MCQs using the LLM.
        """
        if not documents:
            return []

        # Filter chunks that are long enough
        valid_docs = [d for d in documents if len(d['text']) > 100]
        if not valid_docs:
            valid_docs = documents

        # Select random docs to generate questions from
        selected_docs = random.sample(valid_docs, min(num_questions, len(valid_docs)))
        
        quiz = []
        for doc in selected_docs:
            text = doc['text'][:500] # Limit context for speed
            source = doc.get('source', 'Unknown')
            
            prompt = (
                f"Generate a multiple choice question based on this text: \"{text}\"\n"
                "Format:\n"
                "Question: [Question text]\n"
                "Option A: [Option 1]\n"
                "Option B: [Option 2]\n"
                "Option C: [Option 3]\n"
                "Answer: [Correct Option Text]"
            )
            
            try:
                # Use the generator to get raw text
                # We reuse generate_answer method but treat prompt as the query
                response = self.generator.generate_answer(prompt, [], stream=False)
                
                # Parse response
                lines = response.split('\n')
                question = ""
                options = []
                answer = ""
                
                for line in lines:
                    line = line.strip()
                    if line.startswith("Question:"):
                        question = line.replace("Question:", "").strip()
                    elif line.startswith("Option"):
                        options.append(line.split(":", 1)[1].strip())
                    elif line.startswith("Answer:"):
                        answer = line.replace("Answer:", "").strip()
                
                # If parsing failed or incomplete, skip
                if not question or len(options) < 2 or not answer:
                    continue
                    
                # Ensure answer is in options, if not (LLM hallucination), pick one or skip
                # Simple Cleanup: If answer is "Option A", map it to the index
                
                final_options = options[:4] # Max 4 options
                
                quiz.append({
                    "question": question,
                    "options": final_options,
                    "answer": answer,
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
