"""
RadioNLP Clinical Decision Support System - Vercel Serverless Entry Point
"""

import os
import sys
import json
import base64
import io
from flask import Flask, request, jsonify, send_file, Response
import pdfplumber

# Dynamically locate project root
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(ROOT_DIR, "src")
if SRC_DIR not in sys.path:
    sys.path.append(SRC_DIR)

from inference_engine import analyze_report

app = Flask(__name__)

INDEX_HTML_PATH = os.path.join(SRC_DIR, "index.html")
CADUCEUS_PATH = os.path.join(SRC_DIR, "caduceus.png")

@app.route("/", methods=["GET"])
@app.route("/index.html", methods=["GET"])
def home():
    if os.path.exists(INDEX_HTML_PATH):
        with open(INDEX_HTML_PATH, "r", encoding="utf-8") as f:
            return Response(f.read(), mimetype="text/html")
    return "Clinical Dashboard index.html not found.", 404

@app.route("/src/caduceus.png", methods=["GET"])
@app.route("/caduceus.png", methods=["GET"])
def caduceus():
    if os.path.exists(CADUCEUS_PATH):
        return send_file(CADUCEUS_PATH, mimetype="image/png")
    return "", 404

@app.route("/api/analyze", methods=["POST"])
def analyze():
    try:
        data = request.get_json(force=True, silent=True) or {}
        text = data.get("text", "")
        if not text:
            return jsonify({"error": "No report text provided."}), 400
        result = analyze_report(text)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/parse_pdf", methods=["POST"])
def parse_pdf():
    try:
        data = request.get_json(force=True, silent=True) or {}
        pdf_b64 = data.get("pdf_base64", "")
        if not pdf_b64:
            return jsonify({"error": "Empty PDF payload."}), 400
        pdf_bytes = base64.b64decode(pdf_b64)
        
        text_parts = []
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            for page in pdf.pages:
                txt = page.extract_text()
                if txt and len(txt.strip()) > 10:
                    text_parts.append(txt.strip())
        
        extracted_text = "\n\n".join(text_parts).strip()
        return jsonify({"text": extracted_text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Vercel entrypoint is the app WSGI instance
handler = app

if __name__ == "__main__":
    app.run(port=8501, debug=True)
