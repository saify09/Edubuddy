import matplotlib.pyplot as plt
import os
from fpdf import FPDF
import tempfile
import pandas as pd

def generate_pdf_report(student_name: str, profession: str, quiz_history: list, analytics: dict = None) -> bytes:
    """
    Generates a PDF report and returns the bytes.
    """
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", 'B', 16)
    pdf.cell(0, 10, "EduBuddy Progress Report", ln=True, align='C')
    
    # Helper to sanitize text for Latin-1 (removes emojis/special chars)
    def sanitize(text):
        # Replace specific emojis with text equivalents first
        text = str(text).replace("🚀", " (Rising)").replace("📉", " (Dropping)").replace("⚖️", " (Stable)")
        return text.encode('latin-1', 'replace').decode('latin-1')

    pdf.set_font("Helvetica", size=12)
    pdf.ln(10)
    pdf.cell(0, 10, f"Student Name: {sanitize(student_name)}", ln=True)
    pdf.cell(0, 10, f"Profession: {sanitize(profession)}", ln=True)
    pdf.ln(10)
    
    # Analytics Section
    if analytics:
        pdf.set_font("Helvetica", 'B', 14)
        pdf.cell(0, 10, "Performance Analytics", ln=True)
        pdf.set_font("Helvetica", size=12)
        pdf.cell(0, 10, f"Average Score: {sanitize(analytics.get('average', 'N/A'))}", ln=True)
        pdf.cell(0, 10, f"Predicted Next Score: {sanitize(analytics.get('predicted_score', 'N/A'))}", ln=True)
        pdf.cell(0, 10, f"Trend: {sanitize(analytics.get('trend', 'N/A'))}", ln=True)
        
        # Advanced Analytics
        if 'learning_metrics' in analytics:
            lm = analytics['learning_metrics']
            pdf.ln(5)
            pdf.set_font("Helvetica", 'B', 13)
            pdf.cell(0, 10, "Learning Insights", ln=True)
            pdf.set_font("Helvetica", size=12)
            pdf.cell(0, 10, f"Learning Speed: {sanitize(lm.get('learning_speed', 'N/A'))}", ln=True)
            pdf.cell(0, 10, f"Time to Mastery: {sanitize(lm.get('time_to_mastery', 'N/A'))}", ln=True)
            
        if 'weak_areas' in analytics and analytics['weak_areas']:
            pdf.ln(5)
            pdf.set_font("Helvetica", 'B', 13)
            pdf.cell(0, 10, "Recommended Revision Topics", ln=True)
            pdf.set_font("Helvetica", size=12)
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
            
    # Return as bytes using temp file to ensure validity
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.close() # Close handle for Windows compatibility
        pdf.output(tmp.name)
        tmp_path = tmp.name
        
    with open(tmp_path, "rb") as f:
        pdf_bytes = f.read()
        
    os.remove(tmp_path)
    return pdf_bytes

def generate_certificate(student_name: str, course_name: str = "AI-Powered Learning with EduBuddy", date: str = None, document_name: str = None) -> bytes:
    """
    Generates a professional PDF certificate.
    """
    if not date:
        date = pd.Timestamp.now().strftime("%B %d, %Y")
        
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    
    # Border
    pdf.set_line_width(3)
    pdf.set_draw_color(11, 61, 145) # Deep Blue
    pdf.rect(10, 10, 277, 190)
    
    # Inner Border
    pdf.set_line_width(1)
    pdf.set_draw_color(255, 127, 14) # Orange
    pdf.rect(15, 15, 267, 180)
    
    # Header
    pdf.set_font("Helvetica", 'B', 36) # Reduced from 40
    pdf.set_text_color(11, 61, 145)
    pdf.ln(15) # Reduced from 20
    pdf.cell(0, 15, "Certificate of Completion", align='C', ln=True)
    
    # Subheader
    pdf.set_font("Helvetica", 'I', 14) # Reduced from 16
    pdf.set_text_color(100, 100, 100)
    pdf.ln(5) # Reduced from 10
    pdf.cell(0, 10, "This is to certify that", align='C', ln=True)
    
    # Student Name
    pdf.set_font("Helvetica", 'B', 28) # Reduced from 30
    pdf.set_text_color(0, 0, 0)
    pdf.ln(5) # Reduced from 10
    
    # Sanitize name
    def sanitize(text):
        return str(text).encode('latin-1', 'replace').decode('latin-1')
        
    pdf.cell(0, 15, sanitize(student_name), align='C', ln=True)
    
    # Body
    pdf.set_font("Helvetica", '', 14) # Reduced from 16
    pdf.set_text_color(100, 100, 100)
    pdf.ln(5) # Reduced from 10
    pdf.cell(0, 10, "has successfully completed the course", align='C', ln=True)
    
    # Course Name
    pdf.set_font("Helvetica", 'B', 22) # Reduced from 24
    pdf.set_text_color(11, 61, 145)
    pdf.ln(5)
    pdf.cell(0, 15, sanitize(course_name), align='C', ln=True)
    
    # Document Name (New)
    if document_name:
        pdf.set_font("Helvetica", 'I', 12) # Reduced from 14
        pdf.set_text_color(80, 80, 80)
        pdf.ln(2)
        
        # Truncate if too long
        doc_text = sanitize(document_name)
        if len(doc_text) > 60:
            doc_text = doc_text[:57] + "..."
            
        pdf.cell(0, 10, f"Studied: {doc_text}", align='C', ln=True)
    
    # Date
    pdf.set_font("Helvetica", '', 12) # Reduced from 14
    pdf.set_text_color(100, 100, 100)
    pdf.ln(5) # Reduced from 10 to fix large gap
    pdf.cell(0, 10, f"Date: {date}", align='C', ln=True)
    
    # Signature
    pdf.ln(10) # Reduced from 15
    pdf.set_draw_color(0, 0, 0)
    
    # Draw line relative to current Y
    y = pdf.get_y()
    pdf.line(110, y, 190, y)
    
    pdf.ln(2) # Small gap between line and text
    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 5, "EduBuddy AI Instructor", align='C', ln=True)
    
    # Return as bytes using temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.close() # Close handle for Windows compatibility
        pdf.output(tmp.name)
        tmp_path = tmp.name
        
    with open(tmp_path, "rb") as f:
        cert_bytes = f.read()
        
    os.remove(tmp_path)
    return cert_bytes
