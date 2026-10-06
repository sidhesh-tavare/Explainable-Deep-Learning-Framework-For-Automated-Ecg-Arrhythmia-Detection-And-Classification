# V1 Analysis: Baseline 1D CNN + Grad-CAM

**Notebook:** `ECG_Arrhythmia_Baseline_1D_CNN_GradCAM.ipynb`
**Outputs folder:** `all_my_outputs/`
**Run environment (from outputs):** Kaggle, data at `/kaggle/input/heartbeat`. The TensorFlow version is not printed (see §6.3).

Every number below is copied from the notebook's printed outputs, its saved CSV, or its saved figures. Anything inferred rather than printed is labelled **[Interpretation]**. Anything missing or unclear is labelled **[Unclear]**.

---

## 1. Objective

The notebook's first markdown cell describes it as a **baseline** for the B.Tech project *"Explainable Deep Learning Framework for Automated ECG Arrhythmia Detection and Classification"*. Its stated goals:

1. Load the Kaggle *ECG Heartbeat Categorization Dataset* (MIT-BIH part, Kachuee et al., 2018).
2. Look at the class imbalance and one example beat per class.
3. Train a small 1D CNN with a class-weighted loss.
4. Report accuracy, per-class precision / recall / F1, macro-F1 and a confusion matrix on the test set.
5. Draw one Grad-CAM heatmap per class as a first, qualitative look at explainability.

The notebook says plainly that this is a starting point. It is not the planned framework. Section 10 of the notebook lists how the planned framework will differ (see §5.5).

---

## 2. Dataset

| Item | Value (from outputs) |
|---|---|
| Source | Kaggle "ECG Heartbeat Categorization Dataset", files `mitbih_train.csv` and `mitbih_test.csv` |
| Origin | MIT-BIH Arrhythmia Database, pre-segmented by the dataset authors (Kachuee et al., 2018) |
| Total beats | 109,446 (87,554 in the train file + 21,892 in the test file) |
| Beat length | 187 samples = 1.5 s at 125 Hz |
| Format | One row per beat: 187 amplitude values scaled 0–1, zero-padded at the end, label in the last column |
| Classes | 5 AAMI classes: N (0) Normal, S (1) Supraventricular ectopic, V (2) Ventricular ectopic, F (3) Fusion, Q (4) Unknown / paced |

### 2.1 Class distribution (printed by cell 6)

| Class | Train beats | Train % | Test beats | Test % |
|---|---|---|---|---|
| N | 72,471 | 82.77 | 18,118 | 82.76 |
| S | 2,223 | 2.54 | 556 | 2.54 |
| V | 5,788 | 6.61 | 1,448 | 6.61 |
| F | 641 | 0.73 | 162 | 0.74 |
| Q | 6,431 | 7.35 | 1,608 | 7.35 |

The data is heavily imbalanced: N is about 83% of beats and F is under 1%. The notebook points out that a model that always predicts N would already score above 80% accuracy. Figure: `figures/01_class_distribution.png`.

### 2.2 Splits

| Set | Shape | How it was made |
|---|---|---|
| Train | (70,043, 187, 1) | 80% of `mitbih_train.csv`, stratified, `random_state=42` |
| Validation | (17,511, 187, 1) | The other 20% of `mitbih_train.csv`. Used for early stopping and LR scheduling |
| Test | (21,892, 187, 1) | `mitbih_test.csv`, used only once at the end |

The split is **by beat, not by patient**, so beats from the same patient can appear in train, validation and test. The notebook states this itself (cell 0): the scores are **intra-patient** scores and will be higher than scores on unseen patients.

### 2.3 Preprocessing

The notebook does **no signal processing of its own**: no filtering, no R-peak detection, no segmentation and no normalisation. All of that was done by the dataset authors. The notebook only:
- casts the data to `float32` / `int64`, and
- adds a channel axis (`[..., None]`) for Conv1D.

The details of the authors' preprocessing (filter type, how the window is placed around the R peak) are **not described in the notebook**. **[Unclear]** for report purposes; they would have to be cited from Kachuee et al., 2018.

Figure `figures/02_example_beats.png` shows the first training beat of each class. Every beat has a sharp peak near t = 0 and a second peak later on, and is then flat at zero (padding) for the rest of the 1.5 s window.

---

## 3. Methodology (in notebook order)

### Step 1: Setup (cell 2)
- Seeds: `random`, `numpy` and `tf` all set to 42.
- Constants: `FS = 125`, `EPOCHS = 30`, `BATCH_SIZE = 128`.
- Every figure is saved to `figures/` at 200 dpi.

### Step 2: Data loading (cell 4)
The notebook searches for `mitbih_train.csv` under `$ECG_DATA_DIR`, `/kaggle/input` or `.`. It was found at `/kaggle/input/heartbeat`.

### Step 3: Class-imbalance analysis (cell 6) and example beats (cell 8)
See §2.1.

### Step 4: Train/validation split and class weights (cell 10)
- Stratified 80/20 split (see §2.2).
- Class weights use sklearn `'balanced'`: `w_c = N / (K · n_c)`, computed on the training portion. The notebook chose this instead of oversampling rare beats.

| Class | Weight |
|---|---|
| N | 0.24 |
| S | 7.88 |
| V | 3.03 |
| F | 27.31 |
| Q | 2.72 |

With these weights one F beat counts about 113× as much as one N beat (27.31 / 0.24; V2 prints this ratio as 113:1).

### Step 5: Model, `baseline_1d_cnn` (cell 12)

| Layer | Output shape | Params |
|---|---|---|
| Input `beat` | (187, 1) | 0 |
| Conv1D 32 filters, kernel 7, `same` → BN → ReLU → MaxPool 2 | (93, 32) | 256 + 128 |
| Conv1D 64 filters, kernel 5, `same` → BN → ReLU → MaxPool 2 | (46, 64) | 10,304 + 256 |
| Conv1D 128 filters, kernel 3, `same` → BN → ReLU (`relu3`) → MaxPool 2 | (23, 128) | 24,704 + 512 |
| GlobalAveragePooling1D | (128) | 0 |
| Dense 64, ReLU | (64) | 8,256 |
| Dropout 0.3 | (64) | 0 |
| Dense 5, softmax | (5) | 325 |
| **Total** | | **44,741** (44,293 trainable, 448 non-trainable) |

### Step 6: Training (cell 14)

| Hyperparameter | Value |
|---|---|
| Optimiser | Adam, learning rate 1e-3 |
| Loss | Sparse categorical cross-entropy, with the class weights above |
| Batch size | 128 |
| Max epochs | 30 |
| Early stopping | monitor `val_loss`, patience 6, `restore_best_weights=True` |
| LR schedule | ReduceLROnPlateau on `val_loss`, factor 0.5, patience 3, min 1e-5 |
| Augmentation | None |

The model was saved as `baseline_1d_cnn.keras`.

### Step 7: Evaluation (cells 17–19)
The notebook predicts with argmax on the test set and computes accuracy, per-class precision / recall / F1, macro-F1 (the plain mean of the 5 F1 scores), a classification report and a confusion matrix (counts and row-normalised). Per-class results are saved to `baseline_results.csv`.

### Step 8: Grad-CAM (cell 21)
- Target layer: `relu3`, the last conv block's activation before pooling. Its time resolution is 46 steps.
- Method: per-channel weights = mean gradient of the class score over time. CAM = ReLU(Σ weight × feature map), normalised to [0, 1] and linearly interpolated back to 187 samples.
- For each class, the beat explained is the **most confident correctly classified test beat**, shown as a red heatmap behind the waveform.
- The notebook says this is a qualitative preview only. Quantitative checks (P / QRS / T region shares) are deferred to the next phase.

---

## 4. Results

### 4.1 Training log (cell 14)

Training stopped early after **17 of 30 epochs**. Each epoch took about 37–40 s.

| Epoch | Train loss | Train acc | Val loss | Val acc |
|---|---|---|---|---|
| 1 | 0.7056 | 0.6141 | 1.5271 | 0.1445 |
| 2 | 0.4392 | 0.7955 | 4.2889 | 0.8200 |
| 3 | 0.3755 | 0.8335 | 1.6190 | 0.3579 |
| 4 | 0.3430 | 0.8490 | 0.9108 | 0.3817 |
| 5 | 0.3277 | 0.8561 | 0.7683 | 0.8627 |
| 6 | 0.3117 | 0.8608 | 0.6619 | 0.3970 |
| 7 | 0.2927 | 0.8685 | 0.3900 | 0.8472 |
| 8 | 0.2873 | 0.8716 | 0.4885 | 0.8922 |
| 9 | 0.2687 | 0.8796 | 0.5202 | 0.9477 |
| 10 | 0.2626 | 0.8823 | 0.3884 | 0.9298 |
| **11** | 0.2519 | 0.8832 | **0.3493** | 0.9465 |
| 12 | 0.2404 | 0.8870 | 0.8332 | 0.9509 |
| 13 | 0.2421 | 0.8874 | 0.7673 | 0.9054 |
| 14 | 0.2251 | 0.8956 | 0.4090 | 0.7845 |
| 15 | 0.1965 | 0.9030 | 0.3753 | 0.9191 |
| 16 | 0.1838 | 0.9077 | 0.6271 | 0.8515 |
| 17 | 0.1750 | 0.9093 | 0.6210 | 0.6172 |

Epoch 11 has the lowest validation loss (0.3493). With patience 6, training stopped at epoch 17 and the epoch-11 weights were restored. (The log does not print "restoring weights", but this follows from `restore_best_weights=True`. V2 also records the baseline's best epoch as 11.) Figure: `figures/03_training_curves.png`.

### 4.2 Test-set metrics (cells 17 and 24)

| Metric | Value |
|---|---|
| **Test accuracy** | **94.41%** |
| **Macro-F1** | **76.29%** |
| Macro precision / recall | 73.22% / 86.07% |
| Weighted F1 | 94.98% |

| Class | Precision | Recall | F1 | Test beats |
|---|---|---|---|---|
| N | 0.9813 | 0.9594 | 0.9702 | 18,118 |
| S | 0.5586 | 0.6691 | 0.6088 | 556 |
| V | 0.8713 | 0.8605 | 0.8659 | 1,448 |
| F | 0.2602 | 0.8642 | 0.4000 | 162 |
| Q | 0.9896 | 0.9502 | 0.9695 | 1,608 |

The same values are in `all_my_outputs/baseline_results.csv`. Figure: `figures/05_per_class_scores.png`.

### 4.3 Confusion matrix (read from `figures/04_confusion_matrix.png`)

| True \ Pred | N | S | V | F | Q |
|---|---|---|---|---|---|
| **N** | **17,382** | 285 | 150 | 293 | 8 |
| **S** | 163 | **372** | 9 | 12 | 0 |
| **V** | 97 | 6 | **1,246** | 91 | 8 |
| **F** | 8 | 0 | 14 | **140** | 0 |
| **Q** | 64 | 3 | 11 | 2 | **1,528** |

Row-normalised recall: N 0.96, S 0.67, V 0.86, F 0.86, Q 0.95.

Key cells:
- **538 beats were predicted F, and only 140 of them were truly F.** 293 were N and 91 were V. This is why F precision is 26%.
- 294 non-S beats were predicted S, against 372 correct ones (285 of the 294 were N), so S precision is 56%.
- **163 of 556 S beats (29%) were called N.** This is the largest error for S.

### 4.4 Grad-CAM (read from `figures/06_gradcam_examples.png`)

All five beats shown were predicted with p = 1.00. Description of the heatmaps:

| Class | Where the heat is concentrated |
|---|---|
| N | A narrow band at the very start of the window (~0–0.1 s), and a band at ~1.15–1.3 s around the second peak and the drop into zero padding |
| S | A band at ~0.35–0.45 s over the second (sharp) peak and the drop into padding. Weak heat at t ≈ 0 |
| V | The start of the window, a broad medium-intensity region (~0.3–0.9 s) and a strong band at ~1.0–1.1 s where the signal ends |
| F | The start of the window and two narrow bands either side of the second peak (~0.4 s and ~0.53 s) |
| Q | The start of the window and a strong band at ~0.75–0.85 s over the second peak |

**[Interpretation]** In most examples the model attends to two places: the first samples of the window and the second large peak / end of the signal. In this dataset the first sample is at the current beat's R peak (per Kachuee et al.; the notebook does not say this), so the second peak is likely the next R peak. If so, the model is partly using **where the next beat occurs**, which is an implicit RR-interval cue, as well as morphology. The notebook does not test this. It is a hypothesis to check with region-based metrics. Heat at the exact window edge (t = 0) may also partly come from `padding='same'` edge effects. **[Unclear]**

### 4.5 Summary block printed by the notebook (cell 24)

```
Model parameters : 44,741
Epochs run       : 17
Test beats       : 21,892
Test accuracy    : 94.41%
Macro-F1         : 76.29%
  N: precision 98.1%  recall 95.9%  F1 97.0%
  S: precision 55.9%  recall 66.9%  F1 60.9%
  V: precision 87.1%  recall 86.0%  F1 86.6%
  F: precision 26.0%  recall 86.4%  F1 40.0%
  Q: precision 99.0%  recall 95.0%  F1 97.0%
```

---

## 5. Findings

### 5.1 What worked
- **A working end-to-end pipeline** (load → split → weighted training → evaluation → Grad-CAM) with a small model of 44,741 parameters.
- **N, Q and V are classified well**: F1 0.970, 0.970 and 0.866.
- **Class weighting got high recall on rare classes.** F recall is 86.4% even though F is only 0.73% of the training data.
- The evaluation is honest about imbalance: it reports macro-F1 and per-class scores, not only accuracy. The test set is used only once.
- **Grad-CAM runs** and gives sharp, localised heatmaps for every class.

### 5.2 What did not work
- **The macro-F1 of 76.29% hides poor rare-class precision.** F precision is 26.0% (about 3 of every 4 F predictions are wrong) and S precision is 55.9%.
- **S is the hardest class**: F1 0.609, and 29% of S beats are called N.
- **Training was very unstable.** Validation accuracy jumped between 14.5% and 95.1% from epoch to epoch (e.g. 0.8627 at epoch 5, then 0.3970 at epoch 6). Validation loss peaked at 4.29 at epoch 2 while training loss fell smoothly.
- **The model was still improving on the training set when it stopped**: training accuracy was 90.93% at epoch 17 and still rising. Early stopping on a noisy `val_loss` cut training short.

### 5.3 Why (based on the evidence in the outputs)
- **Weights that are too strong push the model to over-predict rare classes.** At a 113:1 F:N weight ratio, calling an N beat "F" costs little in the loss, while missing an F costs a lot. The confusion matrix shows exactly this: 293 N beats were predicted F. High recall paired with low precision is the typical sign of over-weighting.
- **[Interpretation] The unstable validation scores** are a gap between training-mode and inference-mode behaviour, not overfitting: training loss keeps falling smoothly while the validation scores swing. V2 later attributes this to slow batch-norm running statistics (momentum 0.99) together with large, heavily weighted gradients. V1 does not test this.
- **Choosing the epoch on validation loss** favours an epoch that is good on average, and on average that means good on class N. The project's main metric is macro-F1. V2 tests this as change E1.

### 5.4 Explainability
At this stage Grad-CAM is a **visual demonstration only**: one hand-picked (most confident) beat per class, with no quantitative measure. The heatmaps do look localised, and possibly physiologically meaningful (peaks / QRS regions). This cannot be claimed from V1's outputs.

### 5.5 Planned next steps stated in the notebook (cell 22)
The notebook lists these differences between the baseline and the planned framework: raw MIT-BIH from PhysioNet (MLII, 360 Hz), 252-sample beats around the R peak, own band-pass filtering and z-scoring, 4 classes (N/S/V/F, with Q removed), intra- **and** inter-patient (DS1/DS2) evaluation, RR-interval features, a CNN-LSTM + RR model, Grad-CAM and SHAP with region-share and deletion tests, and NSTDB noise at 18 / 6 / 0 dB. None of these are implemented in V1.

---

## 6. Limitations and issues

### 6.1 Methodological
1. **Intra-patient split (acknowledged by the notebook).** The Kaggle split is by beat, so the same patients appear in train and test. Scores will overestimate performance on new patients. This is the most important caveat for any reported number.
2. **Preprocessing is a black box.** All filtering and segmentation were done by the dataset authors. The project has not yet implemented its own pipeline.
3. **Zero-padded, variable-length content.** Each beat is padded to 187 samples. The length of the non-zero part varies with heart rate, so the model can use "where the padding starts" as a feature. **[Interpretation]** This may be useful (an RR cue) or a shortcut, and it affects how Grad-CAM should be read.
4. **Q class included.** Q (paced / unclassifiable) is easy here (F1 0.97) and pushes macro-F1 up. The planned framework drops it, so V1's macro-F1 is not directly comparable to a later 4-class macro-F1.
5. **Single run, single seed.** There are no repeats and no confidence intervals. With only 162 F test beats, a handful of beats moves F precision and recall by several points.
6. **Epoch selection on `val_loss`** does not match the macro-F1 objective, and the noisy validation loss caused an early stop.
7. **Class weights too strong** (F:N ≈ 113:1), which caused the over-prediction of F and S.

### 6.2 Explainability
8. Grad-CAM was run on **one beat per class**, chosen as the most confident correct one (the easiest cases). There is no failure case, no averaging and no quantitative metric.
9. Grad-CAM comes from `relu3` at **46-step resolution** and is linearly interpolated to 187 samples, so it is coarse (about 4 samples ≈ 32 ms per step).

### 6.3 Reproducibility and file issues
10. **`all_my_outputs/all_my_outputs.zip` is broken.** It is only 38 bytes, holds just the header for an empty `figures/` folder entry, and has no central directory. `unzip` reports "End-of-central-directory signature not found". It contains nothing usable.
11. **`all_my_outputs/best_model.h5` (1.48 MB) is not produced by any cell in the notebook.** The notebook only saves `baseline_1d_cnn.keras` (614 KB). Its origin is **[Unclear]**: it may be from a different or earlier run. It should not be treated as the baseline model without checking.
12. **TensorFlow version not printed.** The training log format ("Train on 70043 samples, validate on 17511 samples") is the style of older TF/Keras releases, but the model is saved in the newer `.keras` format. The exact environment is **[Unclear]**, which matters if V2 numbers are compared against V1 (V2 ran on TF 2.20.0).
13. **Execution counts are not contiguous** (4–10, then 12, 15–19). Some cells were re-run or edited after the first execution (e.g. cell 17's code style differs from the rest). The outputs shown are internally consistent: the CSV matches the printed table, and the confusion matrix matches precision and recall.
14. `.ipynb_checkpoints/` holds an autosave copy of the notebook. It is not an output.

---

## 7. Output file inventory

| File | Produced by | Contents |
|---|---|---|
| `all_my_outputs/baseline_results.csv` | Cell 17 | Per-class precision / recall / F1 / support (matches §4.2) |
| `all_my_outputs/baseline_1d_cnn.keras` | Cell 14 | Trained baseline model (best-val-loss weights) |
| `all_my_outputs/best_model.h5` | **Not produced by this notebook** | Unknown, see issue 11 |
| `all_my_outputs/all_my_outputs.zip` | Not produced by this notebook | Broken / empty, see issue 10 |
| `figures/01_class_distribution.png` | Cell 6 | Training-set class counts |
| `figures/02_example_beats.png` | Cell 8 | One beat per class |
| `figures/03_training_curves.png` | Cell 15 | Train / val accuracy and loss per epoch |
| `figures/04_confusion_matrix.png` | Cell 18 | Counts and row-normalised confusion matrices |
| `figures/05_per_class_scores.png` | Cell 19 | Per-class precision / recall / F1 bars |
| `figures/06_gradcam_examples.png` | Cell 21 | Grad-CAM, one beat per class |
