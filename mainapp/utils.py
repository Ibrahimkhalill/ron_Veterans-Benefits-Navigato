import os
from PyPDF2 import PdfReader

def list_pdf_fields(pdf_path):
    # Get the absolute path of the PDF file
    pdf_path = os.path.abspath(pdf_path)
    
    # Open and read the PDF file
    reader = PdfReader(pdf_path)
    
    # Extract the fields from the PDF
    fields = reader.get_fields()

    for field, field_info in fields.items():
        # Get the field name and type
        field_name = field_info.get("/T", "No Name")
        field_type = field_info.get("/FT", "No Type")
        
        # Get the field value (if available)
        field_value = field_info.get("/V", "No Value")
        
        # Handle checkbox field type (if applicable)
        if field_type == "/Btn" and field_value != "No Value":
            # If it's a button (checkbox/radio button), check if it's selected
            field_value = "Selected" if field_value else "Not Selected"
        
        # Print field name, type, and value
        print(f"{field_name}, Field Type: {field_type}, Field Value: {field_value}")

# Provide the relative path to the PDF file
list_pdf_fields('static/pdfs/VBA-21-0966-ARE.pdf')
