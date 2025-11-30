import matplotlib.pyplot as plt
import os
from fpdf import FPDF
import tempfile

def generate_pdf_report(student_name: str, roll_no: str, quiz_history: list, analytics: dict = None) -> bytes:
    """
    Generates a PDF report and returns the bytes.
    """
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "EduBuddy Progress Report", ln=True, align='C')
    
    # Helper to sanitize text for Latin-1 (removes emojis/special chars)
    def sanitize(text):
        # Replace specific emojis with text equivalents first
        text = str(text).replace("🚀", " (Rising)").replace("📉", " (Dropping)").replace("⚖️", " (Stable)")
        return text.encode('latin-1', 'replace').decode('latin-1')

    pdf.set_font("Arial", size=12)
    pdf.ln(10)
    pdf.cell(0, 10, f"Student Name: {sanitize(student_name)}", ln=True)
    pdf.cell(0, 10, f"Roll Number: {sanitize(roll_no)}", ln=True)
    pdf.ln(10)
    
    # Analytics Section
    if analytics:
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, "Performance Analytics", ln=True)
        pdf.set_font("Arial", size=12)
        pdf.cell(0, 10, f"Average Score: {sanitize(analytics.get('average', 'N/A'))}", ln=True)
        pdf.cell(0, 10, f"Predicted Next Score: {sanitize(analytics.get('predicted_score', 'N/A'))}", ln=True)
        pdf.cell(0, 10, f"Trend: {sanitize(analytics.get('trend', 'N/A'))}", ln=True)
        
        # Advanced Analytics
        if 'learning_metrics' in analytics:
            lm = analytics['learning_metrics']
            pdf.ln(5)
            pdf.set_font("Arial", 'B', 13)
            pdf.cell(0, 10, "Learning Insights", ln=True)
            pdf.set_font("Arial", size=12)
            pdf.cell(0, 10, f"Learning Speed: {sanitize(lm.get('learning_speed', 'N/A'))}", ln=True)
            pdf.cell(0, 10, f"Time to Mastery: {sanitize(lm.get('time_to_mastery', 'N/A'))}", ln=True)
            
        if 'weak_areas' in analytics and analytics['weak_areas']:
            pdf.ln(5)
            pdf.set_font("Arial", 'B', 13)
            pdf.cell(0, 10, "Recommended Revision Topics", ln=True)
            pdf.set_font("Arial", size=12)
            for source, rate in analytics['weak_areas'].items():
                pdf.cell(0, 10, f"- {sanitize(source)} (Error Rate: {int(rate*100)}%)", ln=True)
        
        pdf.ln(10)
    
    # Chart Generation
    if quiz_history:
        try:
            plt.figure(figsize=(6, 4))
            # Use Bar Chart as requested
            attempts = range(1, len(quiz_history) + 1)
            plt.bar(attempts, quiz_history, color='#0b3d91', width=0.5, label='Score')
            
            # Overlay Trend Line (Both)
            plt.plot(attempts, quiz_history, color='#ff7f0e', marker='o', linestyle='-', linewidth=2, label='Trend')
            
            plt.title("Quiz Score Progression")
            plt.xlabel("Attempt")
            plt.ylabel("Score")
            plt.xticks(attempts) # Ensure integer ticks
            plt.legend()
            plt.grid(axis='y', linestyle='--', alpha=0.7)
            
            # Save to temp file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_file:
                plt.savefig(tmp_file.name, format='png')
                tmp_path = tmp_file.name
            
            plt.close()
            
            # Embed in PDF
            pdf.image(tmp_path, x=10, w=100)
            pdf.ln(5)
            
            # Cleanup
            os.remove(tmp_path)
        except Exception as e:
            print(f"Error generating chart: {e}")
            pdf.cell(0, 10, "Chart generation failed.", ln=True)

    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "Quiz Performance History", ln=True)
    pdf.set_font("Arial", size=12)
    
    if not quiz_history:
        pdf.cell(0, 10, "No quizzes taken yet.", ln=True)
    else:
        for i, score in enumerate(quiz_history):
            pdf.cell(0, 10, f"Quiz {i+1}: Score {score}", ln=True)
            
    # Return as bytes
    return pdf.output(dest='S').encode('latin-1')
