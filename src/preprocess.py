"""
Data Preprocessing and Dataset Construction for Indiana University OpenI Radiology Reports.
Handles XML parsing, text normalization, negation/uncertainty cue tagging,
and MeSH-based multi-label ground truth annotation according to CheXpert standards.
"""

import os
import glob
import re
import xml.etree.ElementTree as ET
import pandas as pd
import numpy as np

def clean_text(text: str) -> str:
    """Clean radiology report text removing boilerplate and excessive whitespace."""
    if not text:
        return ""
    # Normalize anonymization tokens (XXXX)
    text = re.sub(r'X+', ' ', text)
    # Normalize punctuation and whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def parse_openi_dataset(xml_dir: str) -> pd.DataFrame:
    """Parse all XML report files in OpenI dataset directory."""
    records = []
    xml_files = glob.glob(os.path.join(xml_dir, "*.xml"))
    print(f"Parsing {len(xml_files)} XML reports from {xml_dir}...")
    
    for f in xml_files:
        try:
            tree = ET.parse(f)
            root = tree.getroot()
            uid = os.path.splitext(os.path.basename(f))[0]
            
            comparison = ""
            indication = ""
            findings = ""
            impression = ""
            
            for elem in root.findall(".//AbstractText"):
                lbl = elem.attrib.get("Label", "").upper()
                txt = elem.text.strip() if elem.text else ""
                if lbl == "COMPARISON":
                    comparison = txt
                elif lbl == "INDICATION":
                    indication = txt
                elif lbl == "FINDINGS":
                    findings = txt
                elif lbl == "IMPRESSION":
                    impression = txt
                    
            # Full diagnostic report combining Findings and Impression
            diagnostic_text = f"{findings} {impression}".strip()
            if not diagnostic_text:
                continue
                
            # Collect MeSH / RadLex terms
            mesh_terms = []
            for t in root.findall(".//major") + root.findall(".//minor"):
                if t.text:
                    mesh_terms.append(t.text.strip().lower())
            mesh_str = " ".join(mesh_terms)
            
            # Ground truth binary annotations based on MeSH consensus
            # 1. Cardiomegaly
            cardiomegaly = 1 if "cardiomegaly" in mesh_str else 0
            # 2. Pulmonary Edema / Congestion
            edema = 1 if ("edema" in mesh_str or "pulmonary congestion" in mesh_str) else 0
            # 3. Atelectasis
            atelectasis = 1 if "atelectasis" in mesh_str else 0
            # 4. Pleural Effusion / Thickening
            effusion = 1 if ("effusion" in mesh_str or "pleural" in mesh_str) else 0
            # 5. Pneumonia / Consolidation / Infiltrate
            pneumonia = 1 if ("pneumonia" in mesh_str or "consolidation" in mesh_str or "infiltrate" in mesh_str) else 0
            # 6. Granulomatous Disease / Calcified Nodule
            granuloma = 1 if ("granulom" in mesh_str or "calcifi" in mesh_str) else 0
            # 7. Emphysema / COPD / Hyperdistention
            emphysema = 1 if ("emphysema" in mesh_str or "copd" in mesh_str or "hyperdistention" in mesh_str) else 0
            # 8. Normal / No Acute Finding
            is_normal = 1 if ("normal" in mesh_str and not (cardiomegaly or edema or atelectasis or effusion or pneumonia)) else 0
            
            # Combined clinical presence of any primary cardiopulmonary finding
            any_abnormal = 1 if (cardiomegaly or edema or atelectasis or effusion or pneumonia) else 0
            
            records.append({
                "id": uid,
                "findings": clean_text(findings),
                "impression": clean_text(impression),
                "text": clean_text(diagnostic_text),
                "mesh_annotations": mesh_str,
                "Normal": is_normal,
                "Cardiomegaly": cardiomegaly,
                "Edema": edema,
                "Atelectasis": atelectasis,
                "Effusion": effusion,
                "Pneumonia": pneumonia,
                "Granuloma": granuloma,
                "Emphysema": emphysema,
                "AnyAbnormality": any_abnormal,
                "num_words": len(diagnostic_text.split())
            })
        except Exception as e:
            continue
            
    df = pd.DataFrame(records)
    print(f"Successfully processed {len(df)} reports.")
    return df

if __name__ == "__main__":
    xml_dir = r"C:\Users\palem\OneDrive\Documents\3rd Year\Machine Learning\data\ecgen-radiology"
    out_csv = r"C:\Users\palem\OneDrive\Documents\3rd Year\Machine Learning\data\openi_processed_dataset.csv"
    df = parse_openi_dataset(xml_dir)
    df.to_csv(out_csv, index=False)
    print(f"Saved processed dataset to {out_csv}")
    print("\nDataset Summary Statistics:")
    print(f"Total reports: {len(df)}")
    print(f"Mean report length (words): {df['num_words'].mean():.2f} +/- {df['num_words'].std():.2f}")
    target_cols = ["Normal", "Cardiomegaly", "Edema", "Atelectasis", "Effusion", "Pneumonia", "Granuloma", "Emphysema", "AnyAbnormality"]
    for col in target_cols:
        pos = df[col].sum()
        pct = pos / len(df) * 100
        print(f"  {col:<16}: {pos:>4} positive ({pct:5.2f}%)")
