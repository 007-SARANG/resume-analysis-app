"""
PDF Parser Module
Handles PDF file upload and text extraction using multiple libraries for robustness.
"""

import PyPDF2
import pdfplumber
import io
import logging
from typing import Optional, Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PDFParser:
    """
    A robust PDF parser that tries multiple extraction methods
    to handle different PDF formats and structures.
    """
    
    def __init__(self):
        self.supported_formats = ['.pdf']
    
    def extract_text_pypdf2(self, pdf_file) -> str:
        """
        Extract text using PyPDF2 library.
        Good for simple, text-based PDFs.
        """
        try:
            # Handle both file objects and byte streams
            if hasattr(pdf_file, 'read'):
                pdf_content = io.BytesIO(pdf_file.read())
            else:
                pdf_content = pdf_file
            
            pdf_reader = PyPDF2.PdfReader(pdf_content)
            text = ""
            
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            
            return text.strip()
        
        except Exception as e:
            logger.error(f"PyPDF2 extraction failed: {str(e)}")
            return ""
    
    def extract_text_pdfplumber(self, pdf_file) -> str:
        """
        Extract text using pdfplumber library.
        Better for complex layouts and tables.
        """
        try:
            # Handle both file objects and byte streams
            if hasattr(pdf_file, 'read'):
                pdf_content = io.BytesIO(pdf_file.read())
            else:
                pdf_content = pdf_file
            
            text = ""
            with pdfplumber.open(pdf_content) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            
            return text.strip()
        
        except Exception as e:
            logger.error(f"pdfplumber extraction failed: {str(e)}")
            return ""
    
    def extract_text(self, pdf_file) -> Dict[str, Any]:
        """
        Main extraction method that tries multiple approaches
        and returns the best result along with metadata.
        """
        # For Streamlit uploaded files, we need to read the content
        if hasattr(pdf_file, 'read'):
            # Read the file content once
            pdf_file.seek(0)
            file_content = pdf_file.read()
            
            # Try pdfplumber first (usually better results)
            pdf_file.seek(0)
            text_plumber = self.extract_text_pdfplumber(pdf_file)
            
            # Try PyPDF2 
            pdf_file.seek(0)
            text_pypdf2 = self.extract_text_pypdf2(pdf_file)
        else:
            # For file-like objects
            text_plumber = self.extract_text_pdfplumber(pdf_file)
            text_pypdf2 = self.extract_text_pypdf2(pdf_file)
        
        # Choose the better extraction (longer text usually means better extraction)
        if len(text_plumber) > len(text_pypdf2):
            best_text = text_plumber
            method_used = "pdfplumber"
        else:
            best_text = text_pypdf2
            method_used = "PyPDF2"
        
        # If both failed, return empty
        if not best_text or not best_text.strip():
            logger.warning("Both extraction methods failed")
            return {
                "text": "",
                "success": False,
                "method": "none",
                "word_count": 0,
                "char_count": 0,
                "error": "Could not extract text from PDF. The PDF might be image-based or corrupted."
            }
        
        # Calculate basic statistics
        word_count = len(best_text.split())
        char_count = len(best_text)
        
        return {
            "text": best_text,
            "success": True,
            "method": method_used,
            "word_count": word_count,
            "char_count": char_count,
            "error": None
        }
    
    def validate_pdf(self, uploaded_file) -> Dict[str, Any]:
        """
        Validate the uploaded file before processing.
        """
        if not uploaded_file:
            return {"valid": False, "error": "No file uploaded"}
        
        # Check file extension
        if not uploaded_file.name.lower().endswith('.pdf'):
            return {"valid": False, "error": "File must be a PDF"}
        
        # Check file size (limit to 10MB)
        file_size = uploaded_file.size
        if file_size > 10 * 1024 * 1024:  # 10MB in bytes
            return {"valid": False, "error": "File size must be less than 10MB"}
        
        # Try to read as PDF
        try:
            uploaded_file.seek(0)
            PyPDF2.PdfReader(uploaded_file)
            uploaded_file.seek(0)
            return {"valid": True, "error": None, "size": file_size}
        
        except Exception as e:
            return {"valid": False, "error": f"Invalid PDF file: {str(e)}"}
    
    def process_uploaded_file(self, uploaded_file) -> Dict[str, Any]:
        """
        Complete processing pipeline for uploaded PDF files.
        """
        # Validate file first
        validation = self.validate_pdf(uploaded_file)
        if not validation["valid"]:
            return {
                "success": False,
                "error": validation["error"],
                "text": "",
                "metadata": {}
            }
        
        # Extract text
        extraction_result = self.extract_text(uploaded_file)
        
        if extraction_result["success"]:
            return {
                "success": True,
                "error": None,
                "text": extraction_result["text"],
                "metadata": {
                    "file_name": uploaded_file.name,
                    "file_size": validation["size"],
                    "extraction_method": extraction_result["method"],
                    "word_count": extraction_result["word_count"],
                    "char_count": extraction_result["char_count"]
                }
            }
        else:
            return {
                "success": False,
                "error": extraction_result["error"],
                "text": "",
                "metadata": {"file_name": uploaded_file.name}
            }

# Convenience function for easy import
def parse_pdf(uploaded_file) -> Dict[str, Any]:
    """
    Simple function to parse PDF and return extracted text and metadata.
    """
    parser = PDFParser()
    return parser.process_uploaded_file(uploaded_file)