# Ready-to-use wording (report + PPT)

## Title
**Do ECG Arrhythmia Explanations Hold Up? Measuring the Faithfulness, Consistency and Noise-Stability of Grad-CAM and SHAP on a Patient-Independent Classifier**

## Problem statement
Deep learning models classify ECG beats with high reported accuracy, but two problems limit their clinical use. First, many results come from intra-patient splits, which inflate performance; under the inter-patient protocol, F1 drops sharply (e.g. 95.52% → 83.89% [10] p.16; 99.00% → 91.69% [15] p.1). Second, explainability methods such as Grad-CAM and SHAP are usually presented as example heatmaps without any measurement of whether they are correct: fewer than 10% of studies validate explanation maps against clinical structures [12] p.40, and none of the 37 reviewed studies tests whether explanations remain stable when the ECG is corrupted by realistic noise. A clinician therefore cannot tell whether an explanation reflects what the model actually used, or whether it would change under ordinary recording noise.

## Aim
To build a patient-independent ECG arrhythmia classifier and quantitatively evaluate how reliable its explanations are, on clean signals and under realistic noise.

## Objectives
1. **O1.** Develop a CNN-BiLSTM classifier with RR-interval features for the four AAMI beat classes (N, S, V, F), trained and tested on the MIT-BIH inter-patient split (DS1/DS2), and report per-class sensitivity, positive predictivity and F1.
2. **O2.** Generate Grad-CAM and Gradient SHAP explanations for the classifier and evaluate them quantitatively using faithfulness (deletion test), within-class consistency, overlap with clinical waveform regions (P, QRS, T), and agreement between the two methods.
3. **O3 (part of O2 if only two objectives are allowed).** Measure how classification performance and explanation stability change when real noise from the MIT-BIH Noise Stress Test Database (muscle artefact, electrode motion) is added at graded SNRs.

## Novelty (one sentence for the viva)
> "Most explainable ECG papers show heatmaps; we measure them: whether they are faithful to the model, consistent within a class, located on the right waveform, and stable under real noise. No paper in our 37-paper review measures that last one."

## Scope and limitations (for the report)
- Single database for training and testing (MIT-BIH); external validation is future work.
- Expert-annotated R-peak positions are used, so R-peak detection errors are not modelled.
- Clinical-region overlap uses fixed time windows around the R peak, not full waveform delineation.
- No clinician evaluation of explanations (unless arranged).
