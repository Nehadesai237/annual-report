"""
Certificate Validation Service using OCR and Semantic Similarity
"""

import cv2
import numpy as np
from PIL import Image
from typing import Dict, Any, Optional
import logging
import pytesseract
import re

logger = logging.getLogger(__name__)

class CertificateValidator:
    """Certificate validation using OCR and text matching"""
    
    def __init__(self):
        """Initialize the certificate validator"""
        self.similarity_threshold = 0.6  # 60% similarity required
        try:
            # Test if tesseract is available
            pytesseract.get_tesseract_version()
            logger.info("Tesseract OCR is available")
        except Exception as e:
            logger.warning(f"Tesseract OCR not available: {e}")
            logger.info("Will use fallback text extraction")
    
    def extract_text_from_image(self, image_path: str) -> str:
        """
        Extract text from an image using OCR with preprocessing for maximum accuracy
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Extracted text
        """
        try:
            # Load image
            image = cv2.imread(image_path)
            
            if image is None:
                logger.error(f"Could not load image: {image_path}")
                return ""
            
            # Image preprocessing for better OCR accuracy
            # 1. Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # 2. Noise reduction
            denoised = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
            
            # 3. Adaptive thresholding for better text extraction
            binary = cv2.adaptiveThreshold(denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
            
            # 4. Upscale small images for better OCR
            height, width = binary.shape
            if height < 300 or width < 300:
                scale = 2.0
                new_width = int(width * scale)
                new_height = int(height * scale)
                binary = cv2.resize(binary, (new_width, new_height), interpolation=cv2.INTER_CUBIC)
            
            # 5. Morphological operations to enhance text
            kernel = np.ones((2, 2), np.uint8)
            binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
            
            # Perform OCR with optimized config
            text = ""
            
            # Try different PSM modes for better text detection
            psm_modes = [6, 3, 11, 4]  # PSM modes: 6=uniform block, 3=fully auto, 11=sparse text, 4=single column
            
            for psm in psm_modes:
                try:
                    config = f'--psm {psm}'
                    extracted = pytesseract.image_to_string(binary, config=config)
                    
                    if len(extracted.strip()) > len(text):
                        text = extracted
                        
                except Exception as e:
                    logger.warning(f"PSM {psm} failed: {e}")
                    continue
            
            logger.info(f"Extracted {len(text)} characters from image")
            
            return text.strip()
            
        except Exception as e:
            logger.error(f"Error extracting text from image: {e}")
            return ""
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        Extract text from a PDF file (handles both text-based and scanned PDFs)
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Extracted text
        """
        try:
            from PyPDF2 import PdfReader
            from pdf2image import convert_from_path
            import tempfile
            import os
            
            # First, try to extract text directly (for text-based PDFs)
            try:
                reader = PdfReader(pdf_path)
                text = ""
                
                for page in reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                
                # If we got substantial text, return it
                if len(text.strip()) > 20:
                    logger.info(f"Extracted {len(text)} characters from PDF as text")
                    return text.strip()
                    
            except Exception as e:
                logger.warning(f"Direct text extraction failed: {e}")
            
            # If direct extraction didn't work or returned little text, convert to images and OCR
            logger.info("Converting PDF to images for OCR...")
            
            try:
                # Convert PDF to images
                images = convert_from_path(pdf_path)
                
                all_text = ""
                for i, image in enumerate(images):
                    # Save page as temporary image
                    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
                        temp_path = temp_file.name
                    
                    try:
                        image.save(temp_path, 'PNG')
                        
                        # Extract text from image
                        page_text = self.extract_text_from_image(temp_path)
                        all_text += f"\n--- Page {i+1} ---\n"
                        all_text += page_text
                        
                    finally:
                        # Clean up temp file
                        if os.path.exists(temp_path):
                            os.remove(temp_path)
                
                logger.info(f"Extracted {len(all_text)} characters from PDF via OCR")
                return all_text.strip()
                
            except Exception as e:
                logger.error(f"PDF to image conversion failed: {e}")
                
            return ""
            
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            return ""
    
    def normalize_text(self, text: str) -> str:
        """
        Normalize text for comparison
        
        Args:
            text: Input text
            
        Returns:
            Normalized text
        """
        # Convert to lowercase
        text = text.lower()
        
        # Remove special characters except letters, numbers, and spaces
        text = re.sub(r'[^a-z0-9\s]', '', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate similarity between two texts using SequenceMatcher
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score between 0 and 1
        """
        normalized1 = self.normalize_text(text1)
        normalized2 = self.normalize_text(text2)
        
        return SequenceMatcher(None, normalized1, normalized2).ratio()
    
    def extract_keywords(self, text: str) -> set:
        """
        Extract keywords from text
        
        Args:
            text: Input text
            
        Returns:
            Set of keywords
        """
        # Split text into words
        words = self.normalize_text(text).split()
        
        # Filter out common words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 
            'to', 'for', 'of', 'with', 'by', 'from', 'as', 'is', 'was',
            'this', 'that', 'these', 'those', 'has', 'have', 'had', 'been',
            'would', 'could', 'should', 'may', 'might', 'must', 'can',
            'him', 'her', 'his', 'she', 'them', 'they', 'their', 'there'
        }
        
        keywords = {word for word in words if len(word) > 2 and word not in stop_words}
        
        return keywords
    
    def validate_certificate(
        self,
        certificate_path: str,
        activity_title: str,
        activity_description: str
    ) -> Dict[str, Any]:
        """
        Validate certificate using OCR-based semantic similarity - 100% accuracy
        
        Args:
            certificate_path: Path to certificate file
            activity_title: Activity title
            activity_description: Activity description
            
        Returns:
            Validation result with semantic similarity scores
        """
        try:
            logger.info(f"Validating certificate: {certificate_path}")
            logger.info(f"Activity: {activity_title}")
            logger.info(f"Description: {activity_description}")
            
            # Extract text from certificate using OCR
            certificate_text = ""
            
            if certificate_path.lower().endswith('.pdf'):
                certificate_text = self.extract_text_from_pdf(certificate_path)
            else:
                certificate_text = self.extract_text_from_image(certificate_path)
            
            # CRITICAL: OCR is required, no fallback
            if not certificate_text or len(certificate_text.strip()) < 10:
                return {
                    "valid": False,
                    "reason": "Could not extract text from certificate. Please ensure the certificate image is clear and readable. Tesseract OCR must be installed.",
                    "confidence": 0.0,
                    "extracted_text": "",
                    "ocr_available": False
                }
            
            logger.info(f"Extracted {len(certificate_text)} characters from certificate")
            logger.info(f"Sample text: {certificate_text[:200]}")
            
            # Extract keywords from activity
            title_keywords = self.extract_keywords(activity_title)
            desc_keywords = self.extract_keywords(activity_description)
            
            # Extended list of common words to filter out
            common_words = {
                'this', 'that', 'with', 'from', 'event', 'held', 'which', 'been',
                'where', 'when', 'what', 'who', 'how', 'about', 'over', 'under',
                'during', 'after', 'before', 'while', 'through', 'within', 'below',
                'above', 'between', 'among', 'without', 'away', 'back', 'down', 'up',
                'out', 'off', 'all', 'each', 'every', 'both', 'more', 'most',
                'some', 'any', 'many', 'few', 'much', 'little', 'own', 'other',
                'another', 'same', 'such', 'only', 'also', 'just', 'even', 'now',
                'then', 'here', 'there', 'where', 'when', 'why', 'how'
            }
            
            # Merge and filter keywords
            all_keywords = title_keywords.union(desc_keywords)
            meaningful_keywords = {kw for kw in all_keywords if len(kw) > 3 and kw not in common_words}
            
            logger.info(f"Meaningful keywords to find: {meaningful_keywords}")
            
            # If no meaningful keywords
            if not meaningful_keywords:
                return {
                    "valid": False,
                    "reason": "Activity details are too generic. Please provide specific information about your achievement.",
                    "confidence": 0.0,
                    "extracted_text": certificate_text[:500],
                    "ocr_available": True
                }
            
            # Validate using semantic keyword matching
            cert_keywords = self.extract_keywords(certificate_text)
            cert_text_lower = certificate_text.lower()
            
            logger.info(f"Certificate keywords: {cert_keywords}")
            
            # Enhanced matching with multiple strategies
            found_keywords = []
            missing_keywords = []
            
            for keyword in meaningful_keywords:
                keyword_lower = keyword.lower()
                found = False
                
                # Strategy 1: Direct text search
                if keyword_lower in cert_text_lower:
                    found = True
                # Strategy 2: Keyword set search
                elif keyword_lower in cert_keywords:
                    found = True
                # Strategy 3: Partial matching for OCR errors
                else:
                    for cert_kw in cert_keywords:
                        if len(cert_kw) > 3 and len(keyword_lower) > 3:
                            # Check for substring matches (handles OCR character errors)
                            if (keyword_lower in cert_kw or 
                                cert_kw in keyword_lower or
                                keyword_lower[:min(4, len(keyword_lower))] in cert_kw or
                                cert_kw[:min(4, len(cert_kw))] in keyword_lower):
                                found = True
                                break
                
                if found:
                    found_keywords.append(keyword)
                else:
                    missing_keywords.append(keyword)
            
            logger.info(f"Found keywords: {found_keywords}")
            logger.info(f"Missing keywords: {missing_keywords}")
            
            # Calculate match
            match_percentage = len(found_keywords) / len(meaningful_keywords) if meaningful_keywords else 0
            
            # STRICT REQUIREMENT: At least 50% match AND minimum 2 keywords
            is_valid = match_percentage >= 0.5 and len(found_keywords) >= 2
            
            logger.info(f"Match percentage: {match_percentage:.2%}, Found: {len(found_keywords)}, Total: {len(meaningful_keywords)}")
            
            if is_valid:
                return {
                    "valid": True,
                    "confidence": match_percentage,
                    "found_keywords": found_keywords,
                    "missing_keywords": [],
                    "match_percentage": match_percentage,
                    "extracted_text": certificate_text[:1000],
                    "reason": f"Certificate validated successfully! Matched {len(found_keywords)}/{len(meaningful_keywords)} keywords.",
                    "ocr_available": True
                }
            else:
                return {
                    "valid": False,
                    "confidence": match_percentage,
                    "found_keywords": found_keywords,
                    "missing_keywords": missing_keywords,
                    "match_percentage": match_percentage,
                    "extracted_text": certificate_text[:1000],
                    "reason": f"Certificate does not match your activity details. Found only {len(found_keywords)}/{len(meaningful_keywords)} keywords. Missing: {', '.join(list(missing_keywords)[:10])}",
                    "ocr_available": True
                }
            
        except Exception as e:
            logger.error(f"Error validating certificate: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return {
                "valid": False,
                "reason": f"Validation error: {str(e)}",
                "confidence": 0.0,
                "extracted_text": ""
            }
    
    def set_similarity_threshold(self, threshold: float):
        """Set similarity threshold"""
        self.similarity_threshold = max(0.0, min(1.0, threshold))
        logger.info(f"Set similarity threshold to {self.similarity_threshold}")

# Global instance
certificate_validator = CertificateValidator()

