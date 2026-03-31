"""PDF and text file processing module.

Provides functionality to extract text from PDFs and text files,
auto-detect file types, and handle encoding issues.
"""

import os
import re
from pathlib import Path
from typing import Optional, Tuple
from dataclasses import dataclass


@dataclass
class PDFExtractionResult:
    """Result of PDF/text extraction."""
    text: str
    file_type: str  # 'pdf', 'text', or 'unknown'
    page_count: int
    encoding: str
    success: bool
    error: Optional[str] = None


class PDFProcessor:
    """Process PDF and text files to extract algorithm text."""
    
    def __init__(self):
        self.supported_extensions = {'.pdf', '.txt', '.md', '.markdown'}
        self.text_extensions = {'.txt', '.md', '.markdown'}
    
    def extract_text(self, file_path: str) -> PDFExtractionResult:
        """
        Extract text from file (PDF or text).
        
        Args:
            file_path: Path to file
            
        Returns:
            PDFExtractionResult with extracted text
        """
        path = Path(file_path)
        
        # Check if file exists
        if not path.exists():
            return PDFExtractionResult(
                text="",
                file_type="unknown",
                page_count=0,
                encoding="",
                success=False,
                error=f"File not found: {file_path}"
            )
        
        # Check extension
        ext = path.suffix.lower()
        if ext not in self.supported_extensions:
            return PDFExtractionResult(
                text="",
                file_type="unknown",
                page_count=0,
                encoding="",
                success=False,
                error=f"Unsupported file type: {ext}. Supported: {self.supported_extensions}"
            )
        
        # Route to appropriate handler
        if ext == '.pdf':
            return self._extract_pdf(file_path)
        elif ext in self.text_extensions:
            return self._read_text_file(file_path)
        else:
            return PDFExtractionResult(
                text="",
                file_type="unknown",
                page_count=0,
                encoding="",
                success=False,
                error=f"Unknown file type: {ext}"
            )
    
    def _extract_pdf(self, file_path: str) -> PDFExtractionResult:
        """
        Extract text from PDF file.
        
        Uses pdfplumber for text-based PDFs.
        Falls back to PyMuPDF for complex layouts.
        """
        try:
            # Try pdfplumber first (best for text-based PDFs)
            import pdfplumber
            
            text_parts = []
            page_count = 0
            
            with pdfplumber.open(file_path) as pdf:
                page_count = len(pdf.pages)
                
                for i, page in enumerate(pdf.pages):
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)
            
            full_text = '\n\n'.join(text_parts)
            
            # Check if we got any text
            if not full_text.strip():
                # Try PyMuPDF as fallback for image-based or complex PDFs
                return self._extract_pdf_with_pymupdf(file_path)
            
            return PDFExtractionResult(
                text=full_text,
                file_type='pdf',
                page_count=page_count,
                encoding='utf-8',
                success=True
            )
            
        except ImportError:
            # pdfplumber not installed, try PyMuPDF
            return self._extract_pdf_with_pymupdf(file_path)
        except Exception as e:
            return PDFExtractionResult(
                text="",
                file_type='pdf',
                page_count=0,
                encoding="",
                success=False,
                error=f"PDF extraction failed: {str(e)}"
            )
    
    def _extract_pdf_with_pymupdf(self, file_path: str) -> PDFExtractionResult:
        """Fallback PDF extraction using PyMuPDF (fitz)."""
        try:
            import fitz  # PyMuPDF
            
            text_parts = []
            page_count = 0
            
            with fitz.open(file_path) as doc:
                page_count = len(doc)
                
                for page in doc:
                    text_parts.append(page.get_text())
            
            full_text = '\n\n'.join(text_parts)
            
            return PDFExtractionResult(
                text=full_text,
                file_type='pdf',
                page_count=page_count,
                encoding='utf-8',
                success=True
            )
            
        except ImportError:
            return PDFExtractionResult(
                text="",
                file_type='pdf',
                page_count=0,
                encoding="",
                success=False,
                error="PDF libraries not installed. Run: pip install pdfplumber pymupdf"
            )
        except Exception as e:
            return PDFExtractionResult(
                text="",
                file_type='pdf',
                page_count=0,
                encoding="",
                success=False,
                error=f"PDF extraction failed: {str(e)}"
            )
    
    def _read_text_file(self, file_path: str) -> PDFExtractionResult:
        """Read plain text file."""
        try:
            # Try UTF-8 first
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
            
            return PDFExtractionResult(
                text=text,
                file_type='text',
                page_count=1,
                encoding='utf-8',
                success=True
            )
            
        except UnicodeDecodeError:
            # Try other encodings
            encodings = ['latin-1', 'cp1252', 'iso-8859-1']
            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        text = f.read()
                    
                    return PDFExtractionResult(
                        text=text,
                        file_type='text',
                        page_count=1,
                        encoding=encoding,
                        success=True
                    )
                except UnicodeDecodeError:
                    continue
            
            return PDFExtractionResult(
                text="",
                file_type='text',
                page_count=0,
                encoding="",
                success=False,
                error="Could not decode file. Try specifying encoding."
            )
        except Exception as e:
            return PDFExtractionResult(
                text="",
                file_type='text',
                page_count=0,
                encoding="",
                success=False,
                error=f"Text file read failed: {str(e)}"
            )
    
    def is_text_based_pdf(self, file_path: str) -> bool:
        """
        Check if PDF contains extractable text vs just images.
        
        Returns True if PDF has text content.
        """
        try:
            import pdfplumber
            
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text and text.strip():
                        return True
            return False
            
        except Exception:
            return False
    
    def extract_algorithm_section(self, text: str) -> Tuple[str, int, int]:
        """
        Attempt to find algorithm section within extracted text.
        
        Args:
            text: Full extracted text
            
        Returns:
            Tuple of (algorithm_text, start_index, end_index)
        """
        # Common patterns that indicate algorithm sections
        patterns = [
            r'(?i)(?:algorithm|procedure|function)\s+\w+.*?\n.*?\n(?:end|return)',
            r'(?i)(?:input|output):.*?\n.*?\n(?:end|return)',
            r'(?i)step\s*\d+[:.]\s*.+?(?:\n\n|\Z)',
        ]
        
        for pattern in patterns:
            matches = list(re.finditer(pattern, text, re.DOTALL))
            if matches:
                # Return the longest match (most likely complete algorithm)
                longest = max(matches, key=lambda m: len(m.group()))
                return (
                    longest.group(),
                    longest.start(),
                    longest.end()
                )
        
        # If no pattern matched, return first 5000 chars (heuristic)
        return (text[:5000], 0, min(5000, len(text)))


# Convenience function
def extract_text_from_file(file_path: str) -> PDFExtractionResult:
    """Extract text from PDF or text file."""
    processor = PDFProcessor()
    return processor.extract_text(file_path)
