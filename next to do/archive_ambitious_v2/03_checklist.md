# Checklist

## Right now (before coding)
- [ ] Answer the questions in `04_open_questions.md`
- [ ] Show `01_scope_v2.md` to the supervisor and get a yes / changes
- [ ] Decide: update mid-eval PPT and report draft to Scope v2 wording (`05_report_wording.md`)

## Week 1: data pipeline
- [ ] Python env: `numpy scipy wfdb torch scikit-learn matplotlib captum`; fix random seeds; one config file
- [ ] Download `mitdb` with `wfdb`
- [ ] Read one record + annotations; confirm MLII channel and gain in the `.hea` file
- [ ] AAMI mapping (N, S, V, F); drop non-beat symbols
- [ ] Exclude paced records 102, 104, 107, 217; build DS1 / DS2 lists (verify against de Chazal 2004)
- [ ] Hold out ~4 whole DS1 records for validation
- [ ] Band-pass 0.5–40 Hz with `filtfilt`
- [ ] Segment 252-sample beats, z-score; compute RR features
- [ ] Class-count table for DS1 / DS2 / validation

## Week 2–3: baseline
- [ ] CNN v0 → DS2 results
- [ ] CNN-BiLSTM + RR → DS2 results
- [ ] Sanity check: accuracy lies between min and max per-class recall
- [ ] First Grad-CAM overlays for one N, S, V and F beat
- [ ] Mid-evaluation slides

## Week 4–6: explanation metrics
- [ ] Gradient SHAP maps
- [ ] M4 Grad-CAM vs SHAP agreement
- [ ] M1 deletion faithfulness
- [ ] M2 within-class consistency
- [ ] M3 P / QRS / T region overlap

## Week 7–9: noise
- [ ] Download `nstdb`; noise-injection function at target SNR
- [ ] F1 vs SNR (MA, EM × 18 / 6 / 0 dB)
- [ ] M5 explanation stability vs SNR
- [ ] Ablation: without RR features; bootstrap CI

## Week 10+: buffer, then writing
