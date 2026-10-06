# Scope v2: the narrowed project

## One-line idea
Papers on explainable ECG classification **show** heatmaps. We **measure** whether those heatmaps are faithful, consistent and stable under real noise, using a classifier evaluated the honest (patient-independent) way.

**Working title:** *Do ECG Arrhythmia Explanations Hold Up? Measuring the Faithfulness, Consistency and Noise-Stability of Grad-CAM and SHAP on a Patient-Independent Classifier*

(A shorter alternative if the official title can't change much: *Explainable Deep Learning for ECG Arrhythmia Classification with Quantitative Evaluation of Explanation Reliability*.)

---

## Why we narrowed it
- The old plan (Study Guide Stage 4.3 / 5.3) had three objectives plus Pan-Tompkins, INCART, 5 noise levels × 3 noise types, MC dropout, ablations and bootstrap CIs. That fills all 14 weeks with no buffer.
- The novel part is the explanation evaluation, not the classifier. In all 37 reviewed papers:
  - fewer than 10% of studies validate explanation maps against clinical structures ([12] p.40);
  - explanations are usually shown only as examples ([1] p.6, p.8; [5] p.8–9; [21] p.8; [19] p.11);
  - **no paper measures explanation stability under noise** (Study Guide §4.2, Gap 3).
- A weak S/F recall doesn't threaten this claim, because under DS1/DS2 it is expected ([15] p.16–17).

---

## Objectives (2 instead of 3)

### O1: Honest patient-independent baseline (the tool)
- MIT-BIH, 44 non-paced records, **DS1 → train, DS2 → test** (de Chazal split). Validation = ~4 whole DS1 records.
- **4 AAMI classes: N, S, V, F** (Q dropped; confirm in `04_open_questions.md`).
- Beat window 90 + 162 = 252 samples, z-scored, plus RR features (pre-RR, post-RR, local mean RR, pre-RR / local mean).
- Model: **one** CNN-BiLSTM + RR features, well under 1 M parameters. A plain CNN (v0) is kept only as a sanity baseline.
- Class-weighted cross-entropy; early stopping on validation macro-F1.
- Report: confusion matrix, per-class Se / +P / F1, macro-F1, accuracy, parameter count, ms per beat.
- R peaks: **annotation positions**, stated clearly as a limitation.

### O2: Quantitative evaluation of explanations, clean and under noise (the contribution)
Methods: **Grad-CAM** (last Conv1d) and **Gradient SHAP** (whole network), both via Captum.

| Metric | Question it answers | How (first version) |
|---|---|---|
| **M1 Faithfulness** | Does the map point at what the model actually uses? | Deletion test: remove the top-k% attributed samples vs k% random samples; compare the drop in p(class). Curve over k = 5, 10, 20, 30%. |
| **M2 Within-class consistency** | Does the model explain the same class the same way? | Mean pairwise correlation of maps within each class (sampled pairs). |
| **M3 Clinical-region overlap** | Does it look where a cardiologist would? | Share of attribution in P / QRS / T windows relative to R, per class. Expect V → QRS, S → P/timing. |
| **M4 Method agreement** | Do Grad-CAM and SHAP agree? | Rank (Spearman) correlation between the two maps for the same beat. |
| **M5 Stability under noise** (novel) | Does the explanation survive realistic noise? | Add NSTDB noise to DS2 beats; correlation between clean and noisy maps, plus top-k overlap, vs SNR. Report alongside F1 vs SNR. |

Noise setup: NSTDB **MA (muscle artefact)** and **EM (electrode motion)** at **18, 6 and 0 dB SNR**.

---

## What is in, cut back, dropped

| Keep (core) | Cut back | Dropped → future work / stretch |
|---|---|---|
| DS1/DS2, 4 classes | One model, no architecture search | INCART external test |
| Per-class metrics, macro-F1 | Annotation R peaks (no Pan-Tompkins) | MC-dropout uncertainty |
| Grad-CAM + Gradient SHAP | Noise: 2 types × 3 SNRs (was 3 × 5) | Full ablation study, McNemar tests |
| M1–M5 metrics | 1–2 ablations only (e.g. with/without RR features) | Structured clinician rating (add only if someone is actually available) |
| Explanation stability under noise | Bootstrap CI for macro-F1 only | Pan-Tompkins pipeline |

**Stretch order** if there is time in the buffer week: (1) Pan-Tompkins, (2) INCART, (3) MC dropout.

---

## Gaps answered
- **Gap 1** (explanations shown but not measured) → M1–M4.
- **Gap 2** (XAI rarely paired with patient-independent evaluation) → O1 + O2 on DS1/DS2.
- **Gap 3** (noise robustness narrow, never linked to explanations) → M5.
- Gap 4 (minority classes / external generalisation) → reported honestly in O1; external testing is future work.

## Risks and what we do about them
| Risk | Fallback |
|---|---|
| S/F recall very low | Report it; compare with [15] p.16–17. The claim is about explanations, not accuracy. |
| Grad-CAM through LSTM is awkward | Grad-CAM on the CNN layers only (that's the plan); SHAP covers the whole net. |
| Region windows (P/QRS/T) are crude | Use fixed windows first, state the limitation; delineation only if time allows. |
| Running out of time | Drop M4 first, then reduce M5 to MA noise only. M1 and M5 must stay. |
