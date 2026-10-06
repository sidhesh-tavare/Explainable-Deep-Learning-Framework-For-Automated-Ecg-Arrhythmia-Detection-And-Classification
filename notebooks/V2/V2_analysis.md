# V2 Analysis: Improved 1D CNN (Step-by-step Experiments) + Grad-CAM

**Notebook:** `ECG_Arrhythmia_Classification_Experiments_and_Explainability.ipynb` (36 cells)
**Outputs folder:** `ECG_Arrhythmia_Complete_Results/`
**Run environment (from outputs):** Kaggle, TensorFlow 2.20.0, GPU found (2 × Tesla T4 were listed; the code does not set up multi-GPU, so one was probably used). Data at `/kaggle/input/datasets/shayanfazeli/heartbeat`. Total training time for the five experiments was 8.1 min.

Every number below is copied from the notebook's printed outputs, its saved CSVs, or its saved figures. Anything inferred rather than printed is labelled **[Interpretation]**. Anything missing or unclear is labelled **[Unclear]**.

---

## 1. Objective

V2 starts from the V1 baseline 1D CNN (called **B0**) and adds improvements **one at a time**, so that each change's effect shows up in a results table. Each change targets a problem seen in the V1 outputs:

| Step | Change added | Baseline problem it targets (as stated in the notebook) |
|---|---|---|
| B0 | Baseline (numbers copied from the V1 run) | Accuracy 94.41%, macro-F1 76.29%, F precision only 26.02% |
| E1 | Pick the best epoch by **validation macro-F1** | Baseline picked its epoch on a validation loss dominated by N |
| E2 | + stable training: lower LR, gradient clipping, BN momentum 0.9 | Validation accuracy jumped between 14% and 95% |
| E3 | + softer class weights (square root) | One F beat counted as ~114 N beats, so F and S were over-predicted |
| E4 | + light augmentation | Rare classes have few training beats (F ≈ 513) |
| E5 | + deeper residual network | Training accuracy was only 90.93% and still rising when V1 stopped |
| Final | Best of E1–E5 (chosen on validation) + tuned decision thresholds | F and S predicted too often |

**Rules the notebook sets for itself:** same seed and same train / validation / test split as the baseline. The test set is never used to pick an epoch, a model or a threshold; only the validation set is used for that.

The notebook also repeats Grad-CAM on the final model and builds summary tables and figures for the report.

---

## 2. Dataset

The dataset and split are the same as V1. Printed outputs confirm they match:

| Item | Value |
|---|---|
| Source | Kaggle ECG Heartbeat Categorization Dataset (MIT-BIH part), `mitbih_train.csv` / `mitbih_test.csv` |
| Beats | Train file (87,554, 187), test file (21,892, 187) |
| Beat format | 187 samples, 125 Hz (1.5 s), scaled 0–1, zero-padded |
| Classes | N, S, V, F, Q (5 AAMI classes) |
| Train file per class | N 72,471 · S 2,223 · V 5,788 · F 641 · Q 6,431 |
| Test file per class | N 18,118 · S 556 · V 1,448 · F 162 · Q 1,608 |
| Split | Stratified 80/20 of the train file, seed 42 → Train (70,043) / Val (17,511). Test = test file (21,892) |
| Split type | By beat, so **intra-patient** (stated in the notebook) |

Per-class counts in the training portion: N 57,977 · S 1,778 · V 4,630 · F 513 · Q 5,145.

**Preprocessing:** as in V1, the notebook does no filtering or segmentation of its own. The only new step on the data is **training-time augmentation** (E4 onward, §3.3).

---

## 3. Methodology (in notebook order)

### 3.1 Setup (cell 3)
- `SEED = 42`, and a `reset_seeds()` function is called before every experiment.
- `BATCH_SIZE = 128`, `EPOCHS = 30` (max per experiment), `PATIENCE = 8`.
- The baseline scores are **hard-coded** from the V1 printout: acc 0.9441, macro-F1 0.7629, recall S 0.6691, recall F 0.8642, precision S 0.5586, precision F 0.2602.
- CPU fallback: if no GPU is found, only E4 runs for 15 epochs. This did **not** happen; a GPU was found and all five experiments ran.

### 3.2 Class weights (cell 7)

| Class | Train beats | Balanced weight (B0, E1, E2) | Sqrt weight (E3, E4, E5) |
|---|---|---|---|
| N | 57,977 | 0.24 | 0.49 |
| S | 1,778 | 7.88 | 2.81 |
| V | 4,630 | 3.03 | 1.74 |
| F | 513 | 27.31 | 5.23 |
| Q | 5,145 | 2.72 | 1.65 |

Printed F:N weight ratio: **balanced 113:1, sqrt 10.6:1**. The weights are applied as per-sample `sample_weight` (V1 used Keras `class_weight`).

### 3.3 Augmentation, used from E4 onward (cell 9)
Each epoch, every **training** beat gets a fresh random change:
- amplitude scaled by U(0.9, 1.1),
- Gaussian noise with σ = 0.01, added only where the signal is > 0, so the zero padding stays zero,
- a time shift of −3 to +3 samples (±24 ms). Right shifts repeat the first value; left shifts fill with zeros.

Validation and test beats are never augmented. Figure: `figures/01_augmentation_examples.png` (one N, S and F beat, each with 3 augmented copies; the copies stay close to the original).

### 3.4 Networks (cell 11)

| Network | Description | Params |
|---|---|---|
| `cnn` | Identical to the V1 baseline (Conv 32/7 → 64/5 → 128/3, each with BN + ReLU + MaxPool 2; then GAP → Dense 64 → Dropout 0.3 → Dense 5). BN momentum is now a parameter | **44,741** |
| `resnet` (E5) | Stem Conv 32/7 + BN + ReLU, then 3 residual blocks (32, 64, 128 filters). Each block: Conv k=5 → BN → ReLU → Conv k=5 → BN, added to a shortcut (1×1 conv when the channel count changes), then ReLU and MaxPool 2. Same GAP → Dense 64 → Dropout 0.3 → Dense 5 head | **185,477** |

In both networks the last activation before the final pooling is named `gradcam_target`, so Grad-CAM works on either one. Its time resolution is 46 steps.

**BN momentum reasoning (part of E2):** with momentum 0.99 the running mean/variance used at inference lags behind the changing weights. V2 argues this explains V1's good training / bad validation epochs, and uses momentum 0.9.

### 3.5 Training loop (cell 13), used for every experiment E1–E5
V2 uses a custom per-epoch loop instead of Keras callbacks:
1. If augmentation is on, augment `X_train` freshly.
2. `model.fit(..., epochs=1, sample_weight=..., shuffle=True)`.
3. Predict the validation set and compute **validation macro-F1** and accuracy.
4. If macro-F1 improved, store the weights. Otherwise increase a wait counter. Every 3 non-improving epochs the LR is halved (min 1e-5). After **8** non-improving epochs training stops.
5. At the end, restore the best weights and predict the validation and test sets.

### 3.6 Experiment configurations (cell 15)

Each experiment keeps all earlier changes and adds one:

| ID | Arch | LR | Clipnorm | BN momentum | Weights | Augment |
|---|---|---|---|---|---|---|
| E1 | cnn | 1e-3 | none | 0.99 | balanced | no |
| E2 | cnn | 5e-4 | 1.0 | 0.9 | balanced | no |
| E3 | cnn | 5e-4 | 1.0 | 0.9 | sqrt | no |
| E4 | cnn | 5e-4 | 1.0 | 0.9 | sqrt | yes |
| E5 | resnet | 5e-4 | 1.0 | 0.9 | sqrt | yes |

Common to all: Adam, sparse categorical cross-entropy, batch 128, max 30 epochs, patience 8.

### 3.7 Final model selection and threshold tuning (cell 19)
- **Model choice:** the experiment with the highest **validation** macro-F1.
- **Threshold tuning:** each class probability is multiplied by a scale factor, then argmax is taken. The factors are found by a coordinate search over the grid {0.05, 0.1, 0.2, 0.3, 0.5, 0.7, 1.0, 1.5, 2.0, 3.0, 5.0}: 2 passes over the 5 classes, maximising validation macro-F1. The tuned factors are then applied to the test set once.

### 3.8 Evaluation, Grad-CAM and packaging (cells 21–35)
- Results table for B0, E1–E5 and Final → `experiment_results.csv` and `figures/03_experiment_comparison.png`.
- Final model: classification report, confusion matrix and per-class bars (`04_…`, `05_…`).
- Grad-CAM, the same algorithm as V1, on `gradcam_target` of the final model. For each class it explains the most confident correctly classified test beat (using the **un-tuned** argmax predictions). The model is saved as `improved_1d_cnn.h5`.
- Summary tables → `model_improvement_summary.csv` and `per_class_model_comparison.csv`. Figures `07_…`, `08_…`, `09_…`. Text "experiment roadmap".
- All outputs are zipped into `ECG_Arrhythmia_Complete_Results.zip` (cell 35). The folder in this directory is that package, unzipped.

---

## 4. Results

### 4.1 Training runs (cell 15 logs)

| ID | Best epoch / epochs run | Stopped early? | Best val macro-F1 | Time |
|---|---|---|---|---|
| E1 | 16 / 24 | yes (epoch 24) | 85.43% | 70 s |
| E2 | 28 / 30 | no (hit max 30) | 79.35% | 80 s |
| E3 | 23 / 30 | no (hit max 30) | 88.65% | 80 s |
| E4 | 25 / 30 | no (hit max 30) | 88.01% | 95 s |
| E5 | 18 / 26 | yes (epoch 26) | 93.19% | 158 s |

Notes from the per-epoch logs:
- **E1** is still very unstable: validation accuracy goes 0.9223 (epoch 6) → 0.7707 (epoch 7), and val macro-F1 swings 0.58–0.85.
- **E2** is *not* visibly more stable: validation accuracy falls to 0.6499 at epoch 7 and stays below 0.94 throughout. Its best epoch is 28 of 30 with the LR already down to 3e-5. **[Interpretation]** It looks undertrained (slow learning, still improving at the cap).
- **E3** reaches val macro-F1 0.8227 by epoch 3 and settles around 0.87–0.89 from epoch 17 on.
- **E4** is similar to E3: it peaks at 0.8801 (epoch 25).
- **E5** starts much higher (0.7838 at epoch 1, 0.8768 by epoch 5). It rises fairly smoothly to 0.9319 at epoch 18, and validation accuracy stays at 0.94–0.99.

Figure `figures/02_validation_curves.png` shows these curves. E5 is the highest and smoothest, E2 is the lowest, and E1 is the most jagged.

### 4.2 Main results table (cell 21, `experiment_results.csv`, test set unless stated)

| ID | Change | Val macro-F1 | Test acc | **Test macro-F1** | Recall S | Recall F | Precision S | Precision F | Best epoch |
|---|---|---|---|---|---|---|---|---|---|
| B0 | Baseline (V1 run) | – | 94.41 | **76.29** | 66.91 | 86.42 | 55.86 | 26.02 | 11 |
| E1 | Best epoch by val macro-F1 | 85.43 | 96.28 | **83.96** | 71.58 | 87.04 | 57.02 | 55.95 | 16 |
| E2 | + stable training | 79.35 | 93.58 | **78.30** | 79.14 | 88.27 | 35.63 | 43.73 | 28 |
| E3 | + sqrt class weights | 88.65 | 97.39 | **87.58** | 68.53 | 78.40 | 71.21 | 75.60 | 23 |
| E4 | + light augmentation | 88.01 | 97.02 | **86.20** | 62.23 | 80.25 | 70.61 | 72.63 | 25 |
| E5 | + residual network | 93.19 | 98.29 | **90.77** | 83.63 | 79.01 | 78.95 | 78.05 | 18 |
| **Final** | E5 + tuned thresholds | 93.95* | **98.41** | **91.10** | 77.34 | 76.54 | 87.58 | 82.12 | 18 |

\*Optimistic: the thresholds were fitted on this same validation set (the notebook says so).

**Step-by-step change in test macro-F1** (computed from the table above):

| Step | Δ Test macro-F1 | Δ Val macro-F1 |
|---|---|---|
| B0 → E1 | +7.67 | – |
| E1 → E2 | **−5.66** | −6.08 |
| E2 → E3 | +9.28 | +9.30 |
| E3 → E4 | −1.38 | −0.64 |
| E4 → E5 | +4.57 | +5.18 |
| E5 → Final | +0.33 | +0.76 (optimistic) |

### 4.3 Per-class F1 across experiments (`model_improvement_summary.csv`)

| Model | Acc | Macro-F1 | N F1 | S F1 | V F1 | F F1 | Q F1 |
|---|---|---|---|---|---|---|---|
| B0 | 94.41 | 76.29 | 97.00 | 60.90 | 86.60 | 40.00 | 97.00 |
| E1 | 96.28 | 83.96 | 97.92 | 63.48 | 92.51 | 68.12 | 97.77 |
| E2 | 93.58 | 78.30 | 96.27 | 49.13 | 90.77 | 58.49 | 96.84 |
| E3 | 97.39 | 87.58 | 98.58 | 69.84 | 94.19 | 76.97 | 98.29 |
| E4 | 97.02 | 86.20 | 98.40 | 66.16 | 91.93 | 76.25 | 98.29 |
| E5 | 98.29 | 90.77 | 99.13 | 81.22 | 95.70 | 78.53 | 99.28 |
| Final | 98.41 | 91.10 | 99.18 | 82.14 | 95.87 | 79.23 | 99.06 |

Full per-class precision / recall / F1 for every model is in `per_class_model_comparison.csv`; its Final rows are reproduced in §4.4. Figures: `07_overall_model_comparison.png` (accuracy and macro-F1 bars per model) and `08_per_class_f1_progression.png` (per-class F1 lines B0 → Final).

### 4.4 Final model (E5 + tuned thresholds) in detail (cell 23)

- **Selected model:** E5, val macro-F1 93.19%, the highest of E1–E5.
- **Tuned scale factors:** `{N: 3.0, S: 1.0, V: 1.0, F: 1.0, Q: 1.0}`. Only N changed: its probability is multiplied by 3, so the model must be more confident before it predicts any non-N class.
- **Test accuracy 98.41%** (98.29% before tuning). **Test macro-F1 91.10%** (90.77% before tuning).
- Parameters: 185,477.

| Class | Precision | Recall | F1 | Support |
|---|---|---|---|---|
| N | 0.9874 | 0.9962 | 0.9918 | 18,118 |
| S | 0.8758 | 0.7734 | 0.8214 | 556 |
| V | 0.9805 | 0.9378 | 0.9587 | 1,448 |
| F | 0.8212 | 0.7654 | 0.7923 | 162 |
| Q | 0.9981 | 0.9832 | 0.9906 | 1,608 |
| Macro avg | 0.9326 | 0.8912 | **0.9110** | 21,892 |
| Weighted avg | 0.9836 | 0.9841 | 0.9837 | 21,892 |

**Confusion matrix** (read from `figures/04_confusion_matrix_final.png`):

| True \ Pred | N | S | V | F | Q |
|---|---|---|---|---|---|
| **N** | **18,050** | 53 | 9 | 5 | 1 |
| **S** | 120 | **430** | 4 | 2 | 0 |
| **V** | 64 | 5 | **1,358** | 19 | 2 |
| **F** | 23 | 1 | 14 | **124** | 0 |
| **Q** | 24 | 2 | 0 | 1 | 1,581 |

Row-normalised recall: N 1.00, S 0.77, V 0.94, F 0.77, Q 0.98.
- False F predictions fell from 398 (V1) to **27**. Only 5 N beats were called F (V1: 293).
- False S predictions fell from 294 (V1) to **61**.
- The largest remaining error is **S → N: 120 of 556 S beats (22%)**. Next: V → N (64), F → N (23) and F → V (14).

Figures: `05_per_class_scores_final.png` and `09_final_per_class_metrics.png` both show per-class precision / recall / F1 of the final model.

### 4.5 Baseline → Final summary (printed by cell 28)

```
Accuracy    :  94.41% ->  98.41%   (+4.00 points)
Macro-F1    :  76.29% ->  91.10%   (+14.81 points)
Recall S    :  66.91% ->  77.34%   (+10.43 points)
Recall F    :  86.42% ->  76.54%   (-9.88 points)
Precision S :  55.86% ->  87.58%   (+31.72 points)
Precision F :  26.02% ->  82.12%   (+56.10 points)
NOTE: recall on F is LOWER than the baseline by 9.88 points.
```

### 4.6 Grad-CAM on the final model (read from `figures/06_gradcam_final.png`)

All five beats shown were predicted with p = 1.00.

| Class | Where the heat is concentrated |
|---|---|
| N | Two bands at ~0.12–0.2 s and ~0.4–0.5 s (the region before the second R peak, around the small P-wave-like bump at ~0.5 s). The second R peak itself (~0.7 s) gets low heat |
| S | The start (~0–0.2 s) and a band at ~0.75–0.9 s just after the second peak |
| V | The start (~0–0.1 s), a band at ~0.27–0.35 s, and a band at ~1.15–1.3 s around the second peak and the end of the signal |
| F | One strong broad band at ~0.3–0.5 s, centred on the second peak |
| Q | A band at ~0.1 s (the deep trough) and a band at ~0.75–0.95 s around the second peak |

Compared with V1, the heatmaps are **broader** and more often cover waveform features (bumps, troughs) other than the window start. **[Interpretation]** Strong heat near the second peak or end of signal is still common (S, V, Q). As in V1, this may mean the model uses the timing of the next beat. None of this is quantified in V2.

---

## 5. Findings

### 5.1 What worked
1. **Selecting the epoch on validation macro-F1 (E1) was a large, cheap win:** +7.67 macro-F1, and F precision 26.02 → 55.95. The weights the V1 run saw along the way included better macro-F1 epochs, but `val_loss` did not choose them. (Caveat in §6, item 3.)
2. **Square-root class weights (E3) were the largest single gain:** +9.28 macro-F1 over E2, and the best CNN result (87.58). F precision rose 43.73 → 75.60 and S precision 35.63 → 71.21. This confirms the V1 diagnosis that 113:1 weighting caused over-prediction of rare classes. Recall on F dropped (88.27 → 78.40), which is the expected trade-off.
3. **The residual network (E5) gave the second largest gain:** +4.57 macro-F1. It had the best scores on every metric except F recall, the smoothest training, and S F1 jumped 66.16 → 81.22. With about 4× the parameters (185k vs 45k) it fits the data better (train loss 0.0641 at the best epoch vs ~0.10–0.17 for the CNN runs).
4. **Overall:** test macro-F1 rose from 76.29% to 91.10% and accuracy from 94.41% to 98.41%, on the same 21,892-beat test set. F1 improved for every class (S +21.2, F +39.2, V +9.3 points).
5. **The selection procedure was clean:** the model and thresholds were chosen on validation only, and the test set was looked at once per experiment.

### 5.2 What did not work
1. **E2 (lower LR + clipping + BN momentum 0.9) made things worse:** −5.66 test macro-F1, and S precision fell to 35.63. It did **not** visibly fix the instability it targeted (val accuracy still dropped to 0.65 at epoch 7). It hit the 30-epoch cap with its best epoch at 28, so it was probably undertrained at the halved LR. Its three sub-changes were never tested separately, so it is unknown which one hurt.
2. **E2's settings were still carried into E3–E5.** Every later experiment builds on a step that hurt on its own, so the final model may not be the best combination available.
3. **Augmentation (E4) slightly hurt:** −1.38 test, −0.64 val macro-F1, and S recall fell 68.53 → 62.23. It was also carried into E5.
4. **Threshold tuning had only a small effect** (+0.33 macro-F1) and **traded rare-class recall for precision**. S recall fell 83.63 → 77.34 and F recall 79.01 → 76.54, while S precision rose 78.95 → 87.58. The tuned solution is just "multiply N by 3".
5. **F recall is lower than the baseline:** 76.54 vs 86.42. The notebook flags this itself. The baseline's high F recall came with 26% precision, but **[Interpretation]** missing more F beats may matter clinically.

### 5.3 Why (from the evidence)
- Rare-class precision was limited mainly by **over-weighting**. Reducing the weights (E3) and requiring higher non-N confidence (threshold N×3) both cut false S/F alarms, and both cost some recall.
- The CNN was **capacity / optimisation limited**. In V1 its training accuracy was still rising. The residual network trains faster and further (E5 val macro-F1 is 0.78 at epoch 1, against 0.33–0.67 for the CNN runs).
- **S → N remains the main confusion** (22% of S). **[Interpretation]** S beats often look like N in shape; the main difference is timing (prematurity). That points to explicit RR features, which the project plans to add.

### 5.4 Explainability
Grad-CAM was moved to a generic `gradcam_target` layer and runs on the residual model. The output is still **one most-confident beat per class, qualitative only**. V2 adds **no** quantitative explanation metric and no SHAP.

---

## 6. Limitations and issues

### 6.1 Experimental design
1. **Intra-patient split** (acknowledged by the notebook). All scores, including 98.41% / 91.10%, are by-beat scores on patients also seen in training. They are not comparable to inter-patient (DS1/DS2) results in the literature, which are typically much lower.
2. **Single seed, single run per experiment, no error bars.** Some differences are small: E3 vs E4 is 1.38 points, and Final vs E5 is 0.33 points. The F class has only 162 test beats, so each F beat is ≈0.6 points of F recall. Run-to-run variance was not measured, so whether a ±1–2 point change is real is **[Unclear]**.
3. **B0 → E1 is not a single-variable change.** Besides the selection metric, E1 differs from the V1 run in: a custom loop instead of Keras callbacks; LR halving on non-improving **macro-F1** instead of `ReduceLROnPlateau` on `val_loss`; patience 8 instead of 6; `sample_weight` instead of `class_weight`; and a different TF version (2.20 vs the older V1 environment) and hardware. **B0 was not re-run in V2's environment.** Its numbers were copied in. So the +7.67 gain cannot be credited to "selecting on macro-F1" alone.
4. **Cumulative design with no ablation.** Each step keeps everything before it, including steps that hurt (E2, E4). The contribution of, for example, the residual network *without* E2's settings or augmentation is unknown.
5. **E5 changes two things at once:** architecture type (residual) and capacity (4× parameters). The design cannot tell which one helped.
6. **The 30-epoch cap was binding** for E2, E3 and E4 (none stopped early). Their best epochs were 28, 23 and 25, so they may have been under-trained relative to E1 and E5.
7. **Threshold tuning and model selection share the same validation set** that was used for early stopping. The notebook marks the tuned val score (93.95) as optimistic. Test-set use was correctly limited.
8. **Q class still included** (5 classes). The planned framework uses N/S/V/F, so macro-F1 values here will not carry over directly.

### 6.2 Explainability
9. Grad-CAM uses one hand-picked, most-confident beat per class. There are no failure cases, no aggregate statistics, no region-share or deletion metrics, and no SHAP.
10. Grad-CAM resolution is still 46 steps, interpolated to 187.

### 6.3 Code and file issues
11. **`all_classes_model_comparison.csv` is not produced by any cell in the saved notebook.** It is byte-for-byte identical to `per_class_model_comparison.csv`. Execution counts 9, 11 and 18 are missing, so a cell that wrote it was probably deleted or replaced. It is redundant, not wrong.
12. **B0 per-class values in the summary CSVs are rounded.** The B0 rows in `model_improvement_summary.csv` and `per_class_model_comparison.csv` come from a hard-coded 3-decimal dict (e.g. S F1 60.90 rather than 60.88). The headline B0 numbers (acc 94.41, macro-F1 76.29) are exact.
13. **`__notebook_source__.ipynb` is not a real notebook.** Despite the `.ipynb` extension it is a plain Python script (Kaggle's source export). Its code matches the notebook's code cells line for line (verified), but it has no outputs and will not open in Jupyter.
14. Leftover debug cell `print("HI")` (cell 1) and an empty code cell at the end of the summary section.
15. The intro markdown says "six improvements". There are five experiments plus threshold tuning, so this is consistent if threshold tuning is counted as the sixth.
16. The model is saved in legacy HDF5 format (`improved_1d_cnn.h5`). TF prints a warning about this. It works but is not the recommended format.
17. The notebook header says Grad-CAM is "a qualitative preview" and that the inter-patient split, 4-class setup, RR features, SHAP and noise tests are future work. **None of those are in V2.**

---

## 7. What changed from V1 and how it affected the results

| Aspect | V1 | V2 | Effect on results |
|---|---|---|---|
| Data, classes, split | Kaggle MIT-BIH, 5 classes, stratified 80/20, seed 42 | **Unchanged** | Results are directly comparable on the same 21,892-beat test set (with the caveats in §6.1, item 3) |
| Epoch selection | Lowest `val_loss` (Keras EarlyStopping, patience 6) | Highest **val macro-F1**, custom loop, patience 8 | E1: macro-F1 76.29 → 83.96, F precision 26.0 → 56.0 |
| Optimiser settings | LR 1e-3, no clipping, BN momentum 0.99 | LR 5e-4, clipnorm 1.0, BN momentum 0.9 (E2+) | Alone it **hurt** (−5.66). It did not visibly stabilise training. Kept anyway |
| Class weights | Balanced (F:N ≈ 113:1) | √balanced (F:N ≈ 10.6:1) (E3+) | **Biggest gain** (+9.28). Precision S/F rose sharply, F recall fell |
| Augmentation | None | Scale ±10%, noise σ 0.01, shift ±3 samples (E4+) | Slightly **hurt** (−1.38) |
| Architecture | 3-block CNN, 44,741 params | 3-block residual CNN, 185,477 params (E5) | +4.57 macro-F1. Smoothest training. Best S F1 |
| Decision rule | Plain argmax | Per-class probability scaling tuned on validation (N × 3) | +0.33 macro-F1. Precision ↑, S/F recall ↓ |
| Grad-CAM | `relu3` of the CNN | `gradcam_target` of the residual net | Heatmaps broader, more on waveform features. Still qualitative |
| Reporting | One results CSV, 6 figures | 4 CSVs (one duplicate), 9 figures, step-by-step comparison | Clear ablation-style story for the report |

**Net effect:** test macro-F1 **76.29% → 91.10% (+14.81)**, accuracy **94.41% → 98.41% (+4.00)**. Per-class F1: N 97.0 → 99.2, S 60.9 → 82.1, V 86.6 → 95.9, F 40.0 → 79.2, Q 97.0 → 99.1. Most of the gain came from **better model selection (E1), softer class weights (E3) and the residual network (E5)**. The stability tweaks (E2) and augmentation (E4) did not help on their own. The final model trades F recall (86.4 → 76.5) for much higher F precision (26.0 → 82.1).

---

## 8. Output file inventory

| File | Produced by | Contents |
|---|---|---|
| `experiment_results.csv` | Cell 21 | Main table (§4.2) |
| `model_improvement_summary.csv` | Cell 29 | Accuracy, macro-F1 and per-class F1 per model (§4.3) |
| `per_class_model_comparison.csv` | Cell 30 | Precision / recall / F1 per class per model |
| `all_classes_model_comparison.csv` | **No cell in the saved notebook** | Identical copy of the file above |
| `improved_1d_cnn.h5` | Cell 26 | Final E5 model weights (without the threshold scales, which are not saved anywhere) |
| `__notebook_source__.ipynb` | Kaggle export | Plain-Python source, not a notebook |
| `figures/01_augmentation_examples.png` | Cell 9 | Original vs augmented N, S, F beats |
| `figures/02_validation_curves.png` | Cell 17 | Val macro-F1 and val accuracy per epoch, E1–E5 |
| `figures/03_experiment_comparison.png` | Cell 21 | Test macro-F1, recall S, recall F per model |
| `figures/04_confusion_matrix_final.png` | Cell 23 | Final model confusion matrices |
| `figures/05_per_class_scores_final.png` | Cell 24 | Final per-class P/R/F1 bars |
| `figures/06_gradcam_final.png` | Cell 26 | Grad-CAM, one beat per class, final model |
| `figures/07_overall_model_comparison.png` | Cell 31 | Accuracy and macro-F1 bars, B0 → Final |
| `figures/08_per_class_f1_progression.png` | Cell 32 | Per-class F1 lines, B0 → Final |
| `figures/09_final_per_class_metrics.png` | Cell 33 | Final per-class P/R/F1 bars (similar to 05) |

Note: the tuned threshold scale factors (N = 3.0, others 1.0) are only printed in the notebook output. They are **not saved to any file**, so reloading `improved_1d_cnn.h5` gives the E5 results (90.77 macro-F1), not the Final results (91.10), unless N × 3 is applied by hand.
