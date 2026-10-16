"""
Production Clinical Information Extraction Dashboard.
Multi-Tier Engine with AI OCR:
1. pdfplumber digital text stream extraction
2. If text is empty or boilerplate/scanned, automatically renders PDF pages and runs EasyOCR AI!
3. Parses OpenI XML files (.xml)
4. Plain text (.txt) and CSV (.csv) support
"""

import sys
import io

# Ensure UTF-8 output streams on Windows to prevent cp1252 crashes
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

import os
import json
import base64
import re
import numpy as np
from PIL import Image
import pdfplumber
import pypdfium2
import easyocr
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler

sys.path.append(r"C:\Users\palem\OneDrive\Documents\3rd Year\Machine Learning\src")
from inference_engine import analyze_report

INDEX_HTML_PATH = os.path.join(os.path.dirname(__file__), "index.html")

# Initialize EasyOCR reader (English)
print("Initializing EasyOCR Engine...")
_OCR_READER = easyocr.Reader(['en'], gpu=False, verbose=False)
print("EasyOCR Engine initialized successfully!")

def clean_and_format_clinical_text(raw_lines):
    """Formats clinical sections with clean spacing for readability."""
    formatted = []
    headers = ["EXAM:", "CLINICAL HISTORY:", "INDICATIONS:", "INDICATION:", "PROCEDURE:", "FINDINGS:", "IMPRESSION:", "TECHNIQUE:"]
    for line in raw_lines:
        line_clean = line.strip().strip('_~=-')
        if not line_clean:
            continue
        is_header = any(line_clean.upper().startswith(h) for h in headers)
        if is_header and formatted:
            formatted.append("\n" + line_clean)
        else:
            formatted.append(line_clean)
    return "\n".join(formatted)

def extract_text_from_pdf(pdf_bytes):
    """
    Multi-tier extraction:
    - Tier 1: Try digital text streams using pdfplumber.
    - Tier 2: If the text is only headers/boilerplate or lacks clinical body,
      automatically renders PDF pages to images and runs EasyOCR AI!
    """
    text_parts = []
    
    # Try pdfplumber
    try:
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            for page in pdf.pages:
                txt = page.extract_text()
                if txt and len(txt.strip()) > 20:
                    text_parts.append(txt.strip())
    except Exception:
        pass
        
    full_text = "\n\n".join(text_parts).strip()
    
    # Check if extracted digital text lacks clinical body
    lower_text = full_text.lower()
    has_body = any(k in lower_text for k in ["findings", "impression", "lungs", "heart", "sinus", "cardiopulmonary", "normal", "clear"])
    is_boilerplate_only = ("completing your image" in lower_text and not ("findings" in lower_text or "impression" in lower_text))
    
    if not has_body or is_boilerplate_only or len(full_text) < 150:
        print("Standard PDF stream lacks clinical report body. Activating EasyOCR AI on page images...")
        try:
            pdf = pypdfium2.PdfDocument(pdf_bytes)
            ocr_text_parts = []
            for i in range(len(pdf)):
                page = pdf[i]
                # Render page to high-res image (200 DPI)
                bitmap = page.render(scale=2.0)
                pil_image = bitmap.to_pil()
                img_np = np.array(pil_image)
                ocr_results = _OCR_READER.readtext(img_np, detail=0)
                if ocr_results:
                    formatted_page = clean_and_format_clinical_text(ocr_results)
                    ocr_text_parts.append(formatted_page)
            if ocr_text_parts:
                full_text = "\n\n".join(ocr_text_parts).strip()
                print("EasyOCR successfully extracted clinical text from scanned image!")
        except Exception as ocr_err:
            print("OCR extraction error:", ocr_err)
            
    # Clean decorative characters
    full_text = re.sub(r'[\~_\-]{4,}', '', full_text).strip()
    return full_text

class ServerHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/" or self.path == "/index.html":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            with open(INDEX_HTML_PATH, "rb") as f:
                self.wfile.write(f.read())
        elif self.path == "/caduceus.png" or self.path == "/favicon.ico":
            icon_file = os.path.join(os.path.dirname(__file__), "caduceus.png")
            if os.path.exists(icon_file):
                self.send_response(200)
                self.send_header("Content-Type", "image/png")
                self.end_headers()
                with open(icon_file, "rb") as f:
                    self.wfile.write(f.read())
                return
            self.send_response(404)
            self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8')
        
        if self.path == "/api/analyze":
            try:
                data = json.loads(body)
                text = data.get("text", "")
                result = analyze_report(text)
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(result).encode("utf-8"))
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))

        elif self.path == "/api/parse_pdf":
            try:
                data = json.loads(body)
                pdf_b64 = data.get("pdf_base64", "")
                pdf_bytes = base64.b64decode(pdf_b64)
                extracted_text = extract_text_from_pdf(pdf_bytes)
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"text": extracted_text}).encode("utf-8"))
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))

def run(port=8501):
    server = HTTPServer(('', port), ServerHandler)
    url = f"http://localhost:{port}"
    print(f"\n=======================================================")
    print(f" RadioNLP Dashboard is READY!")
    print(f" Opening in your web browser: {url}")
    print(f"=======================================================\n")
    try:
        webbrowser.open(url)
    except Exception:
        pass
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.server_close()

if __name__ == "__main__":
    run(8501)
