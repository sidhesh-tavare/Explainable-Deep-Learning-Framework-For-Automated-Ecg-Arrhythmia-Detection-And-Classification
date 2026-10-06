# Revised week plan (Scope v2)

> **Assumption:** Week 1 = week starting 2026-10-05, ~14 weeks to the final evaluation, mid-evaluation around the end of Week 3. Re-time once the real dates are known (`04_open_questions.md` Q1).

| Week | Dates (assumed) | Goal | Deliverable |
|---|---|---|---|
| 1 | 05–11 Oct | Environment; download MIT-BIH; AAMI mapping; DS1/DS2 beat extraction; RR features; class-count table | `data/` pipeline + counts table |
| 2 | 12–18 Oct | CNN v0 trained on DS1, tested on DS2 | Confusion matrix, per-class Se/+P/F1 |
| 3 | 19–25 Oct | CNN-BiLSTM + RR; first Grad-CAM overlays; **mid-evaluation slides** | Baseline table; 4 example maps (labelled "qualitative") |
| 4 | 26 Oct–1 Nov | Gradient SHAP; M4 Grad-CAM vs SHAP agreement | Side-by-side maps per class; agreement numbers |
| 5 | 2–8 Nov | M1 deletion faithfulness | Faithfulness curves (top-k vs random) |
| 6 | 9–15 Nov | M2 consistency + M3 P/QRS/T region overlap | Per-class table |
| 7 | 16–22 Nov | Download NSTDB; noise injection (MA, EM at 18/6/0 dB); F1 vs SNR | F1-vs-SNR plot |
| 8 | 23–29 Nov | **M5 explanation stability vs SNR** | Stability-vs-SNR plot per class and method |
| 9 | 30 Nov–6 Dec | 1–2 ablations (no RR features); bootstrap CI on macro-F1 | Small ablation table |
| 10 | 7–13 Dec | **Buffer.** Fix anything broken; stretch goals only if on track | — |
| 11 | 14–20 Dec | Report: methods + results chapters | Draft chapters 3–4 |
| 12 | 21–27 Dec | Report: intro, lit review, discussion, conclusion | Full draft |
| 13 | 28 Dec–3 Jan | Final figures, supervisor feedback, slides | Final report + slides |
| 14 | 4–10 Jan | Viva rehearsal (Study Guide §5.4 questions) | Submission |

Weeks saved vs the old plan: Pan-Tompkins (old wk 7), INCART (old wk 8), MC dropout (old wk 11), and half the ablation week, turned into a buffer week and an extra writing week.
