# Checklist (Scope v4)

## Week 1: data
- [ ] Install: `numpy scipy wfdb torch scikit-learn matplotlib captum streamlit`
- [ ] Download MIT-BIH (`wfdb.dl_database('mitdb', 'data/mitdb')`)
- [ ] Map labels to N, S, V, F; skip paced records 102, 104, 107, 217
- [ ] Filter 0.5–40 Hz, cut 252-sample beats around each annotated R peak, z-score
- [ ] RR features: previous RR, next RR (+ local average RR)
- [ ] Save beats, RR features, labels, record IDs to one `.npz`
- [ ] Class-count table

## Week 2–3: models
- [ ] Random 80/20 stratified split
- [ ] Plain CNN → accuracy, confusion matrix, per-class F1
- [ ] CNN-LSTM + RR → same metrics
- [ ] Grad-CAM on 1 beat per class
- [ ] Mid-evaluation slides

## Week 4: second split + SHAP
- [ ] DS1/DS2 run (record lists in Study Guide §1.9)
- [ ] SHAP (`captum.attr.GradientShap`) side by side with Grad-CAM

## Week 5: Upgrade A
- [ ] Region check: % attribution in P / QRS / T windows, per class
- [ ] Deletion check: top-10% vs random-10% → confidence drop

## Week 6: Upgrade B
- [ ] Download `nstdb`; function to add MA noise at a target SNR
- [ ] F1 vs SNR (18, 6, 0 dB), CNN vs CNN-LSTM
- [ ] Heatmap stability (clean vs noisy correlation)

## Week 7: Upgrade C
- [ ] Streamlit page: pick record/beat → signal, prediction, heatmap, noise slider

## Week 8+
- [ ] Freeze results → report → slides → viva practice
