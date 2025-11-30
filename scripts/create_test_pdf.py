from fpdf import FPDF

pdf = FPDF()
pdf.add_page()
pdf.set_font("Arial", size=12)
pdf.cell(200, 10, txt="Introduction to AI", ln=1, align="C")
pdf.cell(200, 10, txt="Artificial Intelligence is the simulation of human intelligence by machines.", ln=1)
pdf.cell(200, 10, txt="Machine Learning is a subset of AI.", ln=1)
pdf.cell(200, 10, txt="Deep Learning is a subset of Machine Learning.", ln=1)
pdf.cell(200, 10, txt="Neural Networks are the backbone of Deep Learning.", ln=1)
pdf.output("d:/final project/test_analytics.pdf")
