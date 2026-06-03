import os
import mimetypes

try:
    from scripts.pdf_extractor import extract_from_pdf
    from scripts.ocr_engine import extract_from_image
except ImportError:
    from pdf_extractor import extract_from_pdf
    from ocr_engine import extract_from_image

# Supported file extensions
PDF_EXTENSIONS = {'.pdf'}
IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.webp'}
TEXT_EXTENSIONS = {'.txt', '.md'}

def extract_text(file_path: str) -> str:
    """
    Detects the file type and extracts the text using the appropriate handler.
    
    :param file_path: Path to the input file.
    :return: Extracted text as a string.
    :raises FileNotFoundError: If the file does not exist.
    :raises ValueError: If the file format is unsupported or text cannot be extracted.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")
        
    _, ext = os.path.splitext(file_path.lower())
    
    # Try guessing by mime type if extension is empty
    if not ext:
        mime, _ = mimetypes.guess_type(file_path)
        if mime:
            if 'pdf' in mime:
                ext = '.pdf'
            elif 'image' in mime:
                ext = '.png' # Default image fallback
            elif 'text' in mime:
                ext = '.txt'
                
    if ext in PDF_EXTENSIONS:
        return extract_from_pdf(file_path)
    elif ext in IMAGE_EXTENSIONS:
        return extract_from_image(file_path)
    elif ext in TEXT_EXTENSIONS:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read().strip()
        except UnicodeDecodeError:
            # Fallback to latin-1 if utf-8 fails
            with open(file_path, 'r', encoding='latin-1') as f:
                return f.read().strip()
    else:
        raise ValueError(
            f"Formato de arquivo não suportado: '{ext}'. "
            f"Formatos válidos: PDFs, Imagens ({', '.join(sorted(IMAGE_EXTENSIONS))}) ou Arquivos de texto."
        )

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        path = sys.argv[1]
        try:
            texto = extract_text(path)
            print("=== TEXTO EXTRAÍDO ===")
            print(texto)
            print("======================")
        except Exception as e:
            print(f"Erro: {e}", file=sys.stderr)
    else:
        print("Uso: python input_handler.py <caminho_do_arquivo>")
