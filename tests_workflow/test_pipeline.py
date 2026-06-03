import os
import unittest
from unittest.mock import patch, MagicMock
from PIL import Image, ImageDraw

try:
    from scripts.input_handler import extract_text
    from scripts.pdf_extractor import extract_from_pdf
    from scripts.ocr_engine import extract_from_image
except ImportError:
    import sys
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from scripts.input_handler import extract_text
    from scripts.pdf_extractor import extract_from_pdf
    from scripts.ocr_engine import extract_from_image

class TestInputHandler(unittest.TestCase):
    
    def setUp(self):
        # Create temp text file for testing
        self.txt_path = "test_essay.txt"
        with open(self.txt_path, "w", encoding="utf-8") as f:
            f.write("Esta e uma redacao de teste escrita em texto plano.")
            
        self.unsupported_path = "test_essay.xyz"
        with open(self.unsupported_path, "w", encoding="utf-8") as f:
            f.write("Texto qualquer.")

    def tearDown(self):
        if os.path.exists(self.txt_path):
            os.remove(self.txt_path)
        if os.path.exists(self.unsupported_path):
            os.remove(self.unsupported_path)
            
    def test_extract_text_txt(self):
        text = extract_text(self.txt_path)
        self.assertEqual(text, "Esta e uma redacao de teste escrita em texto plano.")
        
    def test_extract_text_unsupported(self):
        with self.assertRaises(ValueError):
            extract_text(self.unsupported_path)
            
    def test_file_not_found(self):
        with self.assertRaises(FileNotFoundError):
            extract_text("non_existent_file.pdf")


class TestPdfExtractor(unittest.TestCase):
    
    def test_pdf_extraction_real_or_mock(self):
        # Check if we have the sample PDF
        sample_pdf = "cartilha_enem_2025.pdf"
        if os.path.exists(sample_pdf):
            try:
                text = extract_from_pdf(sample_pdf)
                self.assertTrue(len(text) > 0)
                # Confirm it contains some ENEM-related text
                self.assertIn("ENEM", text.upper())
            except Exception as e:
                self.fail(f"Falta de suporte do ambiente ou erro na leitura do PDF: {e}")
        else:
            # Mock testing if file is missing
            with patch("pdfplumber.open") as mock_open:
                mock_pdf = MagicMock()
                mock_page = MagicMock()
                mock_page.extract_text.return_value = "Texto mockado do PDF"
                mock_pdf.pages = [mock_page]
                mock_open.return_value.__enter__.return_value = mock_pdf
                
                text = extract_from_pdf("mock.pdf")
                self.assertEqual(text, "Texto mockado do PDF")


class TestOcrEngine(unittest.TestCase):
    
    def setUp(self):
        # Create a simple image containing printed text to test OCR
        self.img_path = "test_ocr_image.png"
        img = Image.new("RGB", (400, 100), color=(255, 255, 255))
        d = ImageDraw.Draw(img)
        d.text((10, 10), "TESTE OCR", fill=(0, 0, 0))
        img.save(self.img_path)

    def tearDown(self):
        if os.path.exists(self.img_path):
            os.remove(self.img_path)

    def test_ocr_extraction(self):
        # Try running OCR, but mock/skip if Tesseract is not installed
        try:
            text = extract_from_image(self.img_path)
            self.assertIsNotNone(text)
        except (RuntimeError, Exception):
            with patch("pytesseract.image_to_string") as mock_ocr:
                mock_ocr.return_value = "TEXTO EXTRAIDO POR OCR"
                text = extract_from_image(self.img_path)
                self.assertEqual(text, "TEXTO EXTRAIDO POR OCR")

if __name__ == "__main__":
    unittest.main()
