"""
Generates publication-quality charts and plots for Phase 3 ML results:
1. ROC Curves comparison for all findings
2. Confusion matrix & diagnostic metrics comparison across models
3. Comparison against Base Paper benchmarks (Pooled Sensitivity, Specificity, AUC, DOR)
4. Forest plot of individual finding sensitivities & specificities
"""

import os
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Set style
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = 'Arial'
plt.rcParams['font.family'] = 'sans-serif'

results_dir = r"C:\Users\palem\OneDrive\Documents\3rd Year\Machine Learning\results"
fig_dir = r"C:\Users\palem\OneDrive\Documents\3rd Year\Machine Learning\figures"
os.makedirs(fig_dir, exist_ok=True)

with open(os.path.join(results_dir, "model_comparison_results.json"), "r") as f:
    model_results = json.load(f)

with open(os.path.join(results_dir, "roc_curves_data.json"), "r") as f:
    roc_data = json.load(f)

# -------------------------------------------------------------
# FIGURE 1: Benchmark Comparison vs Base Paper Meta-Analysis
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(10, 6))

metrics = ['Sensitivity (%)', 'Specificity (%)', 'AUC (AUROC x100)']
base_paper_vals = [91.0, 96.0, 98.0]
base_paper_ci = [(87.0, 93.0), (93.0, 97.0), (96.0, 99.0)]

lr_vals = [
    model_results["Logistic Regression (L2)"]["micro_metrics"]["sensitivity"] * 100,
    model_results["Logistic Regression (L2)"]["micro_metrics"]["specificity"] * 100,
    model_results["Logistic Regression (L2)"]["macro_metrics"]["auroc"] * 100
]

gb_vals = [
    model_results["Gradient Boosting"]["micro_metrics"]["sensitivity"] * 100,
    model_results["Gradient Boosting"]["micro_metrics"]["specificity"] * 100,
    model_results["Gradient Boosting"]["macro_metrics"]["auroc"] * 100
]

svm_vals = [
    model_results["Linear SVM (Calibrated)"]["micro_metrics"]["sensitivity"] * 100,
    model_results["Linear SVM (Calibrated)"]["micro_metrics"]["specificity"] * 100,
    model_results["Linear SVM (Calibrated)"]["macro_metrics"]["auroc"] * 100
]

x = np.arange(len(metrics))
width = 0.2

rects1 = ax.bar(x - 1.5*width, base_paper_vals, width, label='Base Paper (Meta-Analysis Pooled)', color='#1f77b4', alpha=0.85, edgecolor='black')
rects2 = ax.bar(x - 0.5*width, lr_vals, width, label='Our Logistic Regression (L2)', color='#2ca02c', alpha=0.85, edgecolor='black')
rects3 = ax.bar(x + 0.5*width, svm_vals, width, label='Our Linear SVM (Calibrated)', color='#ff7f0e', alpha=0.85, edgecolor='black')
rects4 = ax.bar(x + 1.5*width, gb_vals, width, label='Our Gradient Boosting', color='#d62728', alpha=0.85, edgecolor='black')

# Annotations
for rects in [rects1, rects2, rects3, rects4]:
    for rect in rects:
        height = rect.get_height()
        ax.annotate(f'{height:.1f}%',
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),  # 3 points vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=9, fontweight='bold')

ax.set_ylabel('Metric Value (%)', fontsize=12, fontweight='bold')
ax.set_title('Our Model Validation vs. Base Paper Meta-Analysis Pooled Benchmarks', fontsize=14, fontweight='bold', pad=15)
ax.set_xticks(x)
ax.set_xticklabels(metrics, fontsize=11, fontweight='bold')
ax.set_ylim(70, 105)
ax.legend(loc='lower right', frameon=True, fontsize=10)
plt.tight_layout()
fig.savefig(os.path.join(fig_dir, "benchmark_comparison.png"), dpi=300)
plt.close()
print("Saved benchmark_comparison.png")

# -------------------------------------------------------------
# FIGURE 2: Multi-Label ROC Curves (Logistic Regression)
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(9, 7))
lr_roc = roc_data["Logistic Regression (L2)"]
colors = sns.color_palette("tab10", len(lr_roc))

for idx, (finding, (fpr, tpr, auroc)) in enumerate(lr_roc.items()):
    ax.plot(fpr, tpr, color=colors[idx], lw=2, label=f'{finding} (AUC = {auroc:.3f})')

ax.plot([0, 1], [0, 1], 'k--', lw=1.5, alpha=0.7, label='Random Chance (AUC = 0.50)')
ax.set_xlim([-0.02, 1.0])
ax.set_ylim([0.0, 1.03])
ax.set_xlabel('False Positive Rate (1 - Specificity)', fontsize=12, fontweight='bold')
ax.set_ylabel('True Positive Rate (Sensitivity)', fontsize=12, fontweight='bold')
ax.set_title('Receiver Operating Characteristic (ROC) Curves by Target Finding\n(Logistic Regression Pipeline)', fontsize=13, fontweight='bold', pad=12)
ax.legend(loc="lower right", fontsize=10, frameon=True)
plt.tight_layout()
fig.savefig(os.path.join(fig_dir, "roc_curves_multilabel.png"), dpi=300)
plt.close()
print("Saved roc_curves_multilabel.png")

# -------------------------------------------------------------
# FIGURE 3: Diagnostic Odds Ratio (DOR) Comparison Across Models
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(8, 5))
model_names = list(model_results.keys())
micro_dors = [model_results[m]["micro_metrics"]["dor"] for m in model_names]
base_paper_dor = 220.0

colors = ['#2ca02c', '#ff7f0e', '#7f7f7f', '#d62728']
bars = ax.barh(model_names, micro_dors, color=colors, alpha=0.85, edgecolor='black', height=0.55)
ax.axvline(base_paper_dor, color='blue', linestyle='--', linewidth=2, label=f'Base Paper Benchmark DOR = {base_paper_dor:.0f}')

for bar in bars:
    width = bar.get_width()
    ax.annotate(f'DOR = {width:.1f}',
                xy=(width, bar.get_y() + bar.get_height() / 2),
                xytext=(5, 0),
                textcoords="offset points",
                ha='left', va='center', fontsize=10, fontweight='bold')

ax.set_xlabel('Diagnostic Odds Ratio (DOR) [Higher is Better]', fontsize=11, fontweight='bold')
ax.set_title('Diagnostic Odds Ratio (Micro-Pooled) Across Evaluated Models', fontsize=13, fontweight='bold', pad=12)
ax.set_xlim(0, 950)
ax.legend(loc='lower right', frameon=True, fontsize=10)
plt.tight_layout()
fig.savefig(os.path.join(fig_dir, "dor_comparison.png"), dpi=300)
plt.close()
print("Saved dor_comparison.png")

# -------------------------------------------------------------
# FIGURE 4: Per-Finding Sensitivity & Specificity Heatmap / Matrix
# -------------------------------------------------------------
findings = list(model_results["Logistic Regression (L2)"]["per_finding"].keys())
models = list(model_results.keys())

sens_matrix = np.zeros((len(findings), len(models)))
spec_matrix = np.zeros((len(findings), len(models)))

for j, m in enumerate(models):
    for i, f in enumerate(findings):
        sens_matrix[i, j] = model_results[m]["per_finding"][f]["sensitivity"] * 100
        spec_matrix[i, j] = model_results[m]["per_finding"][f]["specificity"] * 100

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

sns.heatmap(sens_matrix, annot=True, fmt='.1f', cmap='YlGn', cbar=False,
            xticklabels=[m.split('(')[0].strip() for m in models], yticklabels=findings, ax=ax1)
ax1.set_title('Sensitivity (%) across Findings', fontsize=12, fontweight='bold')

sns.heatmap(spec_matrix, annot=True, fmt='.1f', cmap='Blues', cbar=False,
            xticklabels=[m.split('(')[0].strip() for m in models], yticklabels=findings, ax=ax2)
ax2.set_title('Specificity (%) across Findings', fontsize=12, fontweight='bold')

plt.tight_layout()
fig.savefig(os.path.join(fig_dir, "finding_performance_heatmap.png"), dpi=300)
plt.close()
print("Saved finding_performance_heatmap.png")
