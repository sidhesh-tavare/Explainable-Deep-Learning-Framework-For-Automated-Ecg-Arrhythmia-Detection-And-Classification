# Scope v3: the simple, safe version

Goal: a **complete, working, well-explained** project that passes comfortably. No new research claims, just a clean standard pipeline done properly, plus explainability.

**Title (keep the official one):** *Explainable Deep Learning Framework for Automated ECG Arrhythmia Detection and Classification*

---

## What we build (that's all of it)

```
MIT-BIH  ->  filter  ->  cut beats around R peak  ->  CNN-LSTM  ->  N / S / V / F
                                                          |
                                                          v
                                               Grad-CAM heatmap on the beat
```

| Part | What we do | Effort |
|---|---|---|
| Data | MIT-BIH Arrhythmia DB, lead MLII, 4 AAMI classes (N, S, V, F) | Low |
| Preprocessing | Band-pass filter 0.5–40 Hz; use the annotation R-peak positions; 252-sample beat windows; z-score | Low |
| Split | **Main result:** standard random 80/20 beat split (what most papers do, gives high accuracy). **Plus one extra table:** inter-patient DS1/DS2 (same code, different record lists). | Low (the split is just a list) |
| Model | One CNN-LSTM. A plain CNN as the comparison baseline. | Medium |
| Imbalance | Class-weighted loss | Low |
| Evaluation | Accuracy, confusion matrix, per-class precision / recall / F1, macro-F1 | Low |
| Explainability | **Grad-CAM** heatmaps overlaid on example beats for each class; short discussion of whether they highlight QRS / P wave where expected | Low–Medium |
| Optional extra | **SHAP** on the same beats (a few lines with Captum), shown side by side with Grad-CAM | Low |
| Optional demo | A small Streamlit page: pick a record → shows predicted class + heatmap. Examiners like a live demo. | Medium |

## Why two splits?
- The random split gives the "headline" accuracy (~97–99% is typical), so the results look good.
- The DS1/DS2 table costs almost nothing extra. It lets you say in the viva: *"I know random splits are optimistic; on unseen patients performance drops, especially for S and F, which matches the literature ([10] p.16, [15] p.1)."* Examiners reward knowing this, and it protects you if they ask about data leakage.

## Dropped (mention as Future Work in the report)
- Explanation metrics (faithfulness, consistency, etc.)
- Noise robustness (NSTDB)
- External dataset (INCART)
- Uncertainty (MC dropout)
- Pan-Tompkins R-peak detection
- Clinician evaluation

These make a good-looking "Future Work" section, because they come straight from the literature gaps already written in the study guide (§4.2).

## Fallbacks if things go wrong
| Problem | Do this |
|---|---|
| CNN-LSTM won't train well | Use just the CNN; it's enough |
| Grad-CAM code is fiddly | Use Captum's `LayerGradCam`; if still stuck, use simple saliency (`captum.attr.Saliency`) |
| DS1/DS2 results look bad | That's expected; report them honestly in one table and discuss |
| Short on time | Skip SHAP and the demo |
