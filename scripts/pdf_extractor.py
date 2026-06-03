import pdfplumber
import os

def extract_from_pdf(pdf_path: str) -> str:
    """
    Extracts text from a PDF file using pdfplumber.
    
    :param pdf_path: Path to the PDF file.
    :return: Extracted text as a string.
    :raises FileNotFoundError: If the PDF file does not exist.
    :raises Exception: For other errors during text extraction.
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"Arquivo PDF não encontrado: {pdf_path}")
        
    text_content = []
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                text = page.extract_text()
                if text:
                    text_content.append(text)
    except Exception as e:
        raise Exception(f"Erro ao ler o arquivo PDF {pdf_path}: {str(e)}")
        
    extracted_text = "\n".join(text_content).strip()
    
    if not extracted_text:
        raise ValueError("O PDF está vazio ou não contém texto digitalizável.")
        
    return extracted_text

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        try:
            texto = extract_from_pdf(file_path)
            print("--- Texto Extraído ---")
            print(texto)
            print("----------------------")
        except Exception as e:
            print(f"Erro: {e}", file=sys.stderr)
    else:
        print("Uso: python pdf_extractor.py <caminho_do_pdf>")
