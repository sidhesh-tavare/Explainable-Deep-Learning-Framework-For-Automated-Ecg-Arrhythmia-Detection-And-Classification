# Literature Review: Explainable, Patient-Independent and Robust Deep Learning for ECG Arrhythmia Classification

> Source: every statement and number in this document comes from `literature_review.csv` (36 papers). Citation numbers [n] are the row numbers of the CSV, so each claim can be traced back to its row and its `page_refs`.

## 1. Literature Review

### 1.1 Architectures

CNNs are still the most common choice for ECG arrhythmia classification. They appear in 58.7% of the 368 studies reviewed by Xiao et al. [10] and in 62% of the 119 studies reviewed by Kulkarni et al. [12]. Earlier surveys also found CNNs to be the dominant and most effective deep learning method [8], [9]. Hybrid models are becoming more common. These pair a convolutional front end, which learns waveform shape, with a recurrent or attention module, which learns timing. Examples include CNN-LSTM models [1], [25], [26], CNN-BiLSTM models [15], [16], multi-scale CNN-BiLSTM networks [24] and dual-branch BiLSTM/capsule fusion [14].

Transformers are the newest step:
- bidirectional transformers [18], [36];
- CNN-BERT hybrids [23];
- Stockwell-transform CNN-transformers [21];
- a transformer with a large language model, which turns patient age and sex into text prompts [19].

In a meta-regression, attention/transformer models gained 0.845% over 1D-CNNs, but became costly beyond roughly 1 M parameters [12]. Lighter designs can still compete:
- a 0.16 MB CNN-LSTM ran at 5.127 ms per rhythm on a Raspberry Pi [1];
- a 165,061-parameter spatio-temporal CNN reached a macro AUC of 93.41% on PTB-XL, beating larger ResNets [28];
- a 197,093-parameter CNN-VAE achieved 87.01% binary accuracy on PTB-XL [30].

Other directions include graph networks over P-QRS-T segments [22] and interpretable handcrafted features with XGBoost [3].

### 1.2 XAI methods

SHAP is the most common explanation method in this set. It is used in [1], [2], [3], [4], [6], [7] and [28]. Gradient-based saliency maps are used less often: Grad-CAM in [5] and [19], and CAM in [21]. Jang et al. [29] took a different approach. They generated counterfactual ECGs, which showed rhythm irregularity and beat-to-beat variability that saliency maps missed.

Several studies report that explanations agree with clinical criteria:
- absent P waves and wide QRS [1];
- slurred S waves for RBBB and Sokolow-Lyon criteria for LVH [28];
- PR interval for first-degree AV block [3].

The evidence is weaker than it looks. Beck and John [2] found that explanations for APB and PVC beats did not match clinical understanding consistently, and varied across samples of the same class. They also removed the LSTM from their model because it interfered with the XAI methods. Their survey of 5 clinicians found that all of them preferred saliency maps to counterfactuals. Kulkarni et al. [12] report that fewer than 10% of studies checked explanation maps against clinically meaningful ECG structures.

### 1.3 Datasets and evaluation

MIT-BIH dominates. It is used in 61% of studies in [10], in 78.7% in [11] and in 78 of 119 in [12]. PTB-XL is the main 12-lead benchmark [19], [27], [28], [30].

The reported accuracies depend heavily on how the data are split:
- **Inter- vs intra-patient.** In 11 studies that reported both, F1 fell from 95.52% (intra-patient) to 83.89% (inter-patient) [10].
- **Within one paper.** Ibrahim [15] reports 99.00% accuracy on a beat-wise split but 91.69% on a patient-wise split, with Fusion recall of 0.021.
- **Adoption.** Only 30.3% of 122 reviewed articles used the inter-patient paradigm, and only 4.1% met all of the authors' four criteria: AAMI standards, inter-patient evaluation, MIT-BIH and embedded feasibility [11].
- **External validation.** It appeared in only 18.5% of studies, with an average accuracy drop of 8.7% [12]. Kolliyil and Brindise [3] saw about 16% lower performance on external data. Adding a second dataset cost Beck and John's model more than 20% [2].
- **Approaches that hold up.** Adversarial removal of patient-specific features raised atrial fibrillation (AFib) F1 from 61.0% to 77.9% under inter-patient testing [13]. Dual-branch fusion reached 99.55% on a subject-level split [14].

### 1.4 Robustness

Noise robustness is tested unevenly:
- Hassoon et al. [14] tested only additive white Gaussian noise (AWGN), and their F1 fell to 32.46% at 5 dB.
- Tenepalli and Navamani [5] did not test under noise at all.
- Huang et al. [36] state that performance on wearable signals with motion artifacts has not been verified.
- Reddy et al. [24] kept 96.26% accuracy under added Gaussian noise.
- Ashhad et al. [34] used Dempster-Shafer uncertainty-aware fusion, which was more robust than score- or feature-level fusion against Noise Stress Test Database (NSTDB) baseline wander, muscle artifact and electrode motion noise at 15–0 dB.

Denoising front ends include:
- wavelet methods [16], [24], [36];
- adaptive LMS filtering [31];
- a Jacobian-regularized denoising autoencoder [35]. Its authors note it has not yet been tested for diagnosis.

Uncertainty estimation is a complementary safeguard. Zhang et al. [33] rejected high-uncertainty predictions, which raised macro F1 from 0.6635 to 0.8688. Cardiologists then traced most high-uncertainty cases to noise.

## 2. Comparison of the 8 Most Relevant Papers

| Ref | Dataset(s) | Model | XAI | Split | Key result | Main limitation (author-stated) |
|---|---|---|---|---|---|---|
| [1] Alamatsaz 2024 | MIT-BIH + LTAF | Lightweight CNN-LSTM | SHAP | Not stated (85/15) | Acc 98.24%, Se 86.1%, 0.16 MB, 5.127 ms on Raspberry Pi | Poor AFIB/B/T identification; 2 leads, 2 databases |
| [2] Beck 2025 | MIT-BIH + 12-lead (Zheng et al.) | 1D CNN | 4 SHAP variants; saliency vs counterfactual | Not stated (80/20) | Val acc 98.30% (MIT-BIH); 73.45% combined; 5/5 clinicians preferred saliency | Explanations inconsistent within a class; not validated by medical professionals |
| [3] Kolliyil 2025 | CPSC 2018; external CPSC-extra, PTB-XL, G12EC | Handcrafted features + XGBoost | SHAP | Not stated (10-fold CV; external test) | CV macro F1 77%; external macro F1 0.65 vs 0.16 (CNN) | ~16% lower on external data; limited features for PVC/STD/STE |
| [13] Jeong 2024 | MIT-BIH; Chapman-Shaoxing | SE-ResNet with adversarial patient-invariant beat-score maps | Not stated | Inter-patient | AFib F1 77.9% vs 61.0% baseline; SPH F1 87.36% | Cross-database room for improvement; binary task on MIT-BIH |
| [14] Hassoon 2026 | MIT-BIH; INCART, SVDB, PTB | Dual-branch CNN-BiLSTM + CapsNet fusion | Branch contribution weights | Inter-patient (by subject) | Acc 99.55%; F1 S 95.37%, F 90.06% | AWGN only; F1 32.46% at 5 dB; 3.78 M params |
| [15] Ibrahim 2026 | MIT-BIH | CNN-BiLSTM + cGAN augmentation | Not stated | Both | Beat-wise 99.00% vs patient-wise 91.69%; F recall 0.021 | Single patient-wise split; no external validation |
| [28] Anand 2022 | PTB-XL; Chapman | ST-CNN-GAP-5 (165,061 params) | SHAP with clinical validation | Inter-patient (PTB-XL folds) | Macro AUC 93.41%; Chapman macro F1 95.79% | No explicit limitations section; cross-dataset generalization a stated challenge |
| [34] Ashhad 2025 | MIT-BIH; INCART; NSTDB | BiLSTM + ViT (GAF) with Dempster-Shafer fusion | Not stated | Not stated (80/20) | Acc 98.8% / 99.5%; robust 15–0 dB NSTDB noise | No explicit limitations; INCART limited to 3 classes |

## 3. Research Gaps

**Gap 1: Explanations are rarely checked against clinical knowledge, and they are often inconsistent.**
SHAP and Grad-CAM are widely applied [1], [3], [4], [5], [7]. However, fewer than 10% of studies validated explanation maps against clinical ECG structures [12]. Beck and John [2] found explanations that were inconsistent within a class, and links to medical knowledge that trained professionals had not validated. Only a few papers had clinicians or cardiologists check the highlighted waveforms [28], [29].

**Gap 2: Explainability is seldom combined with patient-independent evaluation.**
Several XAI studies give no patient separation for their splits [1], [2], [4], [5]. The reported accuracies are therefore likely to be inflated, given the inter-patient drop in [10] (F1 95.52% → 83.89%) and [15] (99.00% → 91.69%). Only 30.3% of reviewed studies used the inter-patient paradigm [11]. Inter-patient studies that report strong results often have no XAI [13], [15], [16].

**Gap 3: Robustness to realistic noise is tested narrowly and is not linked to explanations.**
Noise tests are limited to AWGN [14] or Gaussian noise [24], or are missing entirely [5], [36]. NSTDB-based robustness testing [34] and the denoising work [35] report no explanation analysis. None of the 36 papers in the CSV checks whether explanations stay stable when noise is added. Zhang et al. [33] show that noise is a main source of predictive uncertainty.

**Gap 4: Minority classes and external generalization remain weak.**
Patient-wise Fusion and S recall reached only 0.021 and 0.209 [15]. F and S remain the hardest classes in [18], [25], [32] and [36]. Only 18.5% of studies validate externally, with an average accuracy drop of 8.7% [12], and external performance falls in [2] and [3].

## 4. Project Objectives

1. **Patient-independent baseline.** Develop a hybrid deep learning arrhythmia classifier and evaluate it under a strict inter-patient protocol (MIT-BIH DS1/DS2), with external testing on a second database. Report per-class and macro F1 alongside accuracy. *(Gaps 2, 4)*
2. **Validated explanations.** Apply at least two post-hoc XAI methods (for example SHAP and Grad-CAM) to the patient-independent model. Measure how consistent the explanations are within each class and how well they match recognized ECG features (P wave, QRS, RR interval). *(Gaps 1, 2)*
3. **Robustness of predictions and explanations.** Assess how classification performance and explanation stability degrade under realistic NSTDB noise (baseline wander, muscle artifact, electrode motion) at graded SNRs, using uncertainty estimates to flag unreliable predictions. *(Gaps 3, 4)*

## 5. References

*Numbered to match the CSV rows. Volume, issue and page details are given only where the CSV records them.*

[1] N. Alamatsaz, L. Tabatabaei, M. Yazdchi, H. Payan, N. Alamatsaz, and F. Nasimi, "A lightweight hybrid CNN-LSTM explainable model for ECG-based arrhythmia detection," *Biomedical Signal Processing and Control*, vol. 90, Art. no. 105884, 2024.

[2] J. Beck and A. John, "Explainable AI (XAI) for arrhythmia detection from electrocardiograms," arXiv:2508.17294, 2025.

[3] J. J. Kolliyil and M. C. Brindise, "Automated detection of arrhythmias using a novel interpretable feature set extracted from 12-lead electrocardiogram," *Computers in Biology and Medicine*, vol. 189, Art. no. 109957, 2025.

[4] M. A. Talukder, A. S. Talaat, N. J. Muna, A. Alazab, M. Kazi, and U. K. Das, "An explainable deep learning framework for trustworthy arrhythmia detection from ECG signals," *Scientific Reports*, vol. 15, Art. no. 39496, 2025.

[5] D. Tenepalli and T. M. Navamani, "Design of an explainable deep learning framework for ECG-based arrhythmia prediction," *IEEE Access*, vol. 13, pp. 200754–, 2025, doi: 10.1109/ACCESS.2025.3636481.

[6] V. Asha, P. Kavitha, R. Sri Gokulam, S. Ciyamala Kushbu, M. Jayashree, and N. Gayathri, "ECG arrhythmia classification a lightweight, explainable, and web-deployable deep learning framework using knowledge-distilled GAN features and Flask," *Natural Resources for Human Health*, vol. 6, no. 14s, pp. 289–296, 2026.

[7] P. Kavitha and L. Shakkeera, "An explainable deep learning framework for accurate and automated cardiac arrhythmia classification using electrocardiogram signals," *Biomedical Signal Processing and Control*, vol. 117, Art. no. 109590, 2026.

[8] Z. Ebrahimi, M. Loni, M. Daneshtalab, and A. Gharehbaghi, "A review on deep learning methods for ECG arrhythmia classification," *Expert Systems with Applications: X*, vol. 7, Art. no. 100033, 2020.

[9] Y. Ansari, O. Mourad, K. Qaraqe, and E. Serpedin, "Deep learning for ECG arrhythmia detection and classification: An overview of progress for period 2017–2023," *Frontiers in Physiology*, vol. 14, Art. no. 1246746, 2023.

[10] Q. Xiao, K. Lee, S. A. Mokhtar, I. Ismail, A. L. bin Md Pauzi, Q. Zhang, and P. Y. Lim, "Deep learning-based ECG arrhythmia classification: A systematic review," *Applied Sciences*, vol. 13, Art. no. 4964, 2023.

[11] G. A. L. Silva, P. H. L. Silva, G. J. P. Moreira, V. L. S. Freitas, J. C. Gertrudes, and E. J. S. Luz, "A systematic review of ECG arrhythmia classification: Adherence to standards, fair evaluation, and embedded feasibility," arXiv:2503.07276, 2025.

[12] N. N. Kulkarni, Nagaraja G. S., B. G. Sudarshan, and Yeriswamy M. C., "Recent advances in deep learning based arrhythmia classification using ECG and PPG signals: A systematic review," *Discover Computing*, vol. 29, Art. no. 666, 2026.

[13] Y. Jeong, J. Lee, and M. Shin, "Enhancing inter-patient performance for arrhythmia classification with adversarial learning using beat-score maps," *Applied Sciences*, vol. 14, Art. no. 7227, 2024.

[14] B. A. Hassoon, S. Xiong, M. A. Hasson, R. Salahudeen, A. O. Abdulsalami, and T. Khan, "Dual-branch bidirectional attention fusion of temporal and hierarchical representations for robust ECG arrhythmia classification," *Expert Systems with Applications*, vol. 331, Art. no. 133409, 2026.

[15] Sa. I. Ibrahim, "A hybrid deep learning algorithm for ECG-based heart disease classification," *Scientific Reports*, vol. 16, Art. no. 29911, 2026.

[16] S. Qin, L. Han, X. Zhang, Y. Zhang, and N. Li, "ECG beat classification based on dilated multi-scale ResNet and BiLSTM," *Measurement Science and Technology*, vol. 37, Art. no. 285701, 2026.

[18] H. El-Ghaish and E. Eldele, "ECGTransForm: Empowering adaptive ECG arrhythmia classification framework with bidirectional transformer," *Biomedical Signal Processing and Control*, vol. 89, Art. no. 105714, 2024.

[19] Q. Chen, C. Lian, B. Xu, Q. Zhou, Y. Su, and Z. Zeng, "Large language model-assisted multi-scale hierarchical classification of ECG signals," *Knowledge-Based Systems*, vol. 324, Art. no. 113807, 2025.

[21] D. Kim, K. R. Lee, D. S. Lim, K. H. Lee, J. S. Lee, D.-Y. Kim, and C.-B. Sohn, "A novel hybrid CNN-transformer model for arrhythmia detection without R-peak identification using stockwell transform," *Scientific Reports*, vol. 15, Art. no. 7817, 2025.

[22] M. Lee, J. Lim, and J. Kim, "ECG-GraphNet: Advanced arrhythmia classification based on graph convolutional networks," *Heart Rhythm O2*, vol. 6, no. 8, pp. 1199–1211, 2025.

[23] H. Liu, "A hybrid model combining 1D-CNN and BERT for intelligent ECG arrhythmia classification," *Scientific Reports*, vol. 15, Art. no. 44456, 2025.

[24] K. K. Reddy C., A. Daduvy, V. S. Kaza, M. Shuaib, M. Mohzary, S. Alam, and A. Sheneamer, "A multi-scale convolutional LSTM-dense network for robust cardiac arrhythmia classification from ECG signals," *Computers in Biology and Medicine*, vol. 191, Art. no. 110121, 2025.

[25] P. Pramkeaw, W. Leangruttananon, P. Suksomboon, T. Tapianthong, and S. Kitdanarakorn, "Deep learning-based ECG arrhythmia detection system: A comparative study of CNN, RNN, and LSTM architectures," in *Proc. 2026 IEEE Int. Conf. Cybernetics and Innovations (ICCI)*, 2026, doi: 10.1109/ICCI68752.2026.11506504.

[26] Y. Wang and S. Rani, "Hybrid CNN-LSTM model for ECG-based arrhythmia detection in internet of medical things," *Discover Internet of Things*, vol. 6, Art. no. 7, 2026.

[27] S. Smigiel, K. Palczynski, and D. Ledzinski, "ECG signal classification using deep learning techniques based on the PTB-XL dataset," *Entropy*, vol. 23, Art. no. 1121, 2021.

[28] A. Anand, T. Kadian, M. K. Shetty, and A. Gupta, "Explainable AI decision model for ECG data of cardiac disorders," *Biomedical Signal Processing and Control*, vol. 75, Art. no. 103584, 2022.

[29] J.-H. Jang, Y.-Y. Jo, S. Kang, J. M. Son, H. S. Lee, J. Kwon, and M. S. Lee, "A novel XAI framework for explainable AI-ECG using generative counterfactual XAI (GCX)," *Scientific Reports*, vol. 15, Art. no. 23608, 2025.

[30] N. A. Mehdi and A. A. Drigh, "ECG classification on PTB-XL: A data-centric approach with simplified CNN-VAE," arXiv:2603.07558, 2026.

[31] R. S. Pashikanti, A. A. Shinde, and C. Y. Patil, "Adaptive predictive control-based noise cancellation with deep learning for arrhythmia classification from ECG signals," in *Proc. 2022 Int. Conf. Intelligent Innovations in Engineering and Technology (ICIIET)*, 2022, doi: 10.1109/ICIIET55458.2022.9967602.

[32] K. Mallikarjunamallu and S. Khasim, "Arrhythmia classification using noise filtering and 1D CNN," *Traitement du Signal*, vol. 41, no. 4, pp. 1847–1859, Aug. 2024.

[33] W. Zhang, X. Di, G. Wei, S. Geng, Z. Fu, and S. Hong, "Cardiac arrhythmia classification with rejection of ECG recordings based on uncertainty estimation from deep neural networks," *Neural Computing and Applications*, vol. 36, pp. 4047–4058, 2024.

[34] M. Ashhad, S. Rahmani, M. Fayiz, A. Etemad, and J. Hashemi, "Uncertainty-aware multi-view arrhythmia classification from ECG," arXiv:2506.06342, 2025 (published at IJCNN 2024).

[35] J. P. Maurya, M. Manoria, and S. Joshi, "A proposed deep learning model for multichannel ECG noise reduction," *Discover Artificial Intelligence*, vol. 5, Art. no. 65, 2025, doi: 10.1007/s44163-025-00292-y.

[36] S. Huang, S. Chen, Z. Guo, K. Ji, and M. Zhang, "MSCA-TNet based deep learning method for ECG arrhythmia classification," *Scientific Reports*, vol. 16, Art. no. 28152, 2026, doi: 10.1038/s41598-026-58850-y.
