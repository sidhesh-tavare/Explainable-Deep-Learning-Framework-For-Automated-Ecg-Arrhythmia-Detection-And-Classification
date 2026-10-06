# Ready-to-use wording (report + PPT), Scope v4

## Title
Explainable Deep Learning Framework for Automated ECG Arrhythmia Detection and Classification

## Problem statement
Arrhythmias are abnormal heart rhythms that can be life-threatening, and detecting them requires inspecting long ECG recordings beat by beat, which is slow and error-prone when done manually. Deep learning models classify ECG beats with high reported accuracy, but three issues limit their use in practice. First, they act as "black boxes" and do not show why a beat was flagged, and when explanations are provided they are usually shown as example heatmaps without being checked (fewer than 10% of studies validate them against clinical structures [12] p.40). Second, many reported accuracies come from splits where the same patient appears in training and testing, which inflates results (e.g. F1 95.52% → 83.89% on unseen patients [10] p.16). Third, models are rarely tested on noisy signals, although real recordings contain muscle and motion artefacts.

## Aim
To develop an explainable deep learning framework that classifies ECG beats into arrhythmia classes, explains each decision visually, checks whether those explanations are sensible, and tests how the system behaves under realistic noise.

## Objectives
1. Build a preprocessing pipeline for the MIT-BIH Arrhythmia Database (filtering, beat segmentation, RR-interval features, mapping to the AAMI classes N, S, V, F).
2. Develop and compare a 1D CNN baseline and a hybrid CNN-LSTM model with RR features, evaluated on both an intra-patient split and the inter-patient DS1/DS2 split using per-class precision, recall and F1-score.
3. Explain predictions with Grad-CAM and SHAP, and assess the explanations by (a) the share of importance on the P wave, QRS complex and T wave and (b) a deletion test of faithfulness.
4. Evaluate robustness by adding real noise from the MIT-BIH Noise Stress Test Database at graded SNRs, measuring the change in classification performance and in explanation stability.
5. Present the framework through an interactive dashboard showing the ECG beat, prediction and explanation.

## Contribution (one line for the viva)
> "Besides classifying beats and showing heatmaps, we check whether the heatmaps are sensible, and whether they stay stable when the signal gets noisy, which none of the 37 papers we reviewed measured."

## Limitations / future work
- Single database; external validation (e.g. INCART) is future work.
- Expert-annotated R-peak positions are used instead of an automatic detector (Pan-Tompkins).
- P/QRS/T regions are fixed time windows around the R peak, not full waveform delineation.
- No uncertainty estimation and no clinician evaluation of explanations.
