"""
Standalone Command-Line Predictor for Live Viva Demonstrations.
Allows typing/pasting text, or passing a dataset CSV file to predict outputs.
Usage:
  1. Interactive mode: python predict.py
  2. Batch file mode:  python predict.py --input sample.csv --output results.csv
"""

import sys
import os
import argparse
import pandas as pd

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))
from inference_engine import analyze_report

def interactive_mode():
    print("=" * 75)
    print("   RadioNLP: Clinical Information Extraction Inference Tool")
    print("=" * 75)
    print("Type or paste any radiology report text below and press Enter twice.")
    print("Type 'exit' to quit.\n")
    
    presets = [
        ("Normal Report", "Both lungs are clear and expanded. Heart and mediastinum normal. No active disease."),
        ("Cardiomegaly + Edema", "The cardiac silhouette is moderately enlarged with prominence of pulmonary vasculature. Mild interstitial pulmonary edema. No pneumothorax."),
        ("Pleural Effusion", "Blunting of the right costophrenic angle consistent with pleural effusion. Normal cardiac contours."),
        ("Complex Negation", "The lungs are clear without focal consolidation, pneumothorax, or large pleural effusion.")
    ]
    
    print("Available Test Presets (Enter number 1-4 or type custom text):")
    for i, (name, txt) in enumerate(presets, 1):
        print(f"  [{i}] {name}")
    print()

    while True:
        try:
            user_input = input("Enter Preset Number (1-4) OR Custom Report Text:\n> ").strip()
            if not user_input:
                continue
            if user_input.lower() in ["exit", "quit", "q"]:
                break
                
            if user_input in ["1", "2", "3", "4"]:
                idx = int(user_input) - 1
                report_text = presets[idx][1]
                print(f"\n[Loaded Preset {user_input}: '{presets[idx][0]}']")
            else:
                report_text = user_input
                
            print("\nAnalyzing report text...")
            res = analyze_report(report_text)
            
            print("\n" + "-" * 75)
            print(f"INPUT TEXT: {res['input_text']}")
            print(f"TRIAGE LEVEL: {res['triage_urgency']}")
            print(f"DETECTED PATHOLOGIES: {res['abnormalities_found']}")
            print("-" * 75)
            print(f"{'Pathology Finding':<20} | {'Status':<10} | {'Confidence':<12} | Influential Text Cues")
            print("-" * 75)
            
            for f_name, d in res["findings_detail"].items():
                status = "DETECTED" if d["present"] else "NEGATIVE"
                conf = f"{d['confidence_percent']}%"
                cues = ", ".join(d["positive_evidence"]) if d["positive_evidence"] else "None"
                print(f"{f_name:<20} | {status:<10} | {conf:<12} | {cues}")
            print("-" * 75 + "\n")
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error during inference: {e}\n")

def batch_mode(input_file, output_file):
    print(f"Loading input file: {input_file}...")
    df = pd.read_csv(input_file)
    text_col = None
    for col in ["text", "report", "findings", "impression"]:
        if col in df.columns:
            text_col = col
            break
    if text_col is None:
        text_col = df.columns[0]
        print(f"Warning: Using first column '{text_col}' as input text.")
        
    print(f"Processing {len(df)} records using clinical NLP engine...")
    results = []
    for text in df[text_col]:
        res = analyze_report(str(text))
        row = {
            "input_text": text,
            "triage_urgency": res["triage_urgency"],
            "detected_findings": "; ".join(res["abnormalities_found"])
        }
        for f, d in res["findings_detail"].items():
            row[f"{f}_prediction"] = 1 if d["present"] else 0
            row[f"{f}_probability"] = d["probability"]
        results.append(row)
        
    out_df = pd.DataFrame(results)
    out_df.to_csv(output_file, index=False)
    print(f"Successfully saved predictions to: {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Predict findings from radiology reports")
    parser.add_argument("--input", "-i", type=str, help="Input CSV dataset file path")
    parser.add_argument("--output", "-o", type=str, default="predictions_output.csv", help="Output CSV path")
    args = parser.parse_args()
    
    if args.input:
        batch_mode(args.input, args.output)
    else:
        interactive_mode()
