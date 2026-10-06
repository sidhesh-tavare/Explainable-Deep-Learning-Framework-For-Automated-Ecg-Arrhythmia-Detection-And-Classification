# Scope v4: solid but manageable

Idea: the simple pipeline from v3, plus **three small upgrades** that make the project look like a proper "framework" rather than "I trained a CNN". Each upgrade costs about a week and can be dropped on its own if time runs out.

**Title (official, unchanged):** *Explainable Deep Learning Framework for Automated ECG Arrhythmia Detection and Classification*

---

## The framework

```
                MIT-BIH (+ NSTDB noise)
                         |
     filter -> beats around R peak -> + RR-interval features
                         |
            CNN  vs  CNN-LSTM (+RR)   ->  N / S / V / F
                         |
        +----------------+-----------------+
        v                v                 v
  Evaluation       Explainability      Robustness
  random split     Grad-CAM + SHAP     F1 vs noise level
  + DS1/DS2        + 2 simple checks   + heatmap stability
        \                |                 /
         +------ Streamlit demo dashboard -+
```

## Core (same as v3, slightly upgraded)
| Part | What we do |
|---|---|
| Data | MIT-BIH, lead MLII, 4 AAMI classes (N, S, V, F), paced records removed |
| Preprocessing | Band-pass 0.5–40 Hz; annotation R peaks; 252-sample beats; z-score |
| **RR features** (new, ~10 lines) | Previous and next RR interval fed into the model alongside the beat. Helps S beats, which are defined by timing ([22] p.4, p.8) |
| Models | Plain CNN (baseline) vs CNN-LSTM + RR (proposed) |
| Imbalance | Class-weighted loss |
| Evaluation | Random 80/20 split **and** inter-patient DS1/DS2; confusion matrix, per-class precision/recall/F1, macro-F1 |
| Explainability | **Grad-CAM and SHAP** (both via Captum), shown side by side per class |

## Upgrade A: "Are the explanations sensible?" (2 simple checks)
Turns pictures into numbers, so the "explainable" part has results, not just figures.
1. **Region check:** what % of the heatmap falls on the P wave, QRS complex and T wave, per class. Expectation: V beats → mostly QRS; S beats → more P wave / timing. One table.
2. **Deletion check:** blank out the 10% of samples the heatmap rates most important and see how much the model's confidence drops; compare with blanking 10% at random. If the heatmap is meaningful, the drop is much bigger. One bar chart.

## Upgrade B: Noise robustness
Real ECGs are noisy; most papers only test clean data.
- Add real **muscle-artefact noise** from the MIT-BIH Noise Stress Test Database to the test beats at 3 levels (SNR 18, 6, 0 dB).
- Plot **F1 vs noise level** for CNN vs CNN-LSTM.
- Bonus (few lines once noise exists): **heatmap stability**, i.e. correlation between the heatmap of the clean beat and of the noisy beat. *None of the 37 reviewed papers measures this*, so it gives you a novelty line for the viva.

## Upgrade C: Demo dashboard (Streamlit)
A small web page: choose a record and beat (optionally add noise) → shows the ECG, predicted class with confidence, and the Grad-CAM/SHAP heatmap. It makes a strong impression at the evaluation and needs no new ML.

---

## Dropped → Future Work
External dataset (INCART), uncertainty estimation (MC dropout), Pan-Tompkins R-peak detection, clinician evaluation, full ablation study.

## If time runs short, drop in this order
1. Heatmap stability (bonus in B)
2. Upgrade C (demo)
3. Upgrade B (noise)
4. Deletion check (A2)

The core + Upgrade A alone is already a decent project.
