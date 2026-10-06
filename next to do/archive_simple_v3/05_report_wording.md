# Ready-to-use wording (report + PPT), Scope v3

## Title
Explainable Deep Learning Framework for Automated ECG Arrhythmia Detection and Classification

## Problem statement
Arrhythmias are abnormal heart rhythms that can be life-threatening, and detecting them requires inspecting long ECG recordings beat by beat, which is slow and error-prone when done manually. Deep learning models can classify ECG beats automatically with high accuracy, but they act as "black boxes": they do not show *why* a beat was classified as abnormal, which limits clinicians' trust. Explainability methods such as Grad-CAM can highlight which parts of the ECG waveform influenced a decision.

## Aim
To develop a deep learning model that automatically classifies ECG beats into arrhythmia classes and to explain its decisions visually using Grad-CAM.

## Objectives
1. Build a preprocessing pipeline for the MIT-BIH Arrhythmia Database: filtering, beat segmentation and mapping to the four AAMI classes (N, S, V, F).
2. Train and compare a 1D CNN and a hybrid CNN-LSTM classifier, evaluated with accuracy, per-class precision, recall and F1-score.
3. Evaluate the model under both a standard (intra-patient) split and the inter-patient DS1/DS2 split, to show how performance changes on unseen patients.
4. Apply Grad-CAM to visualise which regions of the ECG beat (P wave, QRS complex, T wave) drive each prediction.

## Limitations / future work
- Explanations are assessed visually, not with quantitative metrics (faithfulness, consistency).
- Robustness to real-world noise (e.g. MIT-BIH Noise Stress Test Database) is not tested.
- Only one database is used; external validation (e.g. INCART) is future work.
- Expert-annotated R-peak positions are used instead of an automatic detector such as Pan-Tompkins.
- No clinician evaluation of the explanations.
