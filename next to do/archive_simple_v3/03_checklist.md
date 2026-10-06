# Checklist (Scope v3)

## Week 1: data
- [ ] Install: `numpy scipy wfdb torch scikit-learn matplotlib captum`
- [ ] Download MIT-BIH (`wfdb.dl_database('mitdb', 'data/mitdb')`)
- [ ] Map labels to N, S, V, F; skip paced records 102, 104, 107, 217
- [ ] Filter 0.5–40 Hz, cut 252-sample beats around each annotated R peak, z-score
- [ ] Save beats + labels to one `.npz` file
- [ ] Class-count table

## Week 2–3: models
- [ ] Random 80/20 split (stratified)
- [ ] Plain CNN → accuracy, confusion matrix, per-class F1
- [ ] CNN-LSTM → same metrics
- [ ] Grad-CAM on 1 beat per class
- [ ] Mid-evaluation slides

## Week 4–5: extra results
- [ ] DS1/DS2 inter-patient run (same code, record lists from Study Guide §1.9)
- [ ] Grad-CAM figure grid (e.g. 3 beats × 4 classes)
- [ ] (Optional) SHAP side by side

## Week 6–7
- [ ] (Optional) Streamlit demo
- [ ] Tidy code, freeze results

## Week 8+
- [ ] Report → slides → viva practice
