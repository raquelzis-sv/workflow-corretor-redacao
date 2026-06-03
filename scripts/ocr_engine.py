import os
import cv2
import pytesseract
from PIL import Image

# For Windows, if Tesseract is not in the system PATH, the user can configure the path.
# We will check common installation paths on Windows to make it work out-of-the-box if possible.
COMMON_TESSERACT_WINDOWS_PATHS = [
    r"C:\Program Files\Tesseract-OCR\tesseract.exe",
    r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
    os.path.expanduser(r"~\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"),
]

def configure_tesseract():
    """Attempts to configure the Tesseract executable path if on Windows."""
    if os.name == 'nt':
        # If tesseract is already in PATH, pytesseract will find it.
        # Otherwise, we check common locations.
        try:
            pytesseract.get_tesseract_version()
        except pytesseract.TesseractNotFoundError:
            for path in COMMON_TESSERACT_WINDOWS_PATHS:
                if os.path.exists(path):
                    pytesseract.pytesseract.tesseract_cmd = path
                    break

def preprocess_image(image_path: str) -> Image.Image:
    """
    Applies preprocessing to improve OCR accuracy on photographed text.
    - Grayscale conversion
    - Noise reduction (Gaussian Blur)
    - Thresholding (Otsu's binarization)
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Imagem não encontrada: {image_path}")

    # Read image using OpenCV
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Não foi possível ler a imagem: {image_path}")

    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Resize image if it's too small (optional but helps OCR)
    # We will upscale if width is less than 1000px
    height, width = gray.shape
    if width < 1000:
        scale_ratio = 1000.0 / width
        gray = cv2.resize(gray, (0, 0), fx=scale_ratio, fy=scale_ratio, interpolation=cv2.INTER_CUBIC)

    # Apply adaptive thresholding or Otsu thresholding
    # Otsu's thresholding after Gaussian filtering
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    _, thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # Convert back to PIL Image for pytesseract compatibility
    return Image.fromarray(thresh)

def extract_from_image(image_path: str, lang: str = "por") -> str:
    """
    Extracts text from an image using pytesseract.
    
    :param image_path: Path to the image file (png, jpg, jpeg, etc.)
    :param lang: Language code for Tesseract (default: 'por' for Portuguese)
    :return: Extracted text as a string.
    """
    configure_tesseract()
    
    try:
        # Preprocess the image
        processed_pil_img = preprocess_image(image_path)
        
        # Run OCR
        # We specify custom configuration to optimize for page layout/blocks
        custom_config = r'--oem 3 --psm 6'
        text = pytesseract.image_to_string(processed_pil_img, lang=lang, config=custom_config)
        
        extracted_text = text.strip()
        if not extracted_text:
            # Fallback to OCR without preprocessing in case preprocessing cleared out the image
            # (e.g. if the image was already very clean or had special colors)
            pil_img = Image.open(image_path)
            text = pytesseract.image_to_string(pil_img, lang=lang, config=custom_config)
            extracted_text = text.strip()
            
        return extracted_text

    except pytesseract.TesseractNotFoundError:
        raise RuntimeError(
            "Tesseract OCR não está instalado ou não foi encontrado no PATH.\n"
            "Por favor, instale o Tesseract OCR e garanta que ele esteja configurado.\n"
            "Windows: Baixe em https://github.com/UB-Mannheim/tesseract/wiki\n"
            "macOS: brew install tesseract\n"
            "Linux: sudo apt-get install tesseract-ocr tesseract-ocr-por"
        )
    except Exception as e:
        raise Exception(f"Erro ao processar imagem para OCR: {str(e)}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        try:
            texto = extract_from_image(file_path)
            print("--- Texto Extraído (OCR) ---")
            print(texto)
            print("----------------------------")
        except Exception as e:
            print(f"Erro: {e}", file=sys.stderr)
    else:
        print("Uso: python ocr_engine.py <caminho_da_imagem>")
