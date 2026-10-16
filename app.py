"""
RadioNLP Clinical Extraction Application Entry Point.
Starts the HTTP server for local or cloud environments.
"""
import os
import sys

# Ensure src is in python path
SRC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src")
if SRC_DIR not in sys.path:
    sys.path.append(SRC_DIR)

from app_server import run

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8501))
    run(port)
