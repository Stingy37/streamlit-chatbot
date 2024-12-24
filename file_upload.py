import os
import streamlit as st
import PyPDF2
import pytesseract
from PIL import Image

def handle_file_upload(uploaded_file, chat_id):
    file_extension = os.path.splitext(uploaded_file.name)[1].lower()
    if file_extension == ".pdf":
        # Use PyPDF2 to read the PDF file
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        text = ""
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text += page.extract_text()
        # Store the extracted text for this chat session
        st.session_state.document_text[chat_id] = text
        st.success("PDF text extracted and stored.")
    elif file_extension == ".py":
        # Read the .py file
        code = uploaded_file.getvalue().decode("utf-8")
        # Store the code for this chat session
        st.session_state.document_text[chat_id] = code
        st.success(".py file code extracted and stored.")
    elif file_extension in [".png", ".jpg", ".jpeg"]:
        # Use PIL and pytesseract to read the image and extract text
        try:
            image = Image.open(uploaded_file)
            extracted_text = pytesseract.image_to_string(image)
            if extracted_text.strip():
                # Store the extracted text for this chat session
                st.session_state.document_text[chat_id] = extracted_text
                st.success("Text extracted from image and stored.")
            else:
                st.warning("No text found in the image.")
        except Exception as e:
            st.error(f"An error occurred while processing the image: {e}")
    else:
        st.error("Unsupported file type. Please upload a PDF, .py file, or an image.")