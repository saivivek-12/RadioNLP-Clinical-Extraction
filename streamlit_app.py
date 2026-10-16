"""
RadioNLP Clinical Decision Support System
Pixel-Perfect Streamlit Cloud UI matching the manual Human-Crafted Design
"""

import os
import sys
import io
import re
import json
import base64
import streamlit as st
import pdfplumber

# Ensure src is on sys.path
SRC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src")
if SRC_DIR not in sys.path:
    sys.path.append(SRC_DIR)

from inference_engine import analyze_report

# Page Config
st.set_page_config(
    page_title="RadioNLP: Clinical Decision Support & Extraction System",
    page_icon="⚕️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Load Caduceus logo as base64
CADUCEUS_PATH = os.path.join(SRC_DIR, "caduceus.png")
if os.path.exists(CADUCEUS_PATH):
    with open(CADUCEUS_PATH, "rb") as f:
        CADUCEUS_B64 = base64.b64encode(f.read()).decode("utf-8")
else:
    CADUCEUS_B64 = ""

# Inject custom CSS matching index.html exactly
st.markdown(f"""
<style>
    /* Hide Streamlit default chrome & margins */
    #MainMenu {{ visibility: hidden; }}
    footer {{ visibility: hidden; }}
    header {{ visibility: hidden; }}
    .stApp > header {{ display: none; }}
    .block-container {{
        padding-top: 0rem !important;
        padding-bottom: 2rem !important;
        padding-left: 0rem !important;
        padding-right: 0rem !important;
        max-width: 100% !important;
    }}
    
    :root {{
        --slate-900: #0f172a;
        --slate-800: #1e293b;
        --slate-700: #334155;
        --slate-600: #475569;
        --slate-500: #64748b;
        --slate-200: #e2e8f0;
        --slate-100: #f1f5f9;
        --slate-50:  #f8fafc;
        --border-color: #cbd5e1;
    }}

    body, .stApp {{
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif !important;
        background: #f8fafc !important;
        color: #0f172a !important;
        font-size: 13.5px !important;
    }}

    /* Top Navigation Bar */
    .top-navbar {{
        background: #DDD7CD;
        border-bottom: 1px solid #C5BEB2;
        color: #0f172a;
        padding: 14px 24px;
        width: 100%;
        margin-bottom: 20px;
        display: flex;
        align-items: center;
        gap: 14px;
    }}
    .nav-logo {{
        height: 38px;
        width: auto;
        object-fit: contain;
    }}
    .nav-title-box {{
        display: flex;
        flex-direction: column;
    }}
    .nav-title-text {{
        font-size: 16.5px;
        font-weight: 700;
        color: #0f172a;
        letter-spacing: -0.2px;
        line-height: 1.2;
    }}
    .nav-sub-text {{
        font-size: 11.5px;
        color: #555e6d;
        margin-top: 3px;
        font-weight: 500;
    }}

    /* Workspace Container */
    .workspace-wrapper {{
        max-width: 1340px;
        margin: 0 auto;
        padding: 0 16px;
    }}

    /* Panels */
    .custom-panel {{
        background: #ffffff;
        border: 1px solid #cbd5e1;
        border-radius: 6px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }}
    .panel-top-bar {{
        padding: 12px 18px;
        border-bottom: 1px solid #cbd5e1;
        background: #f8fafc;
        border-top-left-radius: 5px;
        border-top-right-radius: 5px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }}
    .panel-heading {{
        font-size: 13.5px;
        font-weight: 600;
        color: #1e293b;
        text-transform: uppercase;
        letter-spacing: 0.4px;
    }}
    .panel-pill {{
        font-size: 11px;
        padding: 2px 7px;
        border-radius: 3px;
        background: #e2e8f0;
        color: #334155;
        font-weight: 500;
    }}
    .panel-content {{
        padding: 18px;
    }}

    /* File Ingestion Box */
    .ingest-box {{
        background: #f8fafc;
        border: 1px solid #cbd5e1;
        border-radius: 4px;
        padding: 12px 14px;
        margin-bottom: 14px;
    }}
    .ingest-header-row {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 8px;
    }}
    .ingest-label {{
        font-size: 12px;
        font-weight: 600;
        color: #334155;
    }}

    /* Textarea Styling */
    .stTextArea textarea {{
        border: 1px solid #cbd5e1 !important;
        border-radius: 4px !important;
        font-size: 13px !important;
        font-family: inherit !important;
        color: #0f172a !important;
        line-height: 1.5 !important;
        background: #ffffff !important;
    }}
    .stTextArea textarea:focus {{
        border-color: #2563eb !important;
        box-shadow: 0 0 0 2px rgba(37,99,235,0.12) !important;
    }}

    /* Buttons */
    div[data-testid="stButton"] > button[kind="primary"] {{
        background: #DDD7CD !important;
        color: #0f172a !important;
        border: 1px solid #BFB7AA !important;
        font-weight: 700 !important;
        font-size: 13px !important;
        border-radius: 4px !important;
        padding: 9px 16px !important;
        width: 100% !important;
    }}
    div[data-testid="stButton"] > button[kind="primary"]:hover {{
        background: #D0C9BD !important;
        border-color: #ABA396 !important;
    }}

    div[data-testid="stButton"] > button[kind="secondary"] {{
        background: #ffffff !important;
        color: #334155 !important;
        border: 1px solid #cbd5e1 !important;
        font-weight: 500 !important;
        font-size: 13px !important;
        border-radius: 4px !important;
        padding: 9px 14px !important;
    }}
    div[data-testid="stButton"] > button[kind="secondary"]:hover {{
        background: #f1f5f9 !important;
    }}

    /* Triage Cards */
    .triage-card {{
        border: 1px solid #cbd5e1;
        border-radius: 4px;
        padding: 12px 16px;
        margin-bottom: 16px;
    }}
    .triage-waiting {{
        background: #f1f5f9;
        border-color: #cbd5e1;
        color: #475569;
    }}
    .triage-high {{
        background: #fef2f2;
        border-color: #fca5a5;
        color: #b91c1c;
    }}
    .triage-med {{
        background: #fffbeb;
        border-color: #fde68a;
        color: #b45309;
    }}
    .triage-low {{
        background: #f0fdf4;
        border-color: #86efac;
        color: #15803d;
    }}
    .triage-heading {{
        font-size: 13.5px;
        font-weight: 700;
        letter-spacing: 0.3px;
    }}
    .triage-sub {{
        font-size: 11.5px;
        font-weight: 400;
        opacity: 0.9;
        margin-top: 2px;
    }}

    /* Table */
    .findings-table {{
        width: 100%;
        border-collapse: collapse;
        font-size: 12.5px;
        border: 1px solid #cbd5e1;
    }}
    .findings-table th {{
        background: #f8fafc;
        color: #334155;
        text-align: left;
        padding: 9px 12px;
        font-weight: 600;
        border-bottom: 1px solid #cbd5e1;
        font-size: 11.5px;
        text-transform: uppercase;
        letter-spacing: 0.4px;
    }}
    .findings-table td {{
        padding: 10px 12px;
        border-bottom: 1px solid #f1f5f9;
        vertical-align: middle;
    }}
    .findings-table tr:hover {{
        background: #f8fafc;
    }}
    .finding-title {{
        font-weight: 600;
        color: #0f172a;
    }}
    .finding-sub {{
        font-size: 10.5px;
        color: #64748b;
    }}

    /* Badges */
    .badge-status {{
        display: inline-block;
        padding: 2px 8px;
        border-radius: 3px;
        font-size: 10.5px;
        font-weight: 700;
        letter-spacing: 0.4px;
    }}
    .status-detected {{
        background: #fee2e2;
        color: #b91c1c;
        border: 1px solid #fca5a5;
    }}
    .status-absent {{
        background: #f1f5f9;
        color: #64748b;
        border: 1px solid #e2e8f0;
    }}

    /* Meter Progress Bar */
    .meter-container {{
        width: 90px;
        height: 6px;
        background: #e2e8f0;
        border-radius: 2px;
        overflow: hidden;
        display: inline-block;
        vertical-align: middle;
        margin-right: 6px;
    }}
    .meter-bar {{
        height: 100%;
        border-radius: 2px;
    }}
    .meter-red {{ background: #ef4444; }}
    .meter-green {{ background: #10b981; }}

    /* Cue Tag */
    .cue-tag {{
        display: inline-block;
        background: #f1f5f9;
        border: 1px solid #cbd5e1;
        padding: 1px 6px;
        border-radius: 3px;
        font-size: 10.5px;
        color: #0369a1;
        margin: 2px;
        font-family: monospace;
    }}
</style>
""", unsafe_allow_html=True)

# Render Navbar
logo_src = f"data:image/png;base64,{CADUCEUS_B64}" if CADUCEUS_B64 else ""
logo_img_tag = f'<img class="nav-logo" src="{logo_src}" alt="Caduceus">' if logo_src else '⚕️'

st.markdown(f"""
<div class="top-navbar">
    {logo_img_tag}
    <div class="nav-title-box">
        <div class="nav-title-text">RadioNLP Clinical Decision Support System</div>
        <div class="nav-sub-text">Multi-Label Thoracic Pathology Extraction Pipeline</div>
    </div>
</div>
""", unsafe_allow_html=True)

# Session State
if "report_text" not in st.session_state:
    st.session_state.report_text = ""
if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None

# Main Two-Column Layout
col_left, col_right = st.columns([440, 700], gap="large")

with col_left:
    st.markdown("""
    <div class="custom-panel">
        <div class="panel-top-bar">
            <span class="panel-heading">1. DOCUMENT INGESTION & NARRATIVE INPUT</span>
            <span class="panel-pill">Input Pipeline</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Ingestion box
    st.markdown("""
    <div style="background: #f8fafc; border: 1px solid #cbd5e1; border-radius: 4px; padding: 10px 14px 4px 14px; margin-bottom: 12px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
            <span style="font-size: 12px; font-weight: 600; color: #334155;">Clinical Document File Source:</span>
            <span style="font-size: 10.5px; color: #64748b;">Supports .pdf, .xml, .txt, .csv</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader(
        "Upload report file",
        type=["pdf", "xml", "txt", "csv"],
        label_visibility="collapsed"
    )
    
    if uploaded_file is not None:
        filename = uploaded_file.name.lower()
        if filename.endswith(".pdf"):
            try:
                with pdfplumber.open(uploaded_file) as pdf:
                    pages = [p.extract_text() for p in pdf.pages if p.extract_text()]
                    text_extracted = "\n\n".join(pages).strip()
                    if text_extracted:
                        st.session_state.report_text = text_extracted
            except Exception as e:
                st.error(f"Error parsing PDF: {e}")
        else:
            raw_text = uploaded_file.read().decode("utf-8", errors="ignore")
            st.session_state.report_text = raw_text

    # Word & Char Count
    current_text = st.session_state.report_text
    char_count = len(current_text)
    word_count = len(current_text.strip().split()) if current_text.strip() else 0

    st.markdown(f"""
    <div style="display: flex; justify-content: space-between; font-size: 11.5px; color: #64748b; margin-top: 10px; margin-bottom: 4px;">
        <span>Free-Text Clinical Report / Impression:</span>
        <span>{char_count} chars | {word_count} words</span>
    </div>
    """, unsafe_allow_html=True)

    text_input = st.text_area(
        "Narrative",
        value=st.session_state.report_text,
        height=260,
        placeholder="Enter or paste radiology report narrative here (e.g. Findings, Impression)... Or select a report file above to ingest automatically.",
        label_visibility="collapsed"
    )
    st.session_state.report_text = text_input

    # Action Toolbar
    btn_col1, btn_col2 = st.columns([4, 1])
    with btn_col1:
        run_nlp = st.button("Extract Findings (Run NLP)", type="primary", use_container_width=True)
    with btn_col2:
        clear_btn = st.button("Clear", type="secondary", use_container_width=True)

    if clear_btn:
        st.session_state.report_text = ""
        st.session_state.analysis_result = None
        st.rerun()

    if run_nlp and text_input.strip():
        with st.spinner("Executing Calibrated NLP Engine..."):
            st.session_state.analysis_result = analyze_report(text_input.strip())

with col_right:
    # Right Panel Header
    res = st.session_state.analysis_result
    num_detected = len(res["abnormalities_found"]) if res else 0
    badge_label = f"{num_detected} Pathologies Detected" if res else "0 Pathologies Detected"

    st.markdown(f"""
    <div class="custom-panel">
        <div class="panel-top-bar">
            <span class="panel-heading">2. DIAGNOSTIC TRIAGE & EXTRACTED PATHOLOGIES</span>
            <span class="panel-pill">{badge_label}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Triage Alert Box
    if not res:
        st.markdown("""
        <div class="triage-card triage-waiting">
            <div>
                <div class="triage-heading">TRIAGE: AWAITING REPORT INPUT</div>
                <div class="triage-sub">Provide report text on the left to compute clinical urgency level.</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        urgency = res["triage_urgency"]
        if "HIGH" in urgency:
            triage_class = "triage-high"
            triage_desc = "Actionable thoracic abnormalities detected requiring prompt medical review."
        elif "MEDIUM" in urgency:
            triage_class = "triage-med"
            triage_desc = "Cardiopulmonary pathology observed. Routine clinical correlation advised."
        else:
            triage_class = "triage-low"
            triage_desc = "No high-urgency or acute thoracic abnormalities detected."

        st.markdown(f"""
        <div class="triage-card {triage_class}">
            <div>
                <div class="triage-heading">TRIAGE: {urgency}</div>
                <div class="triage-sub">{triage_desc}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Findings Table
    if not res:
        st.markdown("""
        <table class="findings-table">
            <thead>
                <tr>
                    <th style="width: 24%;">Thoracic Finding</th>
                    <th style="width: 18%;">Status</th>
                    <th style="width: 26%;">Confidence Metric</th>
                    <th>Influential Text Evidence</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td colspan="4" style="text-align: center; color: #64748b; padding: 35px 15px;">
                        No analysis generated yet. Ingest a report or enter text to populate findings.
                    </td>
                </tr>
            </tbody>
        </table>
        """, unsafe_allow_html=True)
    else:
        rows_html = []
        for finding, detail in res["findings_detail"].items():
            is_present = detail["present"]
            conf = detail["confidence_percent"]
            prob = detail["probability"]
            pos_cues = detail["positive_evidence"]
            neg_cues = detail["negative_evidence"]

            # Subtitles for findings
            sub_titles = {
                "Normal": "Clear Cardiopulmonary Baseline",
                "Cardiomegaly": "Enlarged Cardiac Silhouette",
                "Edema": "Pulmonary Interstitial / Alveolar Fluid",
                "Atelectasis": "Partial Volume Loss / Airspace Collapse",
                "Effusion": "Pleural Fluid Accumulation",
                "Pneumonia": "Consolidation / Airspace Infiltrate",
                "Granuloma": "Calcified Inflammatory Nodule",
                "Emphysema": "Chronic Hyperinflation / Bullous Changes"
            }
            f_sub = sub_titles.get(finding, "Thoracic Finding Extraction")

            # Status Badge
            if is_present:
                status_html = '<span class="badge-status status-detected">DETECTED</span>'
            else:
                status_html = '<span class="badge-status status-absent">NOT DETECTED</span>'

            # Meter Bar
            meter_class = "meter-red" if (is_present and finding != "Normal") else "meter-green"
            meter_width = min(100, max(4, int(conf)))
            meter_html = f"""
            <div class="meter-container">
                <div class="meter-bar {meter_class}" style="width: {meter_width}%;"></div>
            </div>
            <span style="font-weight: 600; font-size: 11.5px;">{conf:.1f}%</span>
            """

            # Evidence Chips
            cues_html = ""
            if pos_cues:
                for c in pos_cues[:2]:
                    cues_html += f'<span class="cue-tag" style="background: #fee2e2; color: #991b1b; border-color: #fca5a5;">+{c}</span>'
            if neg_cues:
                for c in neg_cues[:1]:
                    cues_html += f'<span class="cue-tag" style="background: #f1f5f9; color: #475569;">-{c}</span>'
            if not cues_html:
                cues_html = '<span style="color: #94a3b8; font-size: 11px;">None</span>'

            row = f"""
            <tr>
                <td>
                    <div class="finding-title">{finding}</div>
                    <div class="finding-sub">{f_sub}</div>
                </td>
                <td>{status_html}</td>
                <td>{meter_html}</td>
                <td>{cues_html}</td>
            </tr>
            """
            rows_html.append(row)

        table_content = "\n".join(rows_html)
        st.markdown(f"""
        <table class="findings-table">
            <thead>
                <tr>
                    <th style="width: 24%;">Thoracic Finding</th>
                    <th style="width: 18%;">Status</th>
                    <th style="width: 26%;">Confidence Metric</th>
                    <th>Influential Text Evidence</th>
                </tr>
            </thead>
            <tbody>
                {table_content}
            </tbody>
        </table>
        """, unsafe_allow_html=True)

        # Download JSON Button
        json_str = json.dumps(res, indent=2)
        st.markdown("<div style='display: flex; justify-content: flex-end; margin-top: 15px;'>", unsafe_allow_html=True)
        st.download_button(
            label="Download Output JSON",
            data=json_str,
            file_name="radionlp_clinical_extraction.json",
            mime="application/json"
        )
        st.markdown("</div>", unsafe_allow_html=True)
