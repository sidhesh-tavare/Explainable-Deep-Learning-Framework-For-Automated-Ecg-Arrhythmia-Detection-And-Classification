import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
plt.rcParams["font.family"] = "Times New Roman"
fig, ax = plt.subplots(figsize=(10, 6.2)); ax.set_xlim(0, 10); ax.set_ylim(0, 6.2); ax.axis("off")
NAVY, ORANGE, GREY = "#1F3864", "#ED7D31", "#F2F2F2"
def box(x, y, w, h, title, sub, fc=GREY, ec=NAVY, tc="#202020"):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.08", fc=fc, ec=ec, lw=1.5))
    ax.text(x+w/2, y+h*0.66, title, ha="center", va="center", fontsize=11.5, weight="bold", color=tc)
    ax.text(x+w/2, y+h*0.30, sub, ha="center", va="center", fontsize=9.2, color=tc)
def arrow(x1, y1, x2, y2):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1), arrowprops=dict(arrowstyle="-|>", color="#404040", lw=1.4))
# row 1: data + preprocessing
box(0.2, 4.9, 2.2, 1.0, "ECG data", "MIT-BIH (MLII, 360 Hz)\n+ NSTDB noise")
box(2.9, 4.9, 2.2, 1.0, "Pre-processing", "Band-pass 0.5–40 Hz,\nbeats around R peak, z-score")
box(5.6, 4.9, 1.8, 1.0, "RR features", "previous / next RR\n(normalised)")
box(7.9, 4.9, 1.9, 1.0, "Data split", "intra-patient 80/20\n+ inter-patient DS1/DS2")
for a, b in [(2.4, 2.9), (5.1, 5.6), (7.4, 7.9)]: arrow(a, 5.4, b, 5.4)
# row 2: classifier
box(2.5, 3.2, 4.6, 1.0, "Classifier", "1D CNN (baseline) vs CNN-LSTM + RR (proposed)\nclass-weighted loss", fc=NAVY, tc="white")
arrow(8.85, 4.9, 7.0, 3.95)
box(7.4, 3.2, 2.4, 1.0, "Prediction", "N / S / V / F")
arrow(7.0, 3.7, 7.4, 3.7)
# row 3: three evaluation branches
box(0.2, 1.4, 3.0, 1.1, "Classification evaluation", "confusion matrix, per-class P/R/F1,\nmacro-F1")
box(3.5, 1.4, 3.0, 1.1, "Explainability", "Grad-CAM + SHAP heatmaps;\nregion share (P/QRS/T), deletion test", fc="#FCE4D6", ec=ORANGE)
box(6.8, 1.4, 3.0, 1.1, "Robustness", "macro-F1 vs SNR (18, 6, 0 dB);\nheatmap stability (clean vs noisy)")
for x in (1.7, 5.0, 8.3): arrow(5.0, 3.2, x, 2.5)
box(2.6, 0.1, 4.8, 0.85, "Demo dashboard (Streamlit)", "ECG beat + prediction + heatmap", fc="white")
for x in (1.7, 5.0, 8.3): arrow(x, 1.4, 5.0, 0.95)
fig.savefig(sys.argv[1], dpi=220, bbox_inches="tight", facecolor="white")
