# FYP Study Guide
**Project:** Explainable Deep Learning Framework for Automated ECG Arrhythmia Detection and Classification

---

## Progress log

| Item | Status |
|---|---|
| Inputs checked | Done (2026-10-05). `papers/index.csv` (39 PDFs), `papers/literature_review.csv` (36 rows), `papers/literature_review.md` all present and non-empty. |
| Stage 1: Foundations | **Done** (2026-10-05) |
| Stage 2: Batch plan | **Drafted** (2026-10-05). You asked me to run Stages 2–5 without stopping, so the plan was not approved separately. |
| Stage 3: Batch reviews | **8 of 8 batches drafted** (37 papers) |
| Stage 4: Synthesis | **Drafted**, including the contradiction check against `literature_review.md` (§4.5) |
| Stage 5: Next steps | **Drafted.** The week plan assumes Week 1 = 2026-10-05 and about 14 weeks to the final evaluation |

**Decisions I took while you were away (all reversible)**
1. **ECGformer included.** I added it as **row 37** of `papers/literature_review.csv`, using only facts from its PDF. The original CSV is backed up at `papers/literature_review.csv.bak`.
2. **Two PDFs excluded as off-topic:** the phishing-detection paper and *V-NET-VGG16* (liver-tumour CT). Neither contains any ECG content. They are still in `papers/_unsorted/`.
3. **No existing CSV rows changed.** All key-result numbers in rows 1–36 were found in the PDF text. Four that the text extraction could not read, because they were inline equations, were confirmed from page images: [12] 8.7 ± 2.1 and 13.2 ± 3.4 (p.50), and [15] χ² = 12.41 (p.1).
4. **`literature_review.md` not edited.** Suggested fixes are listed in Stage 4 §4.5.

**Open questions for you**
1. Apply the §4.5 fixes to `literature_review.md` (paper count 36 → 37; wording on "clinicians checked" for [28] and [29]; acknowledge [7] and [28] under Gap 2)?
2. What are your real **mid-evaluation** and **final evaluation** dates? I will re-time Stage 5.3.
3. Is a clinician (e.g. from a hospital you are linked with) available to rate a few explanations? This would strengthen objective 2.
4. Do you agree with the **4-class (N, S, V, F)** default, which drops Q after the paced records are excluded (Stage 5.1 step 9)?
5. Notes: the review files are in `papers/`, not the root. CSV rows 17 and 20 are not cited in `literature_review.md`.

---

# STAGE 1: Foundations

> **How to read this stage.** Each section builds on the previous one. Background facts come from general knowledge. Anything I am not fully sure of is marked **(verify)**. Check those against the dataset documentation or a textbook before you put them on a slide. Numbers about specific papers are labelled with the paper's row number `[n]` in `literature_review.csv`, plus the page given in that CSV. I will re-check each one against the PDF in Stage 3.

---

## 1.1 What the heart's electrical signal is, and what an ECG records

### Plain language
The heart is a pump made of muscle. A muscle cell contracts only when it receives an electrical "go" signal. So every heartbeat starts as an electrical event, and the squeeze follows a fraction of a second later.

That electrical signal does not appear everywhere at once. It starts at one spot and spreads through the heart as a wave, along a fixed route. As the wave moves through millions of cells, it creates small electrical currents. Those currents flow through the body's tissues out to the skin. Electrodes on the skin can pick up the voltage they create, which is about **1 millivolt** (one-thousandth of a volt).

An **ECG (electrocardiogram)** is a graph of that skin voltage against time.

### Building it up step by step

**Step 1: a single cell.** At rest, the inside of a heart muscle cell is negative compared with the outside, at about −90 mV for a ventricular cell **(verify the exact figure)**. When the cell is triggered, positive ions (mainly sodium, Na⁺) rush in and the inside briefly turns positive. This flip is called **depolarization**. The cell then pumps ions back and returns to rest, which is called **repolarization**.
- Depolarization comes first, and the contraction follows it.
- Repolarization is the "reset" that has to happen before the next beat.

**Step 2: a wave of cells.** Each cell triggers its neighbour, so depolarization travels across the heart like a Mexico wave in a stadium. Along the edge of that wave, one side is already depolarized and the other is not. That edge acts like a small battery (an "electrical dipole") pointing in the direction the wave travels.
- A wave moving **towards** a skin electrode makes that electrode read positive, so the trace goes up.
- A wave moving **away** makes it read negative, so the trace goes down.

**Step 3: the conduction route.** The heart has a dedicated wiring system that sets the order in which chambers are activated:

```
  SA node  (natural pacemaker, top of right atrium; fires ~60-100 times/min)
     |
     v
  Atria depolarize  ---------------->  atria contract (push blood into ventricles)
     |
     v
  AV node  (deliberate DELAY ~0.1 s, so the atria finish emptying)
     |
     v
  Bundle of His
     |
     +--> Left bundle branch --+
     +--> Right bundle branch -+--> Purkinje fibres --> Ventricles depolarize
                                                        --> ventricles contract
                                                            (pump blood to body/lungs)
     ...then ventricles repolarize (reset)
```

**Step 4: what a "lead" is.** One ECG trace is the voltage **difference** between electrodes, or between one electrode and an average of several. Each such combination is called a **lead**. A lead "looks at" the heart from one direction, a bit like a camera angle.
- A standard clinical ECG uses **10 electrodes** to make **12 leads** (12 views).
- An ambulatory (Holter) recorder often records only **2 leads**.

**Step 5: turning it into numbers.** An ECG machine **samples** the voltage many times a second and stores each sample as an integer. Two settings describe this:
- **Sampling rate (fs):** how many samples are taken per second, in hertz (Hz).
- **Gain:** how many integer units correspond to 1 mV.

### Worked example (real numbers)
The MIT-BIH database records at **fs = 360 Hz**. Its header files typically give a **gain of 200 units per mV** **(verify in a `.hea` file)**.
- 1 second of signal = 360 samples. A 30-minute record = 30 × 60 × 360 = **648,000 samples per lead**.
- Suppose an R peak is stored as the integer 1264 and the baseline (offset) is 1024. The height is (1264 − 1024) / 200 = **1.2 mV**.
- The time between neighbouring samples is 1/360 s = **2.78 ms**.

### Say it in the viva
> "Every heartbeat starts as an electrical wave. It starts in the SA node, crosses the atria, pauses at the AV node, then spreads through the ventricles. This wave creates millivolt-level potentials on the skin. An ECG is the record of those potentials over time, seen from different angles called leads, and sampled into numbers. MIT-BIH, for example, samples at 360 Hz."

---

## 1.2 P wave, QRS complex, T wave, RR interval

### Plain language
Each bump on an ECG trace corresponds to one physical event from the route above. Once you know which event makes which bump, you can "read" a heartbeat.

```
 Voltage
   ^                    R
   |                    /\
   |                   /  \
   |       P          /    \                 T
   |      / \        /      \             _--_
   |_____/   \______/        \   ________/    \__________   <- baseline
   |                Q         \ /
   |                           S
   +--------------------------------------------------------> time
         |<- PR ->|<-QRS->|<-- ST -->|
         |<------------ QT ---------------------->|
   One beat. The next beat's R peak follows after the "RR interval".
```

### Formal definitions

| Feature | Physical event | Typical normal value (adult, resting) |
|---|---|---|
| **P wave** | Atria depolarize | Duration < 0.12 s; small, < 0.25 mV **(verify)** |
| **PR interval** | Start of P to start of QRS. Mostly the AV-node delay | 0.12–0.20 s |
| **QRS complex** | Ventricles depolarize. Q is the first downward deflection, R the first upward one, S the downward one after R. It is big because the ventricles have much more muscle than the atria. | 0.06–0.10 s (< 0.12 s); R often 0.5–2 mV |
| **ST segment** | Ventricles fully depolarized, so the trace is flat | Should sit near baseline |
| **T wave** | Ventricles repolarize (reset) | Usually upright in lead II |
| **QT interval** | Whole ventricular cycle | ~0.35–0.44 s; depends on heart rate **(verify)** |
| **RR interval** | Time from one R peak to the next | 0.6–1.0 s at rest (60–100 bpm) |

Atrial **re**polarization happens too, but it is tiny and is hidden inside the much larger QRS.

**Heart rate from RR:** HR (beats per minute) = 60 / RR (seconds).

### Worked example
At fs = 360 Hz, a detector finds R peaks at sample numbers **1000, 1290, 1574, 1760, 2120**.

| Beat pair | Samples apart | RR (s) | HR (bpm) |
|---|---|---|---|
| 1000 → 1290 | 290 | 290/360 = 0.806 | 74.5 |
| 1290 → 1574 | 284 | 0.789 | 76.1 |
| 1574 → **1760** | 186 | **0.517** | 116 |
| 1760 → 2120 | 360 | **1.000** | 60 |

The beat at sample 1760 arrived **early**: its RR is only 0.517 / 0.79 ≈ **65%** of the usual value. The gap after it is **long** (1.000 s). An early beat followed by a long pause is the classic sign of a **premature beat**. This is why many models use **pre-RR**, **post-RR** and **local average RR** as extra inputs alongside the beat's shape.

### Why a machine learning model cares
Each arrhythmia class changes one or more of these features:
- A missing P wave suggests the beat did not start in the atria.
- A wide QRS suggests the beat started in the ventricle.
- A short pre-RR means the beat came early.

A good model, and a good explanation, should be paying attention to exactly these regions.

### Say it in the viva
> "The P wave is atrial depolarization, the QRS complex is ventricular depolarization, and the T wave is ventricular repolarization. The RR interval is the time between successive R peaks, and heart rate is 60 divided by RR. Arrhythmias show up as changes in these: a missing P wave, a wide QRS, or an RR interval that is too short or irregular."

---

## 1.3 What an arrhythmia is, and the AAMI classes

### Plain language
An **arrhythmia** is any heartbeat or rhythm that is abnormal in **rate** (too fast or too slow), **regularity**, **where it starts** (its origin), or **how it is conducted**. Some are harmless, like an occasional extra beat. Others can kill, like ventricular fibrillation.

There are two levels of task:
- **Beat-level:** label every single heartbeat (normal, premature ventricular, ...). MIT-BIH is built for this.
- **Rhythm/record-level:** label a stretch of signal, for example "this 10-s ECG shows atrial fibrillation" or "this ECG shows a myocardial infarction". PTB-XL is built for this.

### The AAMI classes (formal)
MIT-BIH cardiologists labelled beats with about 15+ detailed beat types. Every paper used to group them differently, which made results impossible to compare. The **AAMI EC57** standard (from the Association for the Advancement of Medical Instrumentation) fixes a grouping into 5 classes, based mainly on **where the beat originated**.

| AAMI class | Meaning | MIT-BIH beat types grouped in it | What it looks like |
|---|---|---|---|
| **N**: Normal / non-ectopic | Beat starts in the SA node and follows the normal route (or a bundle-branch route) | Normal (N), Left bundle branch block (L), Right bundle branch block (R), Atrial escape (e), Nodal/junctional escape (j) | Normal P, then QRS at the expected time |
| **S**: Supraventricular ectopic | Beat starts early from somewhere **above** the ventricles (atria or AV node) | Atrial premature (A), Aberrated atrial premature (a), Nodal premature (J), Supraventricular premature (S) | **Early**, usually **narrow** normal-looking QRS; P wave abnormal or hidden. **Hard: it looks almost like N.** |
| **V**: Ventricular ectopic | Beat starts early **in the ventricle** itself | Premature ventricular contraction (V), Ventricular escape (E) | **Wide, bizarre QRS** (> 0.12 s), no P before it, T often in the opposite direction, then a long pause |
| **F**: Fusion | A normal wave and a ventricular wave fire at the same moment and collide | Fusion of ventricular and normal (F) | Shape in between N and V. **Very rare and very hard.** |
| **Q**: Unknown / paced | Pacemaker beats or beats that could not be classified | Paced (/), Fusion of paced and normal (f), Unclassifiable (Q) | Pacemaker spike; often **excluded** |

The 4 MIT-BIH records with pacemakers (102, 104, 107, 217) are usually removed under the AAMI recommendations **(verify)**.

### Worked example: how imbalanced it is
Approximate MIT-BIH beat counts after AAMI grouping **(verify; exact counts differ between papers)**:

```
N  ~90,000  ##############################################  (~89%)
V   ~7,000  ####                                            (~7%)
S   ~2,800  ##                                              (~3%)
F     ~800  .                                               (~0.8%)
```

A model that always answers "N" would already be about 89% "accurate". Keep this in mind for section 1.10.

### Say it in the viva
> "An arrhythmia is an abnormality in the rate, rhythm, origin or conduction of the heartbeat. Following the AAMI EC57 standard, we group MIT-BIH beat labels into five classes by where the beat originates: N for normal, S for supraventricular ectopic, V for ventricular ectopic, F for fusion, and Q for paced or unknown. S and F are the hardest, because S looks almost normal and F is both rare and a mix of N and V."

---

## 1.4 Why detecting it by hand is hard, and why automate it

### Plain language
A doctor can read one 10-second ECG well. The problem is volume, fatigue, rare events and noise.

1. **Volume.** A 24-hour Holter recording at 75 bpm contains 75 × 60 × 24 = **108,000 beats**. Nobody can inspect each one.
2. **Rare events.** The dangerous beat may be 1 in 10,000, and missing it is what matters.
3. **Subtle differences.** An S beat differs from an N beat mainly in timing and a small P-wave change.
4. **Every person's ECG looks different.** Body shape, electrode position and heart orientation change the waveform. A "normal" beat for one patient can look like an abnormal beat for another. (This matters a lot in section 1.9.)
5. **Noise.** Real recordings are contaminated by:
   - **Baseline wander:** slow drift caused by breathing and movement (below about 0.5 Hz).
   - **Muscle (EMG) noise:** fast, fuzzy interference when the patient moves their muscles.
   - **Electrode motion artifact:** sudden jumps when the electrode–skin contact changes.
   - **Powerline interference:** 50 Hz in India and Europe, 60 Hz in the US.
6. **Inter-observer variability.** Two experts sometimes label the same beat differently.

### Why automate
- **Screening at scale:** wearables and Holters produce far more data than cardiologists can read.
- **Triage:** flag the suspicious minutes so the doctor reviews only those.
- **Consistency:** an algorithm does not get tired at 3 a.m.

**But** an automated system that cannot justify its decisions will not be trusted in a clinic. That is where "explainable" comes in (sections 1.11–1.12).

### Say it in the viva
> "Manual reading does not scale. A day of Holter data is around a hundred thousand beats, and the dangerous ones are rare. They can also differ only subtly from normal beats, waveforms vary between people, and noise corrupts the signal. Automation provides consistent, scalable screening, but clinicians will only trust it if it can show why it made each decision."

---

## 1.5 The pipeline: raw signal → denoise → R-peak detection → beat segmentation → model → class

### Overview diagram

```
 +-----------+   +-----------+   +-------------+   +--------------+   +---------+   +---------+
 | Raw ECG   |-->| Denoise   |-->| R-peak      |-->| Beat         |-->| Model   |-->| Class   |
 | integers, |   | remove    |   | detection   |   | segmentation |   | (CNN,   |   | N/S/V/F |
 | 360 Hz    |   | drift,    |   | find each   |   | cut a window |   |  LSTM,  |   | + prob. |
 |           |   | 50 Hz,    |   | heartbeat's |   | around each  |   |  ...)   |   |         |
 |           |   | EMG       |   | R peak      |   | R; add RR    |   |         |   |         |
 +-----------+   +-----------+   +-------------+   +--------------+   +---------+   +---------+
                                                                          |
                                                                          v
                                                                  +----------------+
                                                                  | Explanation    |
                                                                  | (Grad-CAM,     |
                                                                  |  SHAP, ...)    |
                                                                  +----------------+
```

### Step 1: Raw signal
**What:** integer samples plus a header that gives fs and gain.
**Why:** this is all the hardware gives us.
**Example:** integer 1264 with offset 1024 and gain 200 → 1.2 mV (section 1.1).

### Step 2: Denoise
**What:** remove frequency content that is not heart activity.
**Why:** otherwise the model may learn the noise, and R-peak detection fails.

Key idea: **every kind of noise lives in a different frequency range**, so a filter can remove it while keeping the ECG.

```
 Frequency (Hz):  0   0.5          5      15       40      50        100+
                  |----|-----------|-------|--------|-------|---------|
 Baseline wander  ####
 P / T waves         ######
 QRS energy                  ###########
 Powerline                                                 #
 Muscle noise                         ################################
 A typical band-pass keeps roughly 0.5-40 Hz (verify: papers use various bands)
```

**Worked example:** a patient breathes 15 times a minute. That is 15/60 = **0.25 Hz**. A high-pass filter with a 0.5 Hz cut-off removes this drift, but keeps the QRS, whose energy sits mostly around 5–15 Hz.

Common methods:
- **Band-pass filters:** Butterworth filters.
- **Median filters for baseline removal:** for example, 200 ms and then 600 ms windows **(verify)**.
- **Wavelet denoising:** split the signal into frequency bands, shrink the small noisy coefficients, then rebuild.
- **Notch filter:** removes exactly 50 Hz or 60 Hz.

### Step 3: R-peak detection
**What:** find the sample index of every R peak.
**Why:** the R peak is the tallest and sharpest feature, so it is the easiest anchor for "a beat happened here".

The classic algorithm is **Pan–Tompkins (1985)**:
1. Band-pass at ~5–15 Hz, which keeps QRS energy.
2. **Differentiate**, which highlights steep slopes.
3. **Square**, which makes everything positive and makes big slopes much bigger than small ones.
4. **Moving-window integration** (~150 ms), which merges the QRS into one hump.
5. **Adaptive threshold:** declare a peak where the hump crosses a threshold that adjusts to recent signal levels.

**Worked example of squaring.** Suppose the derivative values are `[0.1, 0.5, −0.6, 0.05]`. Squaring gives `[0.01, 0.25, 0.36, 0.0025]`. The steep QRS slopes (0.5 and −0.6) now stand far above the gentle P/T slopes (0.1 and 0.05), so they are easy to threshold.

> **Honesty point for the viva.** Many MIT-BIH papers do **not** run a detector at all. They use the R-peak positions from the expert annotation file. That makes results look better than a real deployment would. I will check this paper by paper in Stage 3.

### Step 4: Beat segmentation
**What:** cut a fixed-length window around each R peak.
**Why:** the model needs fixed-size inputs, one beat each.

**Example:** at 360 Hz, take 0.25 s before R (90 samples) and 0.45 s after R (162 samples). That gives **252 samples** per beat. The window covers the P wave (about 0.2 s before R) and the T wave (about 0.3–0.4 s after R). The exact window varies by paper.

Cutting out one beat **throws away timing information**, so pre-RR, post-RR and average RR are usually computed and fed in as extra numbers.

**Normalization (z-score):** subtract the beat's mean and divide by its standard deviation. This makes the model care about **shape**, not absolute amplitude.
Worked example: `[1, 2, 3]` has mean 2 and std 0.816, so it becomes `[−1.22, 0, 1.22]`.

### Step 5: Model → class
The model outputs one raw score (a **logit**) per class. The **softmax** function turns these into probabilities that add up to 1:

  p_i = e^(z_i) / Σ_j e^(z_j)

**Worked example.** Logits for N, S, V, F are `[2.0, 0.5, 1.0, −1.0]`:
- e^z = `[7.389, 1.649, 2.718, 0.368]`, and their sum is 12.124.
- p = `[0.609, 0.136, 0.224, 0.030]`.
- Prediction: **N**, with 61% confidence.

### Say it in the viva
> "The pipeline first band-pass filters the raw ECG to remove baseline wander, powerline and muscle noise. It then finds R peaks, classically with Pan–Tompkins, and cuts a fixed window around each R peak. RR-interval features are added, because cutting out a single beat loses timing. The model outputs a softmax probability for each AAMI class."

---

## 1.6 What a 1D CNN does to a signal

### Plain language
A **convolution** slides a short pattern, called a **kernel** or **filter**, along the signal. At each position it measures how well the signal matches the pattern. Where they match, the output is large. A CNN (Convolutional Neural Network) **learns** what patterns to look for. Nobody designs the kernels by hand.

### Formal definition
For an input x, a kernel w of length K and a bias b:

  y[n] = Σ_{k=0}^{K−1} w[k] · x[n + k] + b

(Strictly speaking this is cross-correlation, which is what deep-learning libraries compute and call "convolution".)

This is followed by a **non-linearity**, usually **ReLU**: ReLU(v) = max(0, v). It keeps positive matches and zeroes everything else.

### Worked numeric example
Signal (a tiny "beat" with a sharp spike at position 2 and a smaller one at position 6):
```
x = [0, 1, 3, 1, 0, 0, 2, 0]
```
Kernel: a "spike detector" (+2 in the middle, −1 at either side):
```
w = [-1, 2, -1],  b = 0
```
Slide the kernel along the signal ("valid" mode, no padding):

| Position | Window | Calculation | y |
|---|---|---|---|
| 0 | [0,1,3] | 0·(−1) + 1·2 + 3·(−1) | −1 |
| 1 | [1,3,1] | −1 + 6 − 1 | **4** |
| 2 | [3,1,0] | −3 + 2 − 0 | −1 |
| 3 | [1,0,0] | −1 + 0 − 0 | −1 |
| 4 | [0,0,2] | 0 + 0 − 2 | −2 |
| 5 | [0,2,0] | 0 + 4 − 0 | **4** |

```
conv output y      = [-1, 4, -1, -1, -2, 4]
after ReLU         = [ 0, 4,  0,  0,  0, 4]     <- fires exactly where the spikes are
after max-pool (2) = [ 4,  0,  4]               <- keep the max of each pair; halves the length
```

**Max-pooling** keeps the strongest response in each small window. It shrinks the signal and makes the result tolerant to small shifts in time.

### What happens across many layers
- **Many filters per layer.** Layer 1 might have 32 kernels, which produce 32 output signals called **channels** or **feature maps**. Each learns a different pattern: an upslope, a peak, a wide dip, and so on.
- **Stacking layers** lets later layers combine earlier patterns. For example, "upslope + sharp peak + downslope" makes a QRS detector.
- The **receptive field** is how many input samples one output value "sees". It grows with depth and pooling.

**Receptive-field worked example.** Start with RF = 1 and jump J = 1 (the step size, measured in input samples). Each layer adds (kernel − 1) × J, and each pooling layer multiplies J by its stride.

| Layer | RF calculation | RF | J |
|---|---|---|---|
| Conv, k = 5 | 1 + 4×1 | 5 | 1 |
| MaxPool 2 | 5 + 1×1 | 6 | 2 |
| Conv, k = 5 | 6 + 4×2 | 14 | 2 |
| MaxPool 2 | 14 + 1×2 | 16 | 4 |
| Conv, k = 5 | 16 + 4×4 | **32** | 4 |

32 samples at 360 Hz is **89 ms**, roughly one QRS width. To "see" a whole 0.7-s beat including the P and T waves, you need more layers, larger kernels, or **dilated** convolutions (kernels with gaps).

**Parameter count:** each kernel has K × (input channels) weights plus 1 bias.
- `Conv1D(1 → 32, k=5)` has 32 × (5×1 + 1) = **192** parameters.
- `Conv1D(32 → 64, k=5)` has 64 × (5×32 + 1) = **10,304** parameters.

**Ending the network:** a **global average pooling** layer (average each channel over time) or a flatten layer, then a **dense (fully connected)** layer, then softmax over the classes.

### How it learns (training, in one paragraph)
1. Start with random kernels.
2. For each training beat, compute the **cross-entropy loss**, −ln(p_true). It is small when the model gives the true class a high probability.
   - Example: the true class is V and the model gives p(V) = 0.224, so the loss is −ln 0.224 = **1.50**.
   - If it gave p(V) = 0.9, the loss would be **0.105**.
3. **Backpropagation** computes how much each weight contributed to the loss (the **gradient**).
4. **Gradient descent** nudges every weight a small step in the direction that lowers the loss.
5. Repeat over many **mini-batches** and **epochs** (full passes over the data).
6. Hold out **validation** data to detect **overfitting**, which is when the model memorizes the training data instead of learning general patterns.

### Say it in the viva
> "A 1D convolution slides a small learned kernel along the ECG and outputs a high value wherever the signal matches that pattern. ReLU and pooling keep the strong matches and shorten the signal. Stacking layers widens the receptive field, so later layers detect whole structures such as a QRS complex. The kernels are learned by backpropagation, which minimizes cross-entropy loss."

---

## 1.7 Why LSTM, attention and transformers are added on top

### Plain language
A CNN is excellent at **local shape**: "is this QRS wide?". It is weaker at **order and long-range timing**: "did this beat arrive early compared with the last few?" or "is the rhythm irregular over 10 seconds?". Many arrhythmias are defined by timing, so we add parts that model sequences.

### RNN → LSTM
A **Recurrent Neural Network (RNN)** reads the sequence one step at a time and keeps a **hidden state** h, which is a memory vector:

  h_t = tanh(W·x_t + U·h_{t−1} + b)

**The problem:** during training, gradients get multiplied by U again and again across time steps, so they shrink to nearly zero. This is the **vanishing gradient** problem, and it means a plain RNN forgets distant context.

An **LSTM (Long Short-Term Memory)** adds a separate **cell state** c, a "conveyor belt" of memory, controlled by three **gates**. Each gate is a sigmoid that outputs a number between 0 and 1:
- **Forget gate f:** how much old memory to keep.
- **Input gate i:** how much new information to write.
- **Output gate o:** how much memory to reveal as output.

  c_t = f_t · c_{t−1} + i_t · (new candidate)

**Tiny example:** the old memory is c = 5.0, the forget gate is f = 0.9, the input gate is i = 0.2, and the new candidate is 3.0.
New c = 0.9×5.0 + 0.2×3.0 = 4.5 + 0.6 = **5.1**. Most of the old memory survives, and a little new information is added.

A **BiLSTM** runs one LSTM forwards and one backwards and joins their outputs. Each time step then knows both what came before and what comes after. That is useful because a beat's post-RR (the pause after it) is also informative.

### Attention
**Idea:** instead of squeezing the whole sequence into one final memory, let the model **look back at every time step** and decide how much each one matters.
1. Compute a relevance **score** for each time step.
2. Turn the scores into **weights** with softmax.
3. Take the **weighted sum** of the features.

**Worked example.** Three time steps (say P region, QRS region, T region) have scores `[2, 1, 0]`.
- Softmax gives weights `[0.665, 0.245, 0.090]`.
- If the feature values at those steps are `[10, 4, 1]`, the context = 0.665×10 + 0.245×4 + 0.090×1 = **7.72**.

The weights themselves can be drawn as a heatmap. That is an **"attention map"** (see section 1.11).

### Transformers
A **transformer** is built almost entirely from **self-attention**. Every time step looks at every other time step directly:
1. Each step produces a **Query** ("what am I looking for?"), a **Key** ("what do I contain?") and a **Value** ("what I pass on").
2. score(i, j) = (q_i · k_j) / √d, where d is the vector length. These scores are softmaxed into weights.
3. Each step's output is the weighted sum of all the Values.

Other parts of a transformer:
- **Positional encoding** adds information about order, because attention by itself ignores order.
- **Multi-head** attention runs several attentions in parallel, so different heads can learn different relationships.

```
  CNN:          [local window] -> sees ~QRS-sized patterns
  LSTM:         x1 -> x2 -> x3 -> ... -> xT    (memory passed step by step)
  Transformer:  every xi <-> every xj          (direct links, all pairs)
```

**Trade-offs**

| | CNN | LSTM | Transformer |
|---|---|---|---|
| Good at | Local shape | Order, timing | Long-range relationships |
| Training speed | Fast, parallel | Slow, sequential | Parallel, but cost grows with length² |
| Data needed | Moderate | Moderate | Large |

**Common hybrid (and what our literature review found):** a CNN front end learns the waveform shape, then an LSTM, attention or transformer module learns the timing.

### Say it in the viva
> "CNNs capture local waveform shape, but arrhythmias are also defined by timing between beats. LSTMs keep a gated memory across the sequence, which avoids the vanishing gradient of plain RNNs. Attention and transformers go further and let every time step weigh every other one directly. That is why most recent models are hybrids: a CNN for shape, followed by an LSTM or attention module for timing."

---

## 1.8 Datasets: MIT-BIH and PTB-XL

### Why datasets matter
A model is only as good as its labelled data, and you can only compare papers when they use the same dataset and the same split. Both datasets below are free on **PhysioNet** and stored in **WFDB** format:
- `.dat` holds the signal.
- `.hea` is the header (fs, gain, leads).
- `.atr` holds the annotations.

The Python `wfdb` package reads them.

### MIT-BIH Arrhythmia Database (`mitdb`)
- **Source:** Beth Israel Hospital, Boston, recorded 1975–1979 **(verify)**.
- **Records:** **48** half-hour excerpts from **47** subjects. Records 201 and 202 come from the same person **(verify)**.
  - Records 100–124 were chosen at random from Holter tapes.
  - Records 200–234 were chosen to include rare but clinically important arrhythmias **(verify)**.
- **Leads:** 2 per record. The first is usually **modified lead II (MLII)**. The second is usually **V1** (sometimes V2, V4 or V5) **(verify)**.
- **Sampling:** **360 Hz**, 11-bit resolution over a 10 mV range.
- **Labels:** about **110,000 beats**, each annotated by cardiologists at its R-peak location, plus rhythm annotations **(verify exact count)**.
- **Worked size:** 48 records × 648,000 samples ≈ **31.1 million samples per lead**.

### PTB-XL (`ptb-xl`)
- **Source:** Physikalisch-Technische Bundesanstalt (Germany). Recorded 1989–1996 and released in 2020 **(verify)**.
- **Records:** **21,799** ten-second ECGs from **18,869** patients (v1.0.3; an earlier version listed 21,837) **(verify)**.
- **Leads:** standard **12 leads**.
- **Sampling:** **500 Hz**, plus a 100 Hz downsampled copy.
- **Labels:**
  - 71 SCP-ECG statements (diagnostic, form and rhythm) **(verify)**.
  - These are grouped into **5 diagnostic superclasses**: NORM (normal), MI (myocardial infarction), STTC (ST/T change), CD (conduction disturbance), HYP (hypertrophy).
  - Labels are **multi-label**: one ECG can carry several.
- **Recommended split:** 10 **stratified, patient-respecting folds**. Folds 9 and 10 have extra human validation and are recommended for validation and test **(verify)**.
- **Worked size:** 10 s × 500 Hz × 12 leads = **60,000 numbers per record** (12,000 at 100 Hz).

### Side by side

| | MIT-BIH | PTB-XL |
|---|---|---|
| Task style | **Beat-level**, single label | **Record-level**, multi-label |
| Records / patients | 48 / 47 | 21,799 / 18,869 |
| Length | ~30 min each | 10 s each |
| Leads | 2 | 12 |
| fs | 360 Hz | 500 Hz (and 100 Hz) |
| Labels | Beat types → AAMI N/S/V/F/Q | Diagnostic statements → 5 superclasses |
| Strength | Standard benchmark for beat classification | Many patients, so generalization is more meaningful |
| Weakness | Very few patients; old, single-centre data | 10-s snippets; not beat-annotated |

### Two more databases our objectives need
- **MIT-BIH Noise Stress Test Database (`nstdb`):** real recordings of **baseline wander (bw)**, **muscle artifact (ma)** and **electrode motion (em)** noise, made to be added to clean ECGs at chosen SNRs **(verify details)**. This is for objective 3 (robustness).
- **St Petersburg INCART:** 75 records, 12-lead, 257 Hz **(verify)**. This is one candidate for external testing in objective 1.

### Say it in the viva
> "MIT-BIH has 48 two-lead, half-hour records from 47 patients at 360 Hz, with every beat labelled. It is the standard for beat classification, but it has very few patients. PTB-XL has about 21,800 ten-second, 12-lead records from about 18,900 patients at 500 Hz, labelled with multi-label diagnostic classes. It comes with recommended patient-respecting folds, so it is better for testing generalization."

---

## 1.9 Intra-patient vs inter-patient split, and why it changes accuracy

### Plain language
Imagine teaching someone to recognize handwritten letters.
- **Version A:** you train them on sentences written by 20 people, then test them on *other sentences by the same 20 people*.
- **Version B:** you test them on sentences by 5 *new people*.

Version A gives a higher score, but Version B tells you whether they can really read.

ECG works the same way. Each patient has their own "beat signature", so their beats look very alike.

### Formal definitions
- **Intra-patient (beat-wise) split:** pool all beats from all patients, shuffle them, and split them randomly into train and test. **The same patient's beats appear on both sides.** The model can partly memorize "what patient 208's beats look like" instead of learning what a V beat looks like in general. This is a form of **data leakage**.
- **Inter-patient (patient-wise) split:** whole **records (patients)** go entirely into train or entirely into test. The test patients are people the model has **never seen**. This is the realistic setting, since a deployed system always meets new patients.

```
 INTRA-PATIENT                         INTER-PATIENT
 Patient A: ■■■■■■□□                   Patient A: ■■■■■■■■  (train)
 Patient B: ■■■■■□■□                   Patient B: ■■■■■■■■  (train)
 Patient C: ■■■■■■■□                   Patient C: □□□□□□□□  (test)
 ■ = train beat, □ = test beat         Test patients are completely unseen
```

### The standard MIT-BIH inter-patient split (de Chazal et al., 2004) **(verify the record lists)**
After removing the 4 paced records, the remaining 44 are split into two sets of 22:
- **DS1 (train):** 101, 106, 108, 109, 112, 114, 115, 116, 118, 119, 122, 124, 201, 203, 205, 207, 208, 209, 215, 220, 223, 230
- **DS2 (test):** 100, 103, 105, 111, 113, 117, 121, 123, 200, 202, 210, 212, 213, 214, 219, 221, 222, 228, 231, 232, 233, 234

Caveat: records 201 (DS1) and 202 (DS2) come from the same person **(verify)**. This small leak is worth mentioning yourself before an examiner does.

For PTB-XL, the recommended folds already keep each patient within a single fold.

### How much it changes the numbers (from our literature review)
- Xiao et al. [10] compared 11 studies that reported both protocols. F1 fell from **95.52%** (intra-patient) to **83.89%** (inter-patient). Source: CSV row 10, pages 14–16.
- Ibrahim [15] reports **99.00%** accuracy beat-wise but **91.69%** patient-wise, with Fusion recall falling to **0.021**. Source: CSV row 15, pages 1 and 14.

*(I will re-check both numbers against the PDFs in Stage 3.)*

### Say it in the viva
> "In an intra-patient split, beats from the same person appear in both training and test sets. The model can memorize each patient's beat shape, so accuracy is inflated. An inter-patient split, such as de Chazal's DS1/DS2 on MIT-BIH, keeps test patients completely unseen, which matches real deployment. Reported F1 drops by more than ten points when you switch to it, so our project uses the inter-patient protocol."

---

## 1.10 Class imbalance, why accuracy misleads, and precision, recall and F1

### Plain language
If 90% of beats are N, a "model" that always says N scores 90% accuracy and catches **zero** dangerous beats. Accuracy counts every correct answer equally, so the huge N class drowns out the rare classes, and the rare classes are the ones that matter.

### Formal definitions (for one class, treated as "this class vs everything else")
- **TP** (true positive): it was this class, and we said this class.
- **FN** (false negative): it was this class, and we said something else. This is a **miss**.
- **FP** (false positive): it was another class, and we said this class. This is a **false alarm**.
- **TN** (true negative): it was another class, and we said another class.

| Metric | Formula | Question it answers | AAMI name |
|---|---|---|---|
| **Accuracy** | correct / total | How often are we right overall? | Acc |
| **Precision** | TP / (TP + FP) | When we say "S", how often is it really S? | **+P** (positive predictivity) |
| **Recall** | TP / (TP + FN) | Of all real S beats, how many did we catch? | **Se** (sensitivity) |
| **Specificity** | TN / (TN + FP) | Of all non-S beats, how many did we correctly leave alone? | Sp |
| **F1** | 2·P·R / (P + R) | One number that balances precision and recall (their harmonic mean) | F1 |
| **Macro-F1** | Average of the per-class F1 scores | Every class counts **equally**, however rare | |

### Worked confusion matrix (1,000 test beats)
Rows are the **true** class and columns the **predicted** class.

```
                 Predicted
               N     S     V     F   | Row total (true)
 True  N     880    10     8     2   |  900
       S      25    22     3     0   |   50
       V       4     1    34     1   |   40
       F       4     0     3     3   |   10
 ------------------------------------+------
 Col total   913    33    48     6   | 1000
```

**Accuracy** = (880 + 22 + 34 + 3) / 1000 = 939 / 1000 = **93.9%**. That sounds great.

**Per class:**

| Class | Precision = TP / column total | Recall = TP / row total | F1 |
|---|---|---|---|
| N | 880/913 = 0.964 | 880/900 = 0.978 | 0.971 |
| S | 22/33 = 0.667 | 22/50 = **0.440** | 0.530 |
| V | 34/48 = 0.708 | 34/40 = 0.850 | 0.773 |
| F | 3/6 = 0.500 | 3/10 = **0.300** | 0.375 |

**Macro-F1** = (0.971 + 0.530 + 0.773 + 0.375) / 4 = **0.662**.

So accuracy says 94%, but the model **misses 56% of S beats and 70% of F beats**. Macro-F1 (0.66) shows the real picture.

**Specificity for S:** TN = 1000 − 22 − 28 − 11 = 939, so Sp = 939 / (939 + 11) = **0.988**.

**The "always N" model:**
- Accuracy = 900/1000 = **90%**.
- F1(N) = 2×0.9×1/(1.9) = 0.947, and F1 = 0 for S, V and F.
- Macro-F1 = 0.947 / 4 = **0.237**.

So accuracy rates this useless model at 90%, while macro-F1 rates it at 0.24, which is the honest score.

**Common fixes for imbalance** (we will meet these in papers):
- **Class weights** in the loss, so rare-class mistakes cost more.
- **Oversampling or undersampling.**
- **Data augmentation**, including GAN-generated beats.
- **Focal loss.**

### Say it in the viva
> "MIT-BIH is about 89% normal beats, so a model that always predicts normal scores roughly 90% accuracy while detecting nothing. That is why we report per-class precision (positive predictivity), recall (sensitivity) and F1, plus macro-F1, which weights each class equally. In my worked example, 93.9% accuracy hides an S-beat recall of only 44%."

---

## 1.11 What "explainable" means: Grad-CAM, SHAP, LIME and attention maps

### Plain language
A deep network has hundreds of thousands of weights. Nobody can read off *why* it called a beat V. **Explainable AI (XAI)** methods produce a human-readable reason, usually a **map showing which part of the input mattered most** for this decision.

### Key distinctions
- **Interpretable by design vs post-hoc.**
  - Interpretable by design: a small decision tree, or a linear model on hand-made features like "QRS width", is readable directly.
  - Post-hoc: we train a black box first, then explain it afterwards.
  - Grad-CAM, SHAP and LIME are all **post-hoc**.
- **Local vs global.**
  - **Local** explains *this one beat*.
  - **Global** explains what the model relies on *in general*, for example by averaging local explanations over a class.
- **Model-specific vs model-agnostic.** Model-specific methods need access to the network's internals (gradients). Model-agnostic methods only need to query the model with inputs and read the outputs.

### Grad-CAM (Gradient-weighted Class Activation Mapping)
**What it computes:** which **time regions** of the last convolutional layer's feature maps pushed the score for class c up.
1. Take the last conv layer's feature maps A_k (k = 1…K channels, each of length T).
2. Compute the gradient of the class score y_c with respect to each feature map: ∂y_c/∂A_k. This answers "if this feature went up, how much would the V score go up?"
3. Average that gradient over time to get one **importance weight per channel**: α_k = mean_t (∂y_c/∂A_k[t]).
4. Heatmap = ReLU( Σ_k α_k · A_k ). Keep only the positive evidence.
5. Stretch (upsample) the heatmap back to the input length and overlay it on the ECG.

**Worked example** (2 channels, length 4):
```
A1 = [0, 2, 4, 1]     alpha1 = 0.5   (channel 1 supports class V)
A2 = [1, 1, 0, 0]     alpha2 = -0.2  (channel 2 argues against V)

0.5*A1   = [ 0.0, 1.0, 2.0, 0.5]
-0.2*A2  = [-0.2,-0.2, 0.0, 0.0]
sum      = [-0.2, 0.8, 2.0, 0.5]
ReLU     = [ 0.0, 0.8, 2.0, 0.5]   <- hottest at position 2 (e.g. the QRS)
```
**Pros:** fast (one backward pass); designed for CNNs.
**Cons:** the resolution is limited to the last layer's length, which is coarse; it only works with conv layers; it is model-specific.

### SHAP (SHapley Additive exPlanations)
**What it computes:** a fair share of the prediction for each input feature, borrowed from **game theory (Shapley values)**. The features are "players" who cooperate to produce the output. Each player's share is its average extra contribution, taken over every possible order in which players could join.

**Formal:** the model output = base value (the average prediction) + Σ φ_i, where φ_i is feature i's Shapley value.

**Worked example** (2 features: pre-RR and QRS width; output = probability of V):

| Features "present" | Model output |
|---|---|
| none (baseline) | 0.10 |
| pre-RR only | 0.30 |
| QRS width only | 0.50 |
| both | 0.90 |

- φ(pre-RR) = average of its contribution when it joins first (0.30 − 0.10 = 0.20) and when it joins second (0.90 − 0.50 = 0.40) = **0.30**.
- φ(QRS) = average of (0.50 − 0.10 = 0.40) and (0.90 − 0.30 = 0.60) = **0.50**.
- Check: 0.10 + 0.30 + 0.50 = 0.90 ✓. The contributions always add up exactly. This is SHAP's key guarantee.

For a raw ECG, the "features" are individual samples or short segments. With n features there are 2ⁿ subsets, so practical versions (KernelSHAP, DeepSHAP, GradientSHAP) **approximate** the values. Results depend on the chosen **baseline**: what "feature absent" means, for example zero signal or an average beat.
**Pros:** solid theory; values add up exactly; works with any model.
**Cons:** slow; depends on the baseline; on correlated time samples the attributions can be noisy.

### LIME (Local Interpretable Model-agnostic Explanations)
**What it computes:** it builds a **simple linear model that imitates the black box near this one input**, then reads that linear model's weights.
1. Split the beat into segments, for example P, QRS and T.
2. Make many perturbed copies with some segments "switched off" (replaced by baseline).
3. Ask the black-box model for its prediction on each copy.
4. Fit a weighted linear regression, prediction ≈ b + w_P·P + w_QRS·QRS + w_T·T. Copies closer to the original get more weight.
5. The weights w are the explanation.

**Worked example** (1 = segment kept, 0 = segment blanked; output = p(V)):

| P | QRS | T | p(V) |
|---|---|---|---|
| 1 | 1 | 1 | 0.90 |
| 0 | 1 | 1 | 0.85 |
| 1 | 0 | 1 | 0.20 |
| 1 | 1 | 0 | 0.80 |

Solving b + w_P + w_QRS + w_T = 0.90 and the other equations gives:
- **w_P = 0.05**
- **w_QRS = 0.70**
- **w_T = 0.10**
- b = 0.05

The explanation: "QRS drives the V decision." That is clinically sensible, because V beats have a wide QRS.
**Pros:** model-agnostic; easy to explain to people.
**Cons:** the result depends on how you segment and perturb, and it can change between runs (instability).

### Attention maps
**What it computes:** nothing extra. You simply **plot the attention weights** the model already computed (section 1.7), for example `[0.665, 0.245, 0.090]` over P, QRS and T.
**Pros:** free, since it comes out of the forward pass.
**Cons:** attention weights show where information was **routed**, which is not necessarily what **caused** the decision. Whether "attention is explanation" is an open debate in the literature (Jain & Wallace 2019, and replies to it) **(verify)**.

### Bonus: counterfactual explanations (they appear in our literature review)
Counterfactuals ask: "what is the **smallest change** to this ECG that would flip the prediction from V to N?" The difference between the original and the changed ECG *is* the explanation.

### Comparison

| Method | Needs gradients? | Model-agnostic? | Cost | Output |
|---|---|---|---|---|
| Grad-CAM | Yes | No (CNNs) | Very low | Coarse heatmap over time |
| SHAP | Depends on variant | Yes (KernelSHAP) | High | Signed contribution per sample/segment, adds up to the output |
| LIME | No | Yes | Medium | Weights of a local linear model |
| Attention map | No (already computed) | No (attention models only) | Free | Weights over time steps |

### How do we know an explanation is any good? (This is central to our objective 2.)
- **Faithfulness (deletion test):** blank out the top-k% most "important" samples and check the prediction drops a lot. Then blank random samples and check it drops less.
  Worked example: p(V) = 0.90. Removing the top-10% Grad-CAM region drops it to 0.30. Removing a random 10% drops it to 0.85. The map is faithful.
- **Consistency:** explanations for beats of the same class should look alike.
- **Clinical plausibility:** does the map highlight the region a cardiologist would point to? For example, the QRS for a V beat, and the P wave or pre-RR for an S beat.

### Say it in the viva
> "Grad-CAM weights the last convolutional feature maps by the gradient of the class score, giving a heatmap over time. SHAP gives each input feature its Shapley value, a fair share of the prediction that adds up exactly. LIME fits a simple local linear model by perturbing segments of the input. Attention maps just display the model's own attention weights. All of these explain the model, not the disease, so we also test whether explanations are faithful, consistent within a class, and clinically plausible."

---

## 1.12 Why explainability matters to a doctor

### Plain language
A doctor is legally and ethically responsible for the diagnosis. They cannot sign off on "the computer said so". An explanation turns the model from an **oracle** into an **assistant whose work can be checked**.

### Reasons, built up
1. **Verification in seconds.** Suppose the model flags a beat as V and highlights a wide QRS with no preceding P wave. The cardiologist can glance at it and agree, because that is the textbook V-beat criterion. Without the highlight, they would have to re-read the beat from scratch, which defeats the point of automating.
2. **Catching wrong reasoning (shortcut learning).** A model can score well for the wrong reason. For example, it might key on baseline noise that happens to be common in one patient's record. A heatmap sitting on flat baseline instead of the QRS exposes this. That is a debugging tool for **us** as developers as well.
3. **Mapping to clinical criteria.** Doctors already reason in terms of features:

   | Class | Feature the doctor uses |
   |---|---|
   | V | Wide QRS, no P wave |
   | S | Early beat, abnormal or hidden P wave |
   | Atrial fibrillation | Irregular RR, no P waves |

   An explanation that lands on these features speaks the doctor's language.
4. **Trust and adoption.** Clinicians are unlikely to adopt a system they cannot question. Explanations also help when an alarm needs to be overridden.
5. **Accountability and regulation.** Medical-device and AI regulators increasingly expect transparency about how automated decisions are made **(verify the specific requirements, e.g. EU AI Act and FDA guidance, before citing)**.
6. **Caveat (honesty).** An explanation can look convincing and still be wrong or unstable. Our literature review notes that explanations are rarely validated against clinical structures. That is the reason our project measures **consistency** and **plausibility** instead of just drawing heatmaps (Gap 1 in `literature_review.md`).

```
 Without XAI:   ECG --> [black box] --> "V (97%)"         Doctor: "Why?"  -> no answer
 With XAI:      ECG --> [model] --> "V (97%)" + heatmap on wide QRS, no P
                                                           Doctor: "Agreed."  or  "No, that's noise."
```

### Say it in the viva
> "The clinician, not the algorithm, is responsible for the diagnosis. They need to check the model's reasoning against known ECG criteria, such as a wide QRS with no P wave for a ventricular beat. Explanations make that check fast, expose models that learned shortcuts from noise, and support trust and regulatory accountability. But an explanation can itself be misleading, so we validate explanations rather than just display them."

---

## Stage 1 glossary (quick reference)

| Term | One-line meaning |
|---|---|
| Depolarization / repolarization | Electrical "fire" / "reset" of a heart cell |
| Lead | One viewing angle: the voltage difference between electrode(s) |
| fs (sampling rate) | Samples per second (MIT-BIH: 360 Hz) |
| P / QRS / T | Atrial depolarization / ventricular depolarization / ventricular repolarization |
| RR interval | Time between R peaks; HR = 60/RR |
| AAMI N/S/V/F/Q | Standard 5-class grouping of beat types by where the beat originates |
| Pan–Tompkins | Classic R-peak detector: band-pass, derivative, square, integrate, threshold |
| Kernel / filter | Small learned pattern slid along the signal in a CNN |
| Receptive field | How many input samples one output value can "see" |
| Softmax | Turns scores into probabilities that sum to 1 |
| Cross-entropy | Training loss, −ln(probability given to the true class) |
| LSTM | RNN with gated memory; avoids the vanishing gradient |
| Attention | Softmax-weighted sum over time steps |
| Transformer | A network built from self-attention (Query/Key/Value) |
| Intra- / inter-patient | Same patients in train and test / unseen test patients |
| DS1 / DS2 | de Chazal's standard MIT-BIH inter-patient train/test record sets |
| Precision (+P) / Recall (Se) | Of predicted X, fraction truly X / of true X, fraction caught |
| Macro-F1 | Average F1 over classes, each class weighted equally |
| Grad-CAM | Gradient-weighted sum of the last conv feature maps → heatmap |
| SHAP | Shapley-value attribution; contributions add up to the output |
| LIME | Local linear surrogate fitted to perturbed inputs |
| Faithfulness | Whether removing the "important" region really changes the prediction |

---

**END OF STAGE 1.**

---

# STAGE 2: Batch plan

> **Decisions taken while you were away** (all reversible, and listed in the progress log):
> - **Included:** *ECGformer* (Akan et al., `papers/_unsorted/2401.05434v1.pdf`). It is on topic, so I added it as **row 37** of `literature_review.csv`, with every number taken from its PDF. A backup of the original CSV is at `papers/literature_review.csv.bak`.
> - **Excluded:** the phishing-website paper (CNN-SVM) and the *V-NET-VGG16* paper, which turned out to be about liver-tumour CT. Neither contains any ECG content.
> - That leaves **37 papers** in **8 batches** of 4–5.
>
> **Citation convention for Stages 3–4:** `[n]` is the row number in `literature_review.csv`, and **p.X** is the **PDF page number** (page 1 is the first page of the PDF file, which is sometimes a cover page). Every number has been checked against the text extracted from the PDF.

| Batch | Theme | Papers `[CSV row]` | Why this batch comes at this point |
|---|---|---|---|
| **1** | **Reviews: the map of the field** | [8] Ebrahimi 2020; [9] Ansari 2023; [10] Xiao 2023; [11] Silva 2025; [12] Kulkarni 2026 | Read first. They give the vocabulary, the main datasets, how common each model type is, and they already show the inter-patient problem and the XAI gap. Read in date order, so you see the field change from 2017 to 2025. |
| **2** | **CNN and recurrent baselines on MIT-BIH** | [17] Ahmed 2023 (1D-CNN); [25] Pramkeaw 2026 (ANN vs CNN vs RNN vs LSTM vs CNN-LSTM); [26] Wang 2026 (CNN-LSTM for IoMT); [24] Reddy 2025 (multi-scale CNN + dense + BiLSTM) | These are the simplest working systems, and they map directly onto Stage 1 §1.6–1.7. They give us the "baseline" we will build first. Pramkeaw is the only paper that compares CNN, RNN and LSTM head-to-head. |
| **3** | **Attention and transformer hybrids** | [37] ECGformer 2024; [18] El-Ghaish ECGTransForm 2024; [20] Ikram 2025; [23] Liu CNN-BERT 2025; [36] Huang MSCA-TNet 2026 | The next step up from Batch 2: what attention adds, and at what cost. Two of these papers use the *same* Kaggle beat split, which is a lesson in how splits shape results. |
| **4** | **Changing the input representation** | [21] Kim 2025 (Stockwell time-frequency, no R-peak); [5] Tenepalli 2025 (beats drawn as images + Grad-CAM); [22] Lee 2025 (graph of P-QRS-T); [19] Chen 2025 (multi-scale + LLM text prompts, PTB-XL) | Shows that the *input* to the network is a design choice, not just the network itself. It also introduces Grad-CAM and attention maps on real models just before the XAI batch. |
| **5** | **XAI on MIT-BIH: what is explained, and how well** | [1] Alamatsaz 2024 (CNN-LSTM + SHAP); [4] Talukder 2025 (CNN + SHAP/LIME); [6] Asha 2026 (proposed GAN + distillation + SHAP); [7] Kavitha 2026 (Cycle-GAN + SHAP); [2] Beck 2025 (4 SHAP variants, clinician survey) | The core of our title. Four papers claim explainability, and Beck then tests those claims critically. This is the evidence for Gap 1. |
| **6** | **Patient-independent evaluation** | [13] Jeong 2024 (adversarial patient-invariance); [14] Hassoon 2026 (dual-branch, subject split); [16] Qin 2026 (dilated ResNet-BiLSTM, INCART external); [15] Ibrahim 2026 (beat-wise vs patient-wise) | Read this only after you have seen the high intra-patient numbers in Batches 2–5. It shows how much they fall under a fair split. This is the evidence for Gap 2 and objective 1. |
| **7** | **Robustness: noise, denoising and uncertainty** | [32] Mallikarjunamallu 2024 (noise + notch + 1D-CNN); [31] Pashikanti 2022 (adaptive LMS); [35] Maurya 2025 (denoising autoencoder, NSTDB); [33] Zhang 2024 (Monte Carlo dropout rejection); [34] Ashhad 2025 (uncertainty-aware fusion, NSTDB) | Covers what happens to the model with real-world noise, and how a model can say "I'm not sure". This is the evidence for Gap 3 and objective 3. |
| **8** | **12-lead, PTB-XL and clinically checked explanations** | [27] Smigiel 2021; [30] Mehdi 2026; [28] Anand 2022 (SHAP checked against clinical criteria); [3] Kolliyil 2025 (interpretable features, external tests incl. PTB-XL); [29] Jang 2025 (counterfactual XAI) | Last, because PTB-XL is multi-label, 12-lead and record-level, which is the hardest setting. It also holds the strongest examples of explanations checked against clinical knowledge, which is the bar our objective 2 aims for. |

**Total:** 5 + 4 + 5 + 4 + 5 + 4 + 5 + 5 = **37 papers**.

---

# STAGE 3: Batch reviews

---

## Batch 1: Reviews (the map of the field)

### a. What question this batch tries to answer
*"What does the deep-learning ECG-arrhythmia field look like: which models, which datasets, how is it evaluated, and what is still missing?"*

A **review** runs no experiments of its own. It reads many papers and summarises them. A **systematic review** does this with a written, repeatable search procedure (which databases, which keywords, which inclusion rules), so readers can trust it is not cherry-picked. A **meta-analysis** goes one step further and statistically pools the numbers from many studies.

### b. Paper by paper

#### [8] Ebrahimi et al., 2020: "A review on deep learning methods for ECG arrhythmia classification" (*Expert Systems with Applications: X*)
- **Problem:** Gives an organised overview of the DL methods used for arrhythmia classification in 2017–2018.
- **Dataset:** None of its own. It catalogues the databases used by the studies it reviews (MIT-BIH, PTB, INCART, PhysioNet challenges and others).
- **Method:** A topical (not fully systematic) survey of PubMed and Google Scholar. It found 77 publications, excluded 2, and analysed **75** (p.7). Studies are grouped by model (MLP, CNN, DBN, RNN, LSTM, GRU), by what the network does (feature extractor, classifier or both), and by arrhythmia.
- **Results:**
  - CNN was used for feature extraction in **52%** of studies (p.1, p.9).
  - AF and SVEB/VEB were the most studied arrhythmias, at **48%** and **21%** (p.9).
  - The best reported accuracies were AF **100%**, SVEB **99.8%** and VEB **99.7%** (p.1).
  - One study it cites (Liu et al., MI detection on PTB) already shows the split effect: **99.95%** class-based vs **98.79%** patient-specific (p.8).
- **Limitation:** It only covers 2017–2018. The DL weaknesses it lists are overfitting on small datasets, learning noise, heavy computation, vanishing gradients, and working well for only about 6 classes (p.10).
- **Relation to our project:** It shows CNNs were the default from the start. It has **no XAI discussion** (XAI: not stated). It is historical context only.

#### [9] Ansari et al., 2023: "Deep learning for ECG arrhythmia detection and classification: an overview of progress for period 2017–2023" (*Frontiers in Physiology*)
- **Problem:** Gives a systematic overview of DL for ECG arrhythmia from 2017 to 2023, and proposes a guideline pipeline.
- **Dataset:** None of its own. It summarises 17 databases, including MIT-BIH, INCART, NSTDB, PTB and CPSC 2018.
- **Method:** It searched Google Scholar, PubMed, Scopus and DBLP. It found **4,215** studies, **2,492** of them unique, and included **78** (p.3). **The inclusion rule required accuracy ≥ 96%** (p.3).
- **Results:**
  - The reviewed models' accuracies range from **96.00% to 99.80%** (Table 3, p.13).
  - F1 ranges from **95.30% to 99.99%** (Table 4, p.14).
  - CNNs dominate. Hybrids (a CNN feature extractor followed by an RNN or Transformer) beat shallow models but cost more computation. Class imbalance is a long-term challenge.
- **Limitation:** Because only studies with ≥ 96% accuracy were included, the review is **deliberately biased towards high-scoring work** (p.3). The protocol was not registered, and there was no formal risk-of-bias check (p.3).
- **Relation to our project:** It recommends **interpretable DL** and **INCART for generalisation testing** (p.15–17). Both are in our objectives.

#### [10] Xiao et al., 2023: "Deep Learning-Based ECG Arrhythmia Classification: A Systematic Review" (*Applied Sciences*)
- **Problem:** Gives a systematic review of DL for ECG arrhythmia, with explicit attention to how studies are **evaluated**.
- **Dataset:** None of its own. MITDB is used by **223 of 368** studies (61%) (p.2, p.6).
- **Method:** It searched up to December 2022. It found **3,910** records, **2,265** of them unique, and included **368** (p.4). For each study it recorded the database, preprocessing, model, number of classes, and **intra- vs inter-patient** evaluation.
- **Results:**

  | Finding | Number | Page |
  |---|---|---|
  | Studies that denoise | 38% (138) | p.2, p.9 |
  | Studies that augment data | 28% (102) | p.2, p.10 |
  | Studies using a CNN | 58.7% (216) | p.2, p.12 |
  | Studies using a hybrid model | 22.3% (82) | p.12 |
  | Intra-patient only / inter-patient only / both | 319 / 27 / 11 | p.14 |
  | Inter-patient studies using DS1/DS2 | 82% (31/38) | p.14–15 |
  | Studies sharing their code | ~6% (20/368) | p.17 |

  For the **11 studies that reported both protocols** (p.16):

  | Metric | Intra-patient | Inter-patient |
  |---|---|---|
  | Accuracy | 98.39% | 90.15% |
  | F1 | **95.52%** | **83.89%** |
  | Sensitivity | 93.51% | 78.16% |
  | Positive predictivity (Ppv) | 92.78% | **62.82%** |
  | Specificity | 99.19% | 93.86% |

  Inter-patient averages across all such studies: Acc **92.62%**, F1 **79.48%**, Se **79.25%**, Ppv **71.74%** (p.16).
- **Limitation:** The authors say these averaged cross-study numbers are biased, because the studies used different tasks and class counts (p.16).
- **Relation to our project:** **This is the main citation for our inter-patient argument (Gap 2).** Notice that accuracy falls by only about 8 points, but Ppv falls by about 30. This is exactly the "accuracy hides failure" point from Stage 1 §1.10.

#### [11] Silva et al., 2025: "A Systematic Review of ECG Arrhythmia Classification: Adherence to Standards, Fair Evaluation, and Embedded Feasibility" (arXiv)
- **Problem:** Asks how many highly cited ECG papers actually follow fair evaluation rules and could run on small devices.
- **Dataset:** None of its own. It focuses on MIT-BIH and the AAMI classes, and it describes the de Chazal DS1/DS2 split (p.7).
- **Method:** A Web of Science search for 2017–2024, narrowed from 1,427 to 927, then 653, then 621 papers, and finally **122** included (p.4). Each paper is scored on four "**E3C**" criteria:
  1. Follows AAMI.
  2. Uses an inter-patient split.
  3. Uses MIT-BIH.
  4. Considers embedded (small-device) feasibility.
- **Results** (p.11):

  | Criterion | Papers meeting it |
  |---|---|
  | Follows AAMI | 68 (55.7%) |
  | Inter-patient split | **37 (30.3%)** |
  | Uses MIT-BIH | 96 (78.7%) |
  | Considers embedded feasibility | 38 (31.1%) |
  | Meets **all four** | **5 (4.1%)** |

  - One reviewed spiking neural network (Xing et al.) gets **92.07%** inter-patient but **98.26%** with a 70:30 random split (p.23).
  - Raj & Ray average **86.89%** accuracy, but their F-class F1 is **4.08%** and Q-class F1 **0.94%** (Table 9, p.24).
- **Limitation:** Only Web of Science and SCI-EXPANDED papers are covered. Reporting is not standardised, so several studies lack per-class results (p.25–26).
- **Relation to our project:** It recommends reporting **Se, +P and F1 for all five AAMI classes**, plus model size and inference time (p.25). We will report in exactly this format.

#### [12] Kulkarni et al., 2026: "Recent advances in deep learning based arrhythmia classification using ECG and PPG signals: a systematic review" (*Discover Computing*)
- **Problem:** Gives an up-to-date systematic review **with meta-analysis** of ECG and PPG arrhythmia DL from 2023 to mid-2025.
- **Dataset:** None of its own. It surveys MIT-BIH, PTB-XL, CPSC 2018, INCART and others.
- **Method:** A PRISMA 2020 review of 2,745 records, of which **119** were included (p.11). It uses random-effects pooling, meta-regression and Pareto (accuracy vs cost) analysis.
- **Results:**
  - CNNs appear in **62%** of works (p.1).
  - Pooled ECG accuracy is **97.84%**, vs **93.65%** for PPG (p.50).
  - In meta-regression, attention/transformers gain **+0.845%** over a 1D-CNN, and hybrid CNN-RNN models gain **+0.574%** (p.44).
  - There is a "knee point" at about **1 M parameters / 1 GFLOP**. Beyond it, gains of less than 0.5 points need far more computation (p.42).
  - **Only 18.5% (22/119)** of studies validate on an external dataset. Those that do lose an average of **8.7 ± 2.1%** accuracy (range 6–14%) and **13.2 ± 3.4%** F1 (range 8–18%) (p.50).
  - Minority classes lose **19.4%** F1, against **2.8%** for Normal (p.50).
  - Only **28%** of studies used inter-patient validation (p.18).
  - **Fewer than 10%** of studies validated explanation maps against clinically meaningful ECG structures (p.40).
- **Limitation:** It covers only open-access English papers from five databases. Heterogeneity is extreme (I² ≈ 100%), and no risk-of-bias tool was used (CSV page_refs: p.59–60).
- **Relation to our project:** **This is the main citation for Gap 1 (unvalidated explanations) and Gap 4 (external validation).** It also notes that hybrid temporal models with 0.5–1.5 M parameters give a good balance of efficiency and performance (p.47), which guides our choice of model size.

### c. Comparison table

| Ref | Years covered | Studies included | Systematic? | Key evaluation finding | XAI coverage |
|---|---|---|---|---|---|
| [8] Ebrahimi | 2017–2018 | 75 (p.7) | Partly (topical) | Patient-specific result lower (99.95 → 98.79%, p.8) | Not stated |
| [9] Ansari | 2017–2023 | 78 (p.3) | Yes, but accuracy ≥ 96% filter | Range 96.00–99.80% (p.13) | Recommends interpretable DL |
| [10] Xiao | to Dec 2022 | 368 (p.4) | Yes | F1 95.52 → 83.89% intra vs inter (p.16) | Rarely discussed |
| [11] Silva | 2017–2024 | 122 (p.4) | Yes | 30.3% inter-patient; 4.1% meet E3C (p.11) | Not stated |
| [12] Kulkarni | 2023–2025 | 119 (p.11) | Yes + meta-analysis | 18.5% external; −8.7% acc (p.50) | < 10% validate maps (p.40) |

### d. Agreement, disagreement, and what is missing
- **They agree that:**
  - CNNs dominate (58.7% in [10] p.12; 62% in [12] p.1).
  - MIT-BIH is the default dataset.
  - Hybrids are rising.
  - Class imbalance hurts the minority classes.
  - Inter-patient evaluation is under-used (30.3% in [11] p.11; 28% in [12] p.18).
- **They disagree on how big the inter-patient penalty is:**
  - Xiao [10] finds a large drop: accuracy 98.39 → 90.15%, and F1 95.52 → 83.89% (p.16).
  - Kulkarni [12] finds pooled MIT-BIH accuracy of **98.58%** intra vs **98.31%** inter (p.47, p.50). That is almost no difference.
  - **Why they can differ:** Xiao compares the *same* 11 studies under both protocols, which is a paired comparison. Kulkarni pools *different* studies with heterogeneity of about 100%. Accuracy is also dominated by the N class (Stage 1 §1.10). **Use Xiao's paired comparison as the stronger evidence, and say why.**
- **Ansari [9] reports 96–99.8% only because it only admitted studies above 96% (p.3).** That is a selection effect, not evidence that the field is solved.
- **Missing:** No review measures whether explanations stay **stable under noise**, or whether they hold up under **inter-patient** splits. That gap is ours.

### e. New terms introduced in this batch
- **Systematic review:** a literature review with a pre-defined search and inclusion rules, so anyone repeating it gets the same set of papers. *Example:* [10] searched 4 databases with fixed keywords and kept 368 of 2,265 unique records (p.4).
- **PRISMA:** a standard checklist and flow diagram for reporting systematic reviews (identified → screened → included). [12] follows PRISMA 2020.
- **Meta-analysis / pooled estimate:** combining many studies' numbers into one estimate, weighting each study (usually by its size or precision). *Example:* [12] pools ECG accuracy to 97.84% (p.50).
- **Heterogeneity (I²):** the percentage of variation between studies that comes from real differences rather than chance. I² ≈ 100% means the studies are so different that one pooled number is barely meaningful.
- **Selection bias:** when the way papers were chosen distorts the conclusion. *Example:* [9] keeps only studies with ≥ 96% accuracy (p.3).
- **External validation:** testing on a *different dataset* (another hospital, device or population) from the one used for training. It is stricter than inter-patient testing, because the recording conditions also change.
- **E3C:** Silva's four criteria: AAMI, inter-patient, MIT-BIH and embedded feasibility ([11] p.11).
- **Pareto frontier / knee point:** the set of models where you cannot gain accuracy without paying more computation. The knee is where extra cost stops buying much accuracy ([12] p.42).
- **Spiking neural network (SNN):** a low-power network type that communicates in spikes (on/off events) instead of continuous values. It appears in [11] as a way to run on embedded hardware.

### f. Examiner questions with model answers
1. **"Most papers report around 99% accuracy on MIT-BIH. Why isn't the problem solved?"**
   *Answer:* Most of those results use intra-patient splits. Xiao et al. show that, for studies reporting both protocols, F1 drops from 95.52% to 83.89% and positive predictivity from 92.78% to 62.82% under inter-patient testing. Only about 30% of studies use inter-patient splits (Silva), and only 18.5% test on an external dataset, where accuracy drops by about 8.7% on average (Kulkarni). So the headline numbers overstate real-world performance.
2. **"Kulkarni finds almost no intra/inter gap in pooled accuracy. Doesn't that contradict your argument?"**
   *Answer:* Kulkarni pools different studies with heterogeneity near 100%, and accuracy is dominated by normal beats. Xiao compares the same 11 studies under both protocols, which is a fairer paired comparison, and it shows large drops in F1, sensitivity and Ppv. That is exactly why we report per-class F1 and not just accuracy.
3. **"What evidence is there that XAI in ECG is not yet mature?"**
   *Answer:* Kulkarni reports that fewer than 10% of studies validated explanation maps against clinically meaningful ECG structures. The earlier reviews barely discuss interpretability; Ansari and Xiao list it as future work. So explanations are common, but checking them is rare. That is our Gap 1.

---

## Batch 2: CNN and recurrent baselines on MIT-BIH

### a. What question this batch tries to answer
*"How well do the basic building blocks from Stage 1 (CNN, RNN, LSTM and a CNN-LSTM hybrid) classify MIT-BIH beats, and what tricks do people add to make them work?"*

### b. Paper by paper

#### [17] Ahmed et al., 2023: "Classifying Cardiac Arrhythmia from ECG Signal Using 1D CNN Deep Learning Model" (*Mathematics*)
- **Problem:** Can a compact, well-tuned 1D-CNN alone classify the 4 AAMI classes accurately?
- **Dataset:** MIT-BIH, lead II. **99,774** beats in classes N, S, V and F (p.5–6). The Q class (24 unknown beats) was dropped.
- **Method:**
  - R peaks are found with the **XQRS** detector (p.5), and **180-sample** beats are cut around them (p.5).
  - The network has three convolution blocks, each with two Conv1D layers (**128** filters, p.8), max-pooling, dropout and batch normalisation. Then come a dense layer and softmax over 4 classes.
  - Imbalance is handled with **class weights** (p.11).
  - In Stage 1 terms (§1.6), this is a stack of learned "pattern detectors" with pooling, ending in softmax.
- **Split:** Random **beat-level** stratified split: 75% train+validation and 25% test (p.6). Patient separation is not described, so it is **intra-patient**.
- **Results:**
  - Test accuracy **0.99**; training accuracy **1.00** (p.10–11).
  - Macro precision **0.93**, recall **0.94**, F1 **0.93** (p.11).
  - Per-class F1: N **1.00**, S **0.92**, V **0.98**, F **0.85** (p.11).
- **Limitation:** The authors acknowledge that imbalance still affects generalisation, and that arrhythmias vary greatly between patients, so more data is needed (p.13). The CSV reviewer also notes that the abstract mentions noise attenuation, but no denoising step is described.
- **Relation to our project:** A clean example of the **plain 1D-CNN baseline** we will build first. Its 0.99 accuracy is an *intra-patient* number, so we should not expect it under DS1/DS2.

#### [25] Pramkeaw et al., 2026: "Deep Learning-Based ECG Arrhythmia Detection System: A Comparative Study of CNN, RNN, and LSTM Architectures" (IEEE ICCI)
- **Problem:** Which architecture works best on the same data and protocol: ANN, CNN, RNN, LSTM or CNN-LSTM?
- **Dataset:** MIT-BIH, all 48 records, AAMI N/S/V/F/Q.
- **Method:**
  - Preprocessing: 0.5 Hz high-pass, 50/60 Hz notch, 40 Hz low-pass, z-score, **Pan-Tompkins** R-peaks, **180-sample** beats (p.5–6).
  - Augmentation: SMOTE, time warping, amplitude scaling and Gaussian noise, plus inverse-frequency class weights.
  - Model sizes are roughly CNN **250K**, LSTM **120K** and CNN-LSTM **450K** parameters (p.6–7).
- **Split:** **Inter-patient** by record: **33** train, **7** validation and **8** test records, plus 5-fold cross-validation with 95% confidence intervals (p.6).
- **Results** (Table, p.7):

  | Model | Accuracy |
  |---|---|
  | ANN | 92.3 ± 1.2% |
  | CNN | 96.8 ± 0.8% |
  | RNN | 94.1 ± 1.5% |
  | LSTM | 97.2 ± 0.7% |
  | **CNN-LSTM** | **98.5 ± 0.5%** |

  - CNN-LSTM also reaches sensitivity **96.8%**, specificity **99.1%**, precision **97.2%** and F1 **97.0%**.
  - CNN-LSTM per-class F1: N **99.1**, SVEB **93.3**, VEB **96.6**, F **89.8**, Q **94.7** (p.7).
  - Cost: **4.2 ms**/beat inference and **6.8 MB** (p.7).
- **Limitation:** Single database, imbalance, and interpretability still needed (p.8). The CSV reviewer also notes the text cites "Figure 19 (Pages 155–165…)" and a "Figure 20", which do not exist in this 8-page paper (p.7). **My analysis:** with only 8 test records, a single split has high variance. S-class F1 of 93.3% is far above the inter-patient averages in Xiao [10] (F1 79.48%, p.16), so treat it with caution.
- **Relation to our project:** It is the only head-to-head comparison, and it supports a **CNN-LSTM baseline** over CNN alone (Stage 1 §1.7: shape + timing).

#### [26] Wang & Rani, 2026: "Hybrid CNN-LSTM model for ECG-based arrhythmia detection in internet of medical things" (*Discover Internet of Things*)
- **Problem:** Can a CNN compress each beat so that an LSTM can run fast enough for wearable (IoMT) devices?
- **Dataset:** MIT-BIH, **40** records with lead II and V1 (p.8). **94,131** beats: N 79,607, S 2,702, V 7,135, F 793, Q 3,894 (Table 1, p.9).
- **Method:**
  - A 15-layer VGG-style 1D-CNN compresses each **300-sample** beat into a **38-dimensional** feature vector (p.7).
  - An LSTM with attention then classifies it.
  - Preprocessing: detrending and wavelet denoising.
  - **Sliding-window augmentation** of the S and F classes in the training set (p.7–8, p.11).
- **Split:** Random **beat-level** split: 75% development and 25% test (p.9). Patient separation not described.
- **Results:**
  - Accuracy **99.20%**, sensitivity **94.07%**, specificity **98.14%** (p.13).
  - An LSTM on raw beats gets **99.16%** but takes **4.5 h** to train, vs **0.78 h** for the CNN-LSTM (p.10–11).
  - Augmentation raised S and F sensitivity by **8.57%** and **9.38%** (p.11).
  - Inference takes **85 ms**/beat on a Jetson Nano (p.15).
- **Limitation:** S and F are still the weakest classes, and only selected records and leads are used (p.11–12, p.15). The CSV reviewer notes internal inconsistencies: the LSTM is given as 32 units in one place and 256 in another, and the model is described as both "series" and "parallel".
- **Relation to our project:** Shows the **CNN front end makes the LSTM cheap**, which is useful if we want our hybrid to be light. Its accuracy is again intra-patient.

#### [24] Reddy et al., 2025: "A multi-scale convolutional LSTM-dense network for robust cardiac arrhythmia classification from ECG signals" (*Computers in Biology and Medicine*)
- **Problem:** Can multi-scale convolutions, dense blocks and a BiLSTM give accurate, noise-robust classification?
- **Dataset:** MIT-BIH, 5 beat types **N, V, A, R, L**. These are *not* the AAMI groups: R and L are bundle-branch beats, which AAMI puts inside N. Initial counts were 75,011 / 8,071 / 7,255 / 2,546 / 7,129 (p.4).
- **Method:**
  - **Multi-scale CNN:** three parallel Conv1D branches with kernels 5, 7 and 9, so the network sees short and long patterns at once.
  - Then **dense blocks** (growth rate 24, p.9), a BiLSTM (64 units) and a dense head.
  - Wavelet denoising, chosen over moving-average and median filters (p.7). It gives an SNR of **11.56 dB** (p.7).
  - Random oversampling of minority classes, with N downsampled to **5,000** (p.3).
- **Split:** Not clearly stated. It is described as 15,000/5,000/5,000 (p.3), as 70/15/15 (p.13) and as 5-fold CV (p.20). Patient separation is not described.
- **Results:**
  - Mean 5-fold accuracy **98.22%** (SD **0.17%**) (p.1, p.21).
  - Per-class F1: N **0.9781**, V **0.9954**, A **0.9867**, R **0.9699**, L **0.9936** (p.16).
  - With added Gaussian noise (SNR 5–30 dB, **400,048** beats) accuracy is **96.26%** (p.11–12).
  - **Without balancing**, validation accuracy is **74.86%**, with every prediction being N (p.4). This is a real-life example of the "always N" model from Stage 1 §1.10.
- **Limitation:** Signs of overfitting, high computational cost, and noise variation listed as a limitation (p.14–16, p.24). The CSV reviewer notes the split is described three ways, balancing may have happened before splitting, and the ethics statement refers to an unrelated brain dataset (p.25).
- **Relation to our project:** The multi-scale idea is worth borrowing. Its noise test uses only **Gaussian** noise, not real NSTDB noise, which supports Gap 3.

### c. Comparison table

| Ref | Model | Classes | Split | Headline result | Weakest class |
|---|---|---|---|---|---|
| [17] Ahmed | 1D-CNN | N, S, V, F | Beat-level random (p.6) | Acc 0.99, macro F1 0.93 (p.11) | F (F1 0.85, p.11) |
| [25] Pramkeaw | CNN-LSTM (vs ANN/CNN/RNN/LSTM) | N, S, V, F, Q | **Inter-patient, 8 test records** (p.6) | Acc 98.5 ± 0.5% (p.7) | F (F1 89.8, p.7) |
| [26] Wang | CNN → LSTM + attention | N, S, V, F, Q | Beat-level random (p.9) | Acc 99.20%, Se 94.07% (p.13) | S, F (p.11) |
| [24] Reddy | Multi-scale CNN + dense + BiLSTM | N, V, A, R, L (not AAMI) | Unclear (p.3, p.13, p.20) | 5-fold acc 98.22% (p.21) | R (F1 0.9699, p.16) |

### d. Agreement, disagreement, and what is missing
- **Agree:**
  - Adding a recurrent layer after a CNN helps (in [25], CNN-LSTM 98.5% vs CNN 96.8%, p.7).
  - Minority classes need balancing ([24] collapses to all-N without it, p.4; [26] gains 8–9% sensitivity from augmentation, p.11).
  - F and S are the hardest classes.
- **Disagree / not comparable:**
  - The class sets differ: [24] does not use AAMI classes, and [17] drops Q.
  - The splits differ: only [25] is inter-patient.
  - So you cannot rank these papers by accuracy.
- **Missing:**
  - **None** of the four has any XAI.
  - Only [24] tests noise, and only synthetic Gaussian noise.
  - None tests on an external dataset.

### e. New terms introduced in this batch
- **Class weights:** multiply each class's loss by a weight, usually inversely proportional to its frequency, so mistakes on rare classes cost more.
  *Example:* with N = 900 and F = 10 beats, weight(F) / weight(N) = 900/10 = 90. One missed F beat then costs as much as 90 missed N beats.
- **Oversampling / SMOTE:**
  - Random oversampling copies minority beats.
  - **SMOTE** (Synthetic Minority Over-sampling Technique) creates *new* synthetic beats by interpolating between a minority beat and one of its nearest minority neighbours: x_new = x_a + λ·(x_b − x_a), with λ between 0 and 1.
  - *Example:* sample values 0.2 and 0.6 with λ = 0.5 give 0.4.
  - **Rule:** do it **only after splitting**, on the training set. Otherwise synthetic copies of test beats leak into training.
- **Sliding-window augmentation:** making extra training beats by shifting the cut-out window by a few samples ([26]).
- **Multi-scale convolution:** several conv branches with different kernel sizes run in parallel and are then concatenated. *Example:* kernels 5, 7 and 9 at 360 Hz see 14, 19 and 25 ms of signal.
- **Dense block (DenseNet):** each layer receives the outputs of *all* earlier layers in the block. The "growth rate" is how many new channels each layer adds (24 in [24]).
- **Batch normalisation:** rescales each layer's outputs to mean 0 and standard deviation 1 within a mini-batch. This stabilises training.
- **Dropout:** randomly switches off a fraction p of neurons during training, for example p = 0.2, so the network cannot rely on any single neuron. This fights overfitting.
- **k-fold cross-validation:** split the data into k parts. Train on k−1 parts and test on the remaining one, rotating k times, then average. It gives a mean ± standard deviation. Note that it is only patient-independent if the *folds* are split by patient.
- **Inference latency:** the time to classify one input, for example 4.2 ms/beat in [25] (p.7). It matters for real-time devices.
- **Edge / IoMT device:** a small computer near the patient, such as a Jetson Nano or Raspberry Pi, rather than a cloud server.

### f. Examiner questions with model answers
1. **"Why does your baseline use a CNN-LSTM rather than just a CNN?"**
   *Answer:* The CNN captures beat morphology, and the LSTM captures temporal dependencies. In the only head-to-head comparison in our set (Pramkeaw et al.), under an inter-patient split, CNN-LSTM reached 98.5% vs 96.8% for CNN alone. Kulkarni's review also finds hybrid CNN-RNN models efficient for their accuracy.
2. **"Ahmed et al. get 99% with a simple CNN. Why not just copy that?"**
   *Answer:* Their split is a random beat-level split, so beats from the same patient appear in both training and test sets. That is intra-patient evaluation and inflates the result. We will use the DS1/DS2 inter-patient split, where we expect lower but honest numbers.
3. **"How do you handle class imbalance, and where do you apply it?"**
   *Answer:* With class-weighted loss, and possibly oversampling, applied only to the training set after the split. Reddy et al. show that without balancing their model predicts only the normal class (74.86% validation accuracy). Balancing before the split would leak information into the test set.

---

## Batch 3: Attention and transformer hybrids

### a. What question this batch tries to answer
*"Does adding self-attention or transformers (Stage 1 §1.7) on top of convolutional features improve beat classification, especially for the hard S and F classes, and at what cost?"*

### b. Paper by paper

#### [37] Akan et al., 2024: "ECGformer: Leveraging transformer for ECG heartbeat arrhythmia classification" (arXiv 2401.05434; **newly added to the CSV**)
- **Problem:** Can a plain encoder-only Transformer classify heartbeats directly from the signal?
- **Dataset:** MIT-BIH beats **as pre-processed by Kachuee et al.** and published on Kaggle (p.3, p.5). Beats are fixed at **188** samples at **125 Hz** (p.3). There are **109,446** beats in 5 AAMI classes, with a fixed split of **87,554 train / 21,892 test** (p.3). PTB is also named, but no PTB results are reported.
- **Method:**
  - Each beat is split into **patches**. Each patch gets a linear embedding and is treated like a "word" (token), as in NLP (p.2).
  - Then come **4 encoder layers** with **8 heads** of size **16**, MLP layers [128, 64], and dropout **0.15** (Tables II–III, p.3).
  - The whole model has only **36,301** parameters (p.3).
  - Training: Adam (lr 1e-4), batch 32, **100** epochs (p.3).
- **Split:** The fixed Kaggle beat split. Patient separation is not described, so it is effectively intra-patient.
- **Results** (Table IV, p.4):
  - Accuracy **0.98**.
  - **Macro** precision **0.95**, recall **0.80**, F1 **0.86**.
  - Per-class recall: N **1**, S **0.58**, V **0.92**, F **0.54**, Q **0.97**.
  - Per-class F1: S **0.73**, F **0.66**.
- **Limitation:** There is no limitations section. **CSV/PDF inconsistencies, recorded in the new CSV row:**
  - The text says S recall is 0.54, but Table IV says **0.58** (p.4).
  - The comparison text says 97%, but Table V and the Conclusion say **98%** (p.5).
  - PTB results are promised but not shown.
- **Relation to our project:** A clear warning example. Accuracy is 98%, yet the model **misses 42% of S beats and 46% of F beats**. That is exactly the Stage 1 §1.10 lesson. The authors themselves note accuracy misleads on imbalanced data (p.4).

#### [18] El-Ghaish & Eldele, 2024: "ECGTransForm: Empowering adaptive ECG arrhythmia classification framework with bidirectional transformer" (*BSPC*)
- **Problem:** How can a model capture both multi-scale shape and past-and-future temporal context, while handling imbalance without oversampling?
- **Dataset:** MIT-BIH, 5 AAMI classes, **87,554 train / 21,892 test** (Table 1, p.6). These are the **same Kaggle/Kachuee counts as [37]**, so the two papers are directly comparable. Also PTB, normal vs MI (11,636 / 2,909, p.6).
- **Method:**
  1. **Multi-scale convolutions** with kernels 5, 9 and 11, averaged.
  2. A **Channel Recalibration Module**, which works like squeeze-and-excitation (see terms below).
  3. A **Bidirectional Transformer (BiTrans)**: self-attention is run on the feature sequence *and* on a reversed copy, and the two are summed (p.5).
  4. A **Context-Aware Loss**, which uses logarithmic class weights.
- **Split:** 80/20 train/test (p.6). Patient separation not described.
- **Results:**
  - MIT-BIH accuracy **99.35 ± 0.16%**; **macro F1 94.26 ± 0.28%** (p.7).
  - Per-class F1: N **99.41**, S **89.22**, V **96.69**, F **86.78**, Q **99.18** (p.7).
  - Ablation (p.8): plain CNN F1 **88.1%** → + multi-scale **90.4%** → + recalibration **+0.9%** → BiTrans **+2.35%**. A standard Transformer adds only **+0.15%**.
  - Context-Aware Loss gives S F1 **89.22%**, vs **74.84%** for oversampling and **64.15%** for a balanced sampler (p.8).
- **Limitation:** It still struggles with F and S, the transformer is computationally costly, and cross-dataset generalisation is needed (p.9).
- **Relation to our project:** On the *same* split, it beats ECGformer by a wide margin in macro F1 (94.26% vs 86%). That shows convolutional front-ends + attention > attention alone. The ablation is a good model for how we should test our own components.

#### [20] Ikram et al., 2025: "Transformer-based ECG classification for early detection of cardiac arrhythmias" (*Frontiers in Medicine*)
- **Problem:** Can a small Transformer on selected features detect arrhythmias early?
- **Dataset:** "MIT-BIH benchmark dataset" from Kaggle (p.16). 5 classes: Normal, APC, VPC, Fusion, Other. Approximately **18,000** Normal, **560** APC and **1,400** VPC samples (p.8).
  - *My observation, not stated by the authors:* these counts are close to the Kachuee **test-set** counts in [37] (18,118 / 556 / 1,448, p.3).
- **Method:**
  - Features are selected with PCA and correlation analysis.
  - A dense projection to 64 dimensions feeds **1** transformer block with 4 heads, followed by global average pooling and softmax.
  - It is trained for **10** epochs (p.8).
- **Split:** "Training and testing subsets". Ratio and patient separation not described.
- **Results:**
  - Accuracy **97%** (p.8); with PCA **97.1%** vs **92.3%** without (p.10).
  - Per-class AUC: Normal **0.98**, APC **0.94**, VPC **1.00** (p.10).
  - From the confusion matrix (p.11): **33.1%** of APC and **43.8%** of Fusion beats are misclassified as Normal.
- **Limitation:** The authors list imbalance, homogeneous data, computational cost, black-box behaviour and non-interpretable PCA features (p.14–15). The CSV reviewer notes that the text claims near-perfect Fusion F1 and 100% APC recall, which contradicts the confusion matrix.
- **Relation to our project:** Shows why AUC and accuracy can look high while the minority-class confusion matrix is poor. We must always show the confusion matrix.

#### [23] Liu, 2025: "A hybrid model combining 1D-CNN and BERT for intelligent ECG arrhythmia classification" (*Scientific Reports*)
- **Problem:** Can CNN local features plus a BERT-style bidirectional encoder for global context improve minority classes?
- **Dataset:** MIT-BIH, 5 AAMI classes, plus a 9-class experiment.
- **Method:**
  - A 1D-CNN local feature extractor.
  - A **BERT-style** bidirectional Transformer encoder with a **[CLS]** token (p.2, p.5).
  - **Cross-modal attention and gated fusion** of the CNN and BERT features (p.6).
  - **Focal loss** (p.5).
  - Preprocessing: 0.5–50 Hz band-pass, plus time-stretch and amplitude-scale augmentation.
- **Split:** 70/10/20 (p.6). Patient separation not described.
- **Results:**
  - 5-class per-class F1: N **99.66**, S **92.84**, F **97.83**, V **84.47**, Q **99.79** (p.8).
  - 9-class accuracy **99.12%**, F1 **95.36%** (p.9).
  - Ablation: CNN-BERT F1 **95.904%** vs BERT alone **95.274%** (p.9).
- **Limitation:** V is the weakest class, the model is a black box, and only MIT-BIH is used (p.8, p.11). The CSV reviewer notes inconsistent architecture descriptions (4 heads/256-dim vs 12 heads/768-dim, p.5) and a claimed multi-dataset validation that is not shown.
- **Relation to our project:** Unusually, F is strong here and **V is weak**, the reverse of most papers. That is a sign that per-class behaviour depends heavily on the architecture and split. The authors list **Grad-CAM, SHAP and Integrated Gradients as future work**, which is exactly our addition.

#### [36] Huang et al., 2026: "MSCA-TNet based deep learning method for ECG arrhythmia classification" (*Scientific Reports*)
- **Problem:** Combine multi-scale convolution, channel attention and a contextual Transformer, and check generalisation on a second database.
- **Dataset:**
  - MIT-BIH: 48 records, 47 subjects, 360 Hz, 5 AAMI classes (p.3).
  - INCART: 75 recordings from **32** patients at **257 Hz**, used for cross-database validation as 2 classes, N vs A (p.9).
- **Method:**
  - db5 wavelet denoising (p.3) and **180-sample** beats.
  - Multi-scale convolution with kernels 3, 5, 7 and 9.
  - **Adaptive Channel Attention**.
  - A **dual-input contextual Transformer** that sees the original and a flipped sequence (p.5).
  - **SMOTE-Tomek** on the training set only (p.3–4).
  - Code is released on Zenodo (p.6).
- **Split:** A **random 65/15/20** split (p.3). Patient separation not described.
- **Results:**
  - MIT-BIH accuracy **98.88%**, **macro-F1 93.97%** (p.1, p.7).
  - Per-class F1: N **99.40**, S **89.67**, V **97.47**, F **83.99**, Q **99.29** (p.7).
  - INCART (N vs A): accuracy **99.47%**, macro-F1 **98.79%** (p.9).
  - Ablation (p.8): removing SMOTE-Tomek costs **−6.08%** macro-F1, including **−10.69%** S-F1. Replacing the Transformer with a BiLSTM gives macro-F1 **90.23%**.
- **Limitation:** Only MIT-BIH and INCART, real wearable noise not verified, and S/F still insufficient (p.11). The CSV reviewer notes the abstract calls the macro-F1 values "macro-average accuracies".
- **Relation to our project:** It is honest that comparisons with published results are not strictly fair because of different partitioning, and it uses its own ablations instead (CSV, p.8). Its released code makes it a candidate reference implementation.

### c. Comparison table

| Ref | Attention type | Params | Split | Macro-F1 | S F1 | F F1 |
|---|---|---|---|---|---|---|
| [37] ECGformer | Encoder-only Transformer on patches | 36,301 (p.3) | Kaggle beat split | 0.86 (p.4) | 0.73 | 0.66 |
| [18] ECGTransForm | Multi-scale CNN + recalibration + **bidirectional** Transformer | not stated in CSV | Same Kaggle beat split (p.6) | **94.26%** (p.7) | 89.22 | 86.78 |
| [20] Ikram | 1 Transformer block on PCA features | not stated | Not described | F1 0.95 (p.12) | (33.1% APC → N, p.11) | (43.8% → N, p.11) |
| [23] Liu | CNN + BERT + gated cross-attention | not stated | 70/10/20 (p.6) | not stated (5-class) | 92.84 | 97.83 |
| [36] Huang | Multi-scale CNN + channel attention + contextual Transformer | not stated | Random 65/15/20 (p.3) | 93.97% (p.7) | 89.67 | 83.99 |

### d. Agreement, disagreement, and what is missing
- **Agree:**
  - Pairing convolution with attention beats attention alone. The clearest evidence is [18] vs [37] on the *same split*, and [36]'s ablation, where replacing the Transformer with a BiLSTM drops macro-F1 to 90.23% (p.8).
  - **S and F remain the weakest classes** ([18] p.9; [36] p.11; [37] p.4).
  - The imbalance strategy matters as much as the architecture ([18]'s loss, p.8; [36]'s SMOTE-Tomek, p.8).
- **Disagree:**
  - Which minority class is hardest: V in [23] (F1 84.47) vs F in [18], [36] and [37].
  - Whether a *standard* Transformer helps: only +0.15% in [18] (p.8).
- **Missing:**
  - **All five use beat-level random or unknown splits.** None uses DS1/DS2.
  - **None provides XAI**, even though attention weights are available for free (Stage 1 §1.11).
  - Only [36] has a second dataset.

### e. New terms introduced in this batch
- **Patch embedding / token:** cut the signal into short pieces ("patches"). Each patch becomes a vector through a learned linear layer and is treated like a word token.
  *Example:* a 177-sample beat cut into patches of 16 samples gives about 11 tokens.
- **Encoder-only Transformer:** the "understanding" half of the original Transformer. It has no decoder, because we classify and do not generate ([37] p.3).
- **Bidirectional Transformer / reversed sequence:** process the sequence forwards and backwards (flipped), then combine. This gives each time step both past and future context ([18] p.5, [36] p.5). It is the attention analogue of a BiLSTM.
- **BERT and the [CLS] token:** BERT is a bidirectional Transformer encoder from NLP. A special [CLS] token is added at the start, and its final vector is used as the summary of the whole sequence for classification ([23] p.5).
- **Squeeze-and-Excitation (SE) / channel attention:**
  1. Average each channel over time (squeeze).
  2. Pass the averages through a tiny network ending in a sigmoid to get one weight between 0 and 1 per channel (excitation).
  3. Multiply each channel by its weight.

  *Example:* channel means [2.0, 0.1] give weights [0.9, 0.2], so the network "turns up" the useful channel.
- **Focal loss:** loss = −(1 − p)^γ · ln p. It down-weights easy examples.
  *Example:* with γ = 2, an easy beat with p = 0.9 contributes (0.1)² × 0.105 = 0.00105. A hard beat with p = 0.3 contributes (0.7)² × 1.204 = 0.59, more than 500 times more.
- **SMOTE-Tomek:** SMOTE oversampling followed by removing "Tomek links", which are pairs of nearest neighbours from different classes. This cleans the class boundary.
- **Ablation study:** remove or replace one component at a time and measure the drop. It shows which parts really matter ([18] p.8, [36] p.8).
- **AUC (Area Under the ROC Curve):** the probability that the model scores a random positive higher than a random negative. 0.5 is chance and 1.0 is perfect. It can be high even when recall at the chosen threshold is poor, as in [20].
- **PCA (Principal Component Analysis):** rotates the features into new axes ordered by how much variance they explain, then keeps the top few. The new axes are mixtures of the original features, so they are hard to interpret clinically ([20]).
- **UMAP / t-SNE:** methods that squash high-dimensional features into 2D for plotting clusters. They are visualisation tools, **not explanations** of a single decision.

### f. Examiner questions with model answers
1. **"Transformers are state of the art. Why not use a pure Transformer?"**
   *Answer:* In our literature, on the identical Kaggle MIT-BIH split, a pure encoder-only Transformer (ECGformer) reached macro-F1 of about 0.86, while ECGTransForm, which puts multi-scale convolutions before a bidirectional Transformer, reached 94.26%. Kulkarni also finds attention models gain only about 0.8% on average and become costly beyond about 1 M parameters. So a convolutional front-end with a light attention or recurrent stage is the better trade-off for our data size.
2. **"ECGformer reports 98% accuracy. Is that a good model?"**
   *Answer:* Not for the clinically important classes. Its S recall is 0.58 and its F recall 0.54, so it misses roughly half of those beats. Accuracy is high only because about 83% of test beats are normal (18,118 of 21,892). Macro-F1 of 0.86 is the honest summary.
3. **"How would you show that each part of your model is necessary?"**
   *Answer:* With an ablation study, like ECGTransForm and MSCA-TNet. Train the full model, then remove or replace one component at a time, and report the change in macro-F1 and per-class F1 under the same inter-patient split.

---

## Batch 4: Changing the input representation

### a. What question this batch tries to answer
*"Instead of feeding the network a raw 1D beat, what happens if we feed it a time-frequency picture, a drawn image, a graph of waves, or extra patient information?"*

This batch also shows Grad-CAM and CAM used on real models, as a warm-up for Batch 5.

### b. Paper by paper

#### [21] Kim et al., 2025: "A novel hybrid CNN-transformer model for arrhythmia detection without R-peak identification using Stockwell transform" (*Scientific Reports*)
- **Problem:** Can we skip R-peak detection entirely (Stage 1 §1.5 step 3) by classifying 10-s segments as time-frequency images?
- **Dataset:**
  - MIT-BIH, 5 AAMI classes, augmented with **SMOTE** (p.2).
  - **Icentia11k**, with more than **11,000** patients and 4 classes (p.2).
- **Method:**
  - Preprocessing: low-pass filter, downsampling to 100 Hz, **detrending**, then 10-s segments.
  - **Stockwell transform** from 0 to 15 Hz. Its real and imaginary parts become a 2D input (p.3–5).
  - The model is a ResNeXt CNN with SE blocks, followed by a 4-layer Transformer (8 heads) (p.4–5), trained with focal loss.
- **XAI:** **Class Activation Maps (CAM)** on the time-frequency input (p.8).
- **Split:** Not stated. Train/test partitioning and patient separation are not described. SMOTE was applied to "the MIT-BIH dataset" (p.2), and the paper does not say whether this happened before or after splitting.
- **Results:**
  - Accuracy: MIT-BIH **99.58%** and Icentia11k **97.80%** (p.7).
  - MIT-BIH F1 for F and Q: **1.0000** (p.7).
  - Ablation (p.7): **1D CNN 31.73%**, 1D Transformer **67.26%**, 2D CNN **99.41%** on MIT-BIH.
  - Detrending is the most impactful preprocessing step (p.6).
- **Limitation:** Only two datasets, the S-transform is computationally heavy, and borderline cases (N misread as V) remain (p.8–9).
- **My caution (not stated by the authors):**
  - Perfect F1 = 1.0000 on the rarest class, F, together with SMOTE applied to the dataset with no stated split, is a warning sign of possible leakage.
  - A 1D CNN scoring only 31.73% is far below every other 1D CNN in our set (e.g. [17] 0.99). That suggests the 10-s segment task is quite different from beat classification.
- **Relation to our project:** It introduces **time-frequency inputs** and **CAM**. We will stay with 1D beats, so that Grad-CAM maps line up with P/QRS/T on the time axis, which is easier for a clinician to read.

#### [5] Tenepalli & Navamani, 2025: "Design of an Explainable Deep Learning Framework for ECG-Based Arrhythmia Prediction" (*IEEE Access*)
- **Problem:** Can drawing each beat as an image let us reuse powerful pretrained image networks, with Grad-CAM to explain them?
- **Dataset:** MIT-BIH lead II. **112,559** beat images: **105,430** non-PVC and **7,129** PVC (p.6).
- **Method:**
  - Each **250**-sample beat (about 0.7 s, p.4–5) is band-pass filtered at 0.5–40 Hz.
  - The beat is **plotted as a 224 × 224 RGB image** (p.5).
  - A frozen **ImageNet-pretrained EfficientNetB0** feeds a 2-head Transformer block and a sigmoid output. The task is **binary**: PVC vs non-PVC.
- **XAI:** **Grad-CAM** on the last EfficientNet conv layer, plus **attention heat maps**.
- **Split:** **80/20 random split** of beat images, **90,047 / 22,512**, random_state 42 (p.6). Patient separation not described.
- **Results:**
  - Test accuracy about **99%** (p.1); ROC AUC about **0.997** (p.10).
  - ImageNet pretraining gives **99%** vs **95.12%** from random initialisation (p.11).
  - Grad-CAM heatmaps consistently highlight the QRS/R-peak and atypical depolarisation regions linked to PVC (CSV findings; Grad-CAM figures p.8–9).
- **Limitation:** MIT-BIH only, not tested under heavy noise, binary only, and single lead (p.13).
- **Relation to our project:** The first real **Grad-CAM-on-ECG** example in our set. The explanation is checked only **visually**: no faithfulness test, no clinician, and no consistency measure. That is Gap 1.

#### [22] Lee et al., 2025: "ECG-GraphNet: Advanced arrhythmia classification based on graph convolutional networks" (*Heart Rhythm O2*)
- **Problem:** Can we represent a heartbeat the way a cardiologist thinks about it, as P, QRS and T *segments* linked by timing, and classify that structure?
- **Dataset:** A **private** single-lead patch ECG dataset from **328** patients (p.1). It has **1,253** ten-second segments and **17,526** beats (p.3): N **75.0%**, S **15.2%**, V **10.4%** (p.4). The P-QRS-T onsets and offsets were annotated by technicians and reviewed by a cardiologist.
- **Method:**
  - Each P, QRS and T segment becomes a **node**. Its features are segment type, width, an autoencoder waveform embedding, and distances.
  - **Edges** connect segments, weighted by time distance.
  - Graph convolution blocks are followed by QRS-centred pooling.
- **Split:** **Inter-patient** 5-fold cross-validation with no patient overlap (p.6).
- **Results:**
  - Macro F1 **88.61%**, accuracy **93.52%** (p.8).
  - Per-class F1: N **96.62**, S **84.16**, V **85.05** (p.8).
  - Distance features raised S F1 from **73.59%** to **81.00%** (p.4, p.8).
  - Graph augmentation raised V F1 from **77.94%** to **81.93%** (p.7–8).
- **Limitation:**
  - It needs the onset and offset of every P-QRS-T segment *before* classification (p.10).
  - Only 3 classes; private data.
  - The authors work for the device company and have filed a patent (p.11).
- **Relation to our project:** The S-class gain from distance (timing) features confirms Stage 1 §1.2: **S beats are defined by timing**. That supports adding RR-interval inputs to our beat model.

#### [19] Chen et al., 2025: "Large Language Model-assisted multi-scale hierarchical classification of ECG signals" (*Knowledge-Based Systems*)
- **Problem:** Can we use the hierarchy of diagnoses (superclass → subclass → specific diagnosis), plus patient age and sex, to improve 12-lead classification?
- **Dataset:**
  - **PTB-XL** at 100 Hz, using the **17,183** records that have age and sex, split **13,746 / 1,718 / 1,719** (Table 1, p.6). Tasks have **5**, 23 and 44 classes.
  - **SPH** (Chapman-Shaoxing-Ningbo), **18,842** records (p.6).
- **Method:**
  - A multi-scale Transformer branch whose patch sizes come from FFT-detected periods.
  - Age and sex are turned into **text prompts**, encoded by a **frozen BERT**, and fused with the signal patches (p.3–4).
  - A parallel TCN (dilated causal convolution) branch.
  - Outputs are aggregated hierarchically from coarse to fine levels.
- **XAI:** **Grad-CAM** to visualise what each branch focuses on (p.11), plus t-SNE (p.10–11).
- **Split:** About 80/10/10 by record (p.6). Patient separation not described. **Note:** PTB-XL provides patient-respecting folds (Stage 1 §1.8), but this paper does not say it used them.
- **Results:**
  - PTB-XL superclass: AUC **91.30**, F1 **77.56** (p.7).
  - Subclass F1 **64.61**, falling to **58.80** without the hierarchy (p.8).
  - SPH superclass F1 **86.40** (p.7).
- **Limitation:** Simple weighted fusion; prompts add computational overhead; records without age/sex were dropped; a small LLM (BERT) was used because of limited GPU (p.12, p.3–4).
- **Relation to our project:** It shows that **patient metadata and disease hierarchy** can help on PTB-XL. It is a future-work idea for us, not a baseline.

### c. Comparison table

| Ref | Input representation | Task / classes | Split | Headline result | XAI |
|---|---|---|---|---|---|
| [21] Kim | Stockwell time-frequency (2D) of 10-s segment | MIT-BIH 5-class; Icentia11k 4-class | Not stated; SMOTE on dataset (p.2) | Acc 99.58% / 97.80% (p.7) | CAM (p.8) |
| [5] Tenepalli | Beat plotted as 224 × 224 image | PVC vs non-PVC | 80/20 random (p.6) | Acc ~99%, AUC 0.997 (p.1, p.10) | Grad-CAM + attention maps |
| [22] Lee | Graph of P/QRS/T segment nodes | N, S, V (private, 328 patients) | **Inter-patient 5-fold** (p.6) | Macro F1 88.61% (p.8) | Not stated |
| [19] Chen | Multi-scale patches + age/sex text prompts | PTB-XL 5/23/44 classes | ~80/10/10 records (p.6) | Super AUC 91.30, F1 77.56 (p.7) | Grad-CAM (p.11) |

### d. Agreement, disagreement, and what is missing
- **Agree:** The representation choice can matter as much as the network.
  - [21]: 2D CNN 99.41% vs 1D CNN 31.73% on their task (p.7).
  - [22]: timing features add about 7 points of S F1 (p.4, p.8).
  - [19]: the hierarchy adds about 6 points of subclass F1 (p.8).
- **Disagree:**
  - [21] says R-peak detection can be avoided, while [22] goes the other way and needs *even more* detection (all P, QRS and T boundaries).
  - Both trade-offs are real. Skipping detection removes one error source. Fine segmentation gives clinically meaningful units that are easy to explain.
- **Missing:**
  - Only Lee [22] uses an inter-patient split.
  - The XAI in [5], [19] and [21] is shown as example pictures only, with **no quantitative check** (faithfulness, consistency, or clinician agreement).

### e. New terms introduced in this batch
- **Time-frequency representation:** a 2D map showing *which frequencies* are present *at which time*. Think of a music score: time runs left to right, pitch bottom to top.
- **Stockwell transform (S-transform):** a time-frequency transform that uses frequency-dependent Gaussian windows. It is narrow in time for high frequencies (sharp QRS) and wide for low frequencies (slow T waves), and it keeps phase information. It is a cousin of the wavelet transform.
- **Detrending:** removing slow drift (baseline wander) by fitting and subtracting a smooth trend line.
  *Example:* a signal [1.0, 1.2, 1.4] that is drifting up by 0.2 per sample, minus the trend [1.0, 1.2, 1.4], gives [0, 0, 0].
- **Transfer learning / ImageNet pretraining:** start from a network already trained on 1 million+ natural photos, then fine-tune it on your data. Early layers already detect edges and shapes. [5] gains about 4 points from this (p.11).
- **EfficientNet:** a family of image CNNs scaled carefully in depth, width and resolution. B0 is the smallest.
- **CAM (Class Activation Map):** the original, simpler form of Grad-CAM. It works when the network ends with global average pooling and a single dense layer, using that dense layer's weights instead of gradients.
- **Graph / node / edge / graph convolution:** a graph is a set of nodes (here, P, QRS and T segments) joined by edges (here, time relationships). Graph convolution updates each node by mixing in its neighbours' features.
  *Example:* node value 2 with neighbours 4 and 6, using a simple average, becomes (2 + 4 + 6)/3 = 4.
- **TCN (Temporal Convolutional Network):** a stack of dilated causal 1D convolutions. "Causal" means each output only sees the past.
- **Dilated convolution:** a kernel with gaps. A kernel of size 3 with dilation 2 covers samples [t, t+2, t+4], so the receptive field grows without extra weights.
- **Prompt / text embedding:** converting text such as "Age 63, male" into a vector with a language model like BERT, so it can be fused with signal features.
- **Hierarchical / multi-task classification:** predict coarse labels (e.g. "conduction disturbance") and fine labels (e.g. "LBBB") together, passing information from coarse to fine.

### f. Examiner questions with model answers
1. **"Why not convert the ECG to an image and use a pretrained CNN, as Tenepalli does?"**
   *Answer:* It works well for binary PVC detection, but the image adds a large backbone and makes Grad-CAM maps live in image pixels rather than time samples, so they are harder to map onto P, QRS and T. Its split is also random beat-level. A 1D model gives explanations directly on the time axis that a cardiologist recognises, at lower cost.
2. **"Kim et al. avoid R-peak detection. Why does your pipeline still detect R peaks?"**
   *Answer:* Beat-level classification under the AAMI standard and the DS1/DS2 protocol is defined per beat, and beat windows make the explanations align with the P-QRS-T structure. R-peak detection on MIT-BIH is mature (Pan-Tompkins). Kim's approach is attractive, but their split is not described and the SMOTE timing is unclear, so their 99.58% is not comparable with an inter-patient result.
3. **"What does Lee's graph model tell us about S beats?"**
   *Answer:* Adding distance (timing) features raised S-class F1 from 73.59% to 81.00%. That confirms S beats are distinguished mainly by prematurity, not shape. So our model should include RR-interval features, and our explanations for S beats should highlight timing, such as the pre-RR interval, rather than only the waveform.

---

## Batch 5: XAI on MIT-BIH (what is explained, and how well)

### a. What question this batch tries to answer
*"When papers call their ECG framework 'explainable', what do they actually compute? Do the explanations make clinical sense, and does anyone test them?"*

The first four papers apply XAI. The fifth, Beck & John [2], **tests** XAI methods critically.

### b. Paper by paper

#### [1] Alamatsaz et al., 2024: "A lightweight hybrid CNN-LSTM explainable model for ECG-based arrhythmia detection" (*BSPC*)
- **Problem:** Build a model small enough for a Holter-type device, which classifies 8 arrhythmias plus normal rhythm and explains itself.
- **Dataset:** MIT-BIH plus the **Long-Term AF database (LTAF)**, with MIT-BIH resampled to **128 Hz** to match (p.3).
- **Method:**
  - Median-filter baseline removal, normalisation to [−1, 1], and **500-sample overlapping segments** (p.3). At 128 Hz, 500 samples is 500/128 ≈ 3.9 s, so this is **rhythm-level**, not single-beat, classification.
  - An 11-layer 1D-CNN with 3 conv blocks, followed by an LSTM (**32** units) and softmax over **9** classes (p.3–5).
  - Class weights handle imbalance (p.3).
- **XAI:** **SHAP** per class, on unseen test data.
- **Split:** **85/15** of the segmented data (p.3–4). Patient separation not described.
- **Results:**
  - Accuracy **98.24%**, sensitivity **86.1%**, specificity **97.5%** (p.5).
  - Model size **0.16 MB**; **5.127 ms** per rhythm on a Raspberry Pi (p.5).
  - SHAP highlights absent P waves, delta waves, wide QRS and pacing spikes, which the authors say agree with cardiologists' criteria (p.6, p.8).
- **Limitation:** Poor identification of AFIB, B and T rhythms; only two databases; only 2 leads (p.4, p.9–10).
- **My analysis:** If the 85/15 split is taken *after* cutting overlapping segments, neighbouring overlapping segments can end up in both train and test. That is an even stronger form of leakage than intra-patient splitting.
- **Relation to our project:** The closest match to our title (**CNN-LSTM + SHAP**, lightweight). But the explanation is checked only by eye against textbook features. No consistency or faithfulness metric is reported.

#### [4] Talukder et al., 2025: "An explainable deep learning framework for trustworthy arrhythmia detection from ECG signals" (*Scientific Reports*)
- **Problem:** Which class-balancing method works best, and can SHAP, LIME and feature-importance analysis explain the result?
- **Dataset:** MITDB, PTBDB (resampled to **360** Hz, p.5) and NSTDB. The task is **binary**: normal vs arrhythmia beats (p.5, p.7).
- **Method:**
  - **1-s R-centred windows**; Butterworth band-pass 0.5–**45** Hz and 50 Hz notch (p.7).
  - A 1D CNN with **128/64** filters (p.8), compared against a DNN.
  - Balancing methods compared: ADASYN, SMOTE, SMOTETomek, ROS and a GAN.
- **XAI:** **SHAP**, **LIME** and **Feature Importance Analysis**.
- **Split:** Held-out test set, ratio and patient separation not described. Balancing was applied to the training data.
- **Results:**
  - ROS + CNN accuracy: MITDB **99.74%**, PTBDB **99.43%**, NSTDB **99.98%** (p.1, p.11–13).
  - GAN + CNN on PTBDB gets **85.84%** (p.24).
  - The explanations are given as sample indices, e.g. **Time_33/34/35** on PTBDB and **Time_365–369** on NSTDB (p.17–18).
- **Limitation:** No feature fusion or transformer; binary only (p.26).
- **Relation to our project:** A cautionary example of **explanations that are not translated into clinical language**. "Time_365 is important" means nothing to a doctor until it is mapped onto P, QRS or T. Our framework must make that mapping.

#### [6] Asha et al., 2026: "ECG Arrhythmia Classification: a Lightweight, Explainable, and Web-Deployable Deep Learning Framework Using Knowledge-Distilled GAN Features and Flask" (*NRFHH*)
- **Problem:** Proposes training a heavy GAN-based classifier, then **distilling** it into a small CNN for a web app, with SHAP.
- **Dataset:** **Planned only**: MIT-BIH (AAMI, **DS1/DS2**, p.3, p.5) and PTB-XL.
- **Method (proposed):**
  - A cycle-consistent GAN for minority augmentation.
  - Response-based knowledge distillation into a light CNN.
  - A Flask web app.
  - SHAP computed offline.
- **Results:** **None.** The paper says its values are **projected performance targets** (p.5). Illustrative targets: GAN classifier **5.0 M** parameters, **21.4 MB**, **186 ms**; distilled CNN **0.31 M**, **1.6 MB**, **11 ms** (p.7).
- **Limitation:** Conceptual and not implemented (p.3, p.5, p.7). The CSV reviewer notes placeholder text in the results ("Lorem SHAP", p.3).
- **Relation to our project:** It has **no evidential value**. Cite it only as an idea (distillation for deployment), never for numbers.
  - *Observation:* its illustrative GAN figures (5.0 M params, 2.1 GFLOPs, p.7) are identical to those reported for the implemented model in [7] (p.14), and the two papers share an author (P. Kavitha).

#### [7] Kavitha & Shakkeera, 2026: "An explainable deep learning framework for accurate and automated cardiac arrhythmia classification using Electrocardiogram signals" (*BSPC*)
- **Problem:** A GAN-based classifier with metaheuristic hyperparameter tuning and SHAP, tested on many datasets.
- **Dataset:**
  - MIT-BIH; MIT-BIH Supraventricular; a 12-lead hospital dataset (**13,241** tests, p.3); PTB-XL.
  - External tests on Shaoxing-Ningbo and INCART.
- **Method:**
  - **Cycle-CMCHA-GAN**: a cycle-consistent GAN with a CNN classification head.
  - Hyperparameters tuned by an "Artificial Afterimage + Colour Harmony" optimisation algorithm (p.3).
  - Preprocessing: notch filter, DWT denoising, R-peak segmentation, and RR/QRS/QT/ST features.
  - SMOTE and class-weighted loss.
- **XAI:** **SHAP** on ECG features. Top MIT-BIH features: QRS (**0.350**) and RR interval (**0.290**) (p.7). Top PTB-XL feature: ST segment (**0.360**) (p.11).
- **Split:** **Inter-patient DS1/DS2** for MIT-BIH, with DS1 subdivided into DS11 for training and DS12 for validation (p.4).
- **Results:**
  - Accuracy: MIT-BIH **99.87%** (p.1, p.15); PTB-XL **99.88%** (p.15); INCART **98.67%** (p.15).
  - **But** Table 7 (p.6) gives MIT-BIH class-wise F1 of N **98.8**, V **88.3**, S **91.9**, F **83.8**, Unknown **77.6**, with recalls of 99.2, 87.1, 91.5, 82.7 and 75.3.
  - Table 19 gives mean accuracy **97%** (p.12, p.14).
- **Worked check (why this does not add up):** overall accuracy equals the **support-weighted average of the per-class recalls**:

  Acc = Σ (share_c × recall_c)

  The largest recall in Table 7 is 99.2% (Normal), so accuracy **cannot exceed 99.2%**. A reported 99.87% is impossible with those recalls. The CSV reviewer flagged the same inconsistency, and also that the data-availability statement says "No data was used" (p.16).
- **Limitation (authors'):** No clinical or multicentre validation (p.14–15).
- **Relation to our project:** It **does** use DS1/DS2 and SHAP, which is close to our objectives. But its numbers are internally inconsistent, so **do not cite its accuracy as a benchmark**. The useful takeaway is that SHAP on *named clinical features* (QRS, RR, ST) produces explanations a doctor can read.

#### [2] Beck & John, 2025: "Explainable AI (XAI) for Arrhythmia Detection from Electrocardiograms" (arXiv)
- **Problem:** Which explanation methods, and which display formats, are actually useful to clinicians? And do the explanations agree with medical knowledge?
- **Dataset:** MIT-BIH, plus a 12-lead dataset (Zheng et al.) merged using SNOMED codes (p.3).
- **Method:**
  - Pan-Tompkins segmentation into **0.6-s** beats (p.4).
  - Classes with fewer than **2,000** samples were excluded, leaving 6 classes (p.4).
  - A 1D CNN. **The LSTM was removed because it interfered with the XAI methods** (CSV; LSTM discussion p.4–5).
  - **Four SHAP variants** were compared: Permutation, Kernel, Gradient and DeepSHAP (p.5–6).
  - A survey of **5 clinical stakeholders** compared saliency maps with counterfactuals (p.5).
- **Split:** 80/20 of beat samples (p.4). Patient separation not described.
- **Results:**
  - MIT-BIH validation accuracy **98.30%** (p.5); macro F1 **0.93**; but APB precision only **0.52** (F1 **0.67**) (p.6).
  - Adding the 12-lead dataset drops validation accuracy to **73.45%** (p.5).
  - **All 5 clinicians preferred saliency maps** over counterfactuals (p.5).
  - Gradient and Deep explainers gave smoother, more interpretable maps than Permutation and Kernel.
- **Limitation (the key ones for us, p.8–10):**
  - Explanations for **APB and PVC did not consistently match clinical understanding**.
  - Explanations **varied across samples of the same class**.
  - Beat-level models lack inter-beat context.
  - The links between XAI and medical knowledge were **not validated by trained professionals**.
- **Relation to our project:** **This is the strongest single motivation for our objective 2.** It shows that "we applied SHAP" is not enough. Consistency within a class and clinical agreement must be *measured*. It also warns that adding an LSTM can make some XAI methods harder to apply, which we must plan for (e.g. use Grad-CAM on the CNN layers, or gradient-based SHAP).

### c. Comparison table

| Ref | Model | XAI | Classes | Split | Result | How the explanation was checked |
|---|---|---|---|---|---|---|
| [1] Alamatsaz | CNN-LSTM, 0.16 MB | SHAP | 9 rhythms | 85/15 segments (p.3–4) | Acc 98.24%, Se 86.1% (p.5) | Visual match to textbook criteria (p.6, p.8) |
| [4] Talukder | 1D CNN + ROS | SHAP, LIME, FIA | Binary | Not described | MITDB 99.74% (p.11) | Sample-index importance only (p.17–18) |
| [6] Asha | Proposed GAN → distilled CNN | SHAP (planned) | AAMI 5 / PTB-XL 5 | DS1/DS2 planned (p.3) | **None (projected, p.5)** | None |
| [7] Kavitha | Cycle-GAN + CNN | SHAP on features | AAMI 5 | **DS1/DS2** (p.4) | 99.87% claimed vs Table 7 recalls ≤ 99.2% (p.6) | Feature ranking (p.7, p.11) |
| [2] Beck | 1D CNN (LSTM removed) | 4 SHAP variants; saliency vs counterfactual | 6 beat types | 80/20 beats (p.4) | Val acc 98.30%; APB precision 0.52 (p.5–6) | **5-clinician survey; consistency examined** (p.5, p.8–10) |

### d. Agreement, disagreement, and what is missing
- **Agree:**
  - SHAP is the default XAI choice (all five).
  - When explanations are shown, they tend to highlight QRS and RR features ([1] p.6; [7] p.7).
- **Disagree:**
  - [1] and [7] present explanations as matching clinical criteria.
  - [2] finds that, for APB and PVC, they **do not consistently** match, and that they vary within a class (p.8–10).
  - The difference is method. [1] and [7] show selected examples. [2] looks across samples and asks clinicians.
- **Missing (this is our Gap 1 in detail):**
  - No paper measures **faithfulness**, for example with a deletion test (Stage 1 §1.11).
  - Only [2] looks at **consistency within a class**, and only qualitatively.
  - **No paper combines XAI with a verified inter-patient split *and* trustworthy numbers.** [7] uses DS1/DS2, but its results are internally inconsistent.
  - None checks whether explanations stay the same when **noise** is added.

### e. New terms introduced in this batch
- **SHAP variants** (all estimate Shapley values from Stage 1 §1.11, in different ways):
  - **Permutation / Kernel SHAP:** model-agnostic. They switch features on and off and fit the contributions. Slow, and can be noisy on long signals.
  - **Gradient SHAP:** averages gradients along paths from baseline inputs to the real input. Fast, smooth maps.
  - **DeepSHAP:** propagates contributions backwards through the layers, using DeepLIFT rules.
- **Saliency map:** any per-sample importance map over the input signal, such as Grad-CAM or gradient-based SHAP. "Where did the model look?"
- **Counterfactual explanation:** "what is the smallest change to this ECG that would change the prediction?" ([2] compares this with saliency maps; [29] in Batch 8 uses it).
- **LIME / FIA:** LIME is covered in Stage 1 §1.11. **Feature Importance Analysis** is a global ranking of input features by how much they affect the model.
- **Knowledge distillation:** train a small "student" network to copy the soft output probabilities of a large "teacher".
  - **Temperature T** softens the probabilities: p_i = exp(z_i/T) / Σ exp(z_j/T).
  - *Example:* logits [2, 0] give [0.88, 0.12] at T = 1, and [0.73, 0.27] at T = 2. The student learns more from the softer version.
- **GAN (Generative Adversarial Network):** two networks compete. A generator makes fake beats, and a discriminator tries to tell fake from real. Used here to create synthetic minority-class beats.
  - **Cycle-consistent GAN:** two generators that translate A → B → A, and must return to the original.
- **ROS / ADASYN:** ROS (random oversampling) duplicates minority samples. ADASYN is a SMOTE variant that creates more synthetic samples near the hard boundary regions.
- **Metaheuristic optimisation:** a search strategy inspired by nature or art, used here to tune hyperparameters instead of grid or random search.
- **Accuracy as a weighted average of recalls:** Acc = Σ_c (n_c / N) × recall_c. So accuracy is always between the smallest and largest per-class recall. This is a quick sanity check you can apply to any paper.

### f. Examiner questions with model answers
1. **"Many papers already use SHAP for ECG. What is new about your explainability?"**
   *Answer:* Most papers show example SHAP maps and say they agree with clinical criteria. Beck & John found that explanations for APB and PVC did not consistently match clinical understanding and varied within the same class. Kulkarni reports that fewer than 10% of studies validate explanation maps against clinical structures. We will *measure* explanations: faithfulness with a deletion test, consistency within each class, and overlap with annotated P/QRS/T regions, all on an inter-patient split.
2. **"Kavitha et al. report 99.87% with DS1/DS2 and SHAP. Hasn't your project already been done?"**
   *Answer:* Their own class-wise table reports a maximum per-class recall of 99.2%, and overall accuracy is a weighted average of per-class recalls, so 99.87% is arithmetically impossible with those numbers. Their F1 for minority classes is 77.6–88.3%. They also do not quantify explanation quality. So the combination of honest inter-patient results with validated explanations is still open.
3. **"Beck & John removed the LSTM because it hampered XAI. Your model has an LSTM. How will you explain it?"**
   *Answer:* Grad-CAM can be applied to the last convolutional layer before the LSTM. That gives a time map of which waveform regions the CNN features came from. Gradient-based SHAP works through the whole network, including the LSTM, because it only needs gradients. We will compare the two maps, which is also a consistency check. If they disagree badly, we will report that honestly as a limitation.

---

## Batch 6: Patient-independent evaluation

### a. What question this batch tries to answer
*"When test patients are truly unseen (Stage 1 §1.9), how much does performance fall, and what methods help a model generalise to new people?"*

### b. Paper by paper

#### [13] Jeong et al., 2024: "Enhancing Inter-Patient Performance for Arrhythmia Classification with Adversarial Learning Using Beat-Score Maps" (*Applied Sciences*)
- **Problem:** Beat shapes carry a "patient signature". Can we train features that *cannot* identify the patient, so that they generalise to new patients?
- **Dataset:**
  - MIT-BIH, MLII lead.
  - Chapman-Shaoxing (**SPH**), lead II, resampled to **360** Hz (p.7–8).
- **Method:**
  1. DWT denoising; **2.4-s** segments converted to CWT **scalograms**, which are time-frequency images (p.4–5).
  2. An **SE-ResNet** beat classifier is trained **adversarially**. A second head tries to identify the patient, and the main network is penalised when it succeeds: loss = λ1 · beat loss − λ2 · patient loss (p.5).
  3. The beat scores across a 10-s signal are stacked into a 2D **beat-score map**. A second SE-ResNet classifies the *rhythm* from this map.
- **Split:** **Inter-patient by record**. Unusually, it trains on **DS2** and tests on **DS1** (p.9). SPH uses 5-fold CV with different patients in each fold.
- **Task:** On MIT-BIH, reduced to **binary AFib vs normal** rhythm (p.9).
- **Results:**
  - MIT-BIH overall F1 **85.7%** vs **75.0%** baseline (p.11).
  - **AFib F1 77.9%** vs **61.0%** (p.11).
  - SPH cross-database: average F1 **87.36%** vs **83.22%** baseline, with λ2 = **0.075** (p.12).
- **Limitation:** Room for improvement across databases; binary task on MIT-BIH; some SPH rhythms merged or removed (p.9, p.11–12, p.15).
- **Relation to our project:** It shows *why* inter-patient testing is hard (patient-specific features) and offers one cure (adversarial invariance). It is a rhythm-level task, so its numbers are not comparable with AAMI beat F1. No XAI.

#### [14] Hassoon et al., 2026: "Dual-branch bidirectional attention fusion of temporal and hierarchical representations for robust ECG arrhythmia classification" (*Expert Systems with Applications*)
- **Problem:** Fuse a temporal branch and a shape-hierarchy branch adaptively, and handle imbalance without synthetic data.
- **Dataset:** MIT-BIH (MLII, AAMI 5). Transfer targets: PTB, INCART and SVDB, all resampled to **360** Hz (p.8–9).
- **Method:**
  - **Branch 1:** multi-scale CNN (kernels 3/5/7) + SE + 2-layer BiLSTM.
  - **Branch 2:** **Capsule Network** with dynamic routing + multi-head self-attention.
  - **Adaptive bidirectional attention fusion** with gating.
  - **EAMCL loss** with class-frequency-dependent margins (no oversampling).
- **XAI:** Branch contribution weights only: **0.710** BiLSTM vs **0.290** CapsNet (p.16).
- **Split:** **Inter-patient by subject**: **80%** of subjects for training and **20%** for testing (p.8). This is not DS1/DS2.
- **Results:**
  - Accuracy / F1 **99.55 ± 0.06%** (p.1, p.9–10).
  - Per-class F1: N **99.81**, S **95.37**, V **98.62**, F **90.06**, Q **99.84** (p.10).
  - Fine-tuned transfer: INCART **99.33%**, SVDB **98.04%**, PTB **98.86%** (p.10–11).
  - Model size **3.78 M** parameters, **15.61 MB** (p.16).
  - **Noise:** under AWGN, F1 drops to **32.46%** at 5 dB and **25.46%** at 0 dB (p.17).
- **Limitation:** Robustness at low SNR is limited; only AWGN was tested; no denoising front-end; heavy model (p.17–18).
- **Relation to our project:**
  - Its S F1 of 95.37% is far above the inter-patient averages in [10] (F1 79.48%, p.16). The likely reason is the random 80/20 *subject* split rather than DS1/DS2. With only 47 subjects, which patients land in the test set changes the result a lot. **My interpretation.**
  - Its **dramatic collapse under noise** is our best evidence for objective 3.

#### [16] Qin et al., 2026: "ECG beat classification based on dilated multi-scale ResNet and BiLSTM" (*Measurement Science and Technology*)
- **Problem:** Build a compact multi-scale model and test it on unseen patients *and* an unseen database without fine-tuning.
- **Dataset:**
  - MIT-BIH, MLII, AAMI N, S, V and F.
  - External: **INCART** lead II, **175,868** mapped beats (p.18).
- **Method:**
  - Median filter + **db5 wavelet** denoising (SNR **14.73 dB**, p.13).
  - Beats of **99** samples before and **160** after the R peak (p.13).
  - ResNet18 with three parallel **dilated** convolutions + BiLSTM.
  - **SMOTE on the training set only, after splitting**.
- **Split:** **Inter-patient by record**: **28** train / 9 validation / 11 test records (p.8, p.10). External INCART testing used no fine-tuning.
- **Results:**
  - Test accuracy **99.39%** (p.14).
  - Per-class F1: N **99.72**, S **91.73**, V **96.70**, **F 20.69**, with only **4** F beats in the test set (p.14).
  - INCART accuracy **98.75%**, recall S **96.05%**, F **85.96%** (p.18).
  - Model size **27.8 M** parameters (p.16).
- **Limitation:** Only two datasets; F results unreliable because there are only 4 F test beats (p.14); no nested CV (p.19).
- **Relation to our project:** A good model of **honest reporting**. It warns about the 4-beat F class and tests on INCART without fine-tuning, both of which we should copy. It also shows how a *random* record split can leave almost no F beats in the test set.

#### [15] Ibrahim, 2026: "A hybrid deep learning algorithm for ECG-based heart disease classification" (*Scientific Reports*)
- **Problem:** Measure directly how much beat-wise evaluation inflates results, using the same model under both protocols.
- **Dataset:** MIT-BIH, all **48** records, AAMI 5 classes. Paced beats are mapped to Q.
- **Method:**
  - Pan-Tompkins R-peaks, **187**-sample beats, Savitzky-Golay denoising (p.10).
  - A 1D-CNN (64 then 128 filters) followed by a BiLSTM (**64** units).
  - **Conditional GAN** augmentation of the training split only.
  - **Focal loss** (p.3) with class weights.
- **Split:** **Both**:
  - Beat-wise: 70/30 random.
  - Patient-wise: **34** training / **14** test records (p.13).
- **Results:**

  | | Beat-wise | Patient-wise |
  |---|---|---|
  | Accuracy | **99.00%** (p.14) | **91.69%** (CI 91.41–91.99) (p.1, p.15) |
  | Macro F1 | 0.92 ± 0.08 (p.14) | **0.547 ± 0.374** (p.1, p.15) |
  | S recall | | **0.209** (from 0.092) (p.16–17) |
  | V recall | | **0.809** (p.16–17) |
  | F recall | | **0.021** (p.16–17) |

  - The GAN improvement is statistically significant: McNemar χ² = **12.41**, p = **0.0004** (p.1).
  - The authors say the model works mainly as a **Normal-beat detector**, with a Fusion miss rate of **97.9%** (p.25).
- **Limitation:**
  - A record-level split is not exactly a patient-level split; only a single split; no external validation (p.25–26).
  - The CSV reviewer notes two different record assignments (p.13 vs p.15), and that paced records are included, so this is **not the standard DS1/DS2**.
- **Relation to our project:** **This is the single best within-paper demonstration of Gap 2:** a 7.31-point accuracy gap (p.1), and macro-F1 almost halved. It also shows that **a statistically significant gain can still be clinically useless.** S recall rising from 0.092 to 0.209 is "significant" but still misses about 4 in 5 S beats.

### c. Comparison table

| Ref | Split | Task | Headline | Minority-class reality | External test |
|---|---|---|---|---|---|
| [13] Jeong | DS2 train → DS1 test (p.9) | AFib vs normal rhythm | AFib F1 77.9% vs 61.0% (p.11) | AFib hardest | SPH cross-db F1 87.36% (p.12) |
| [14] Hassoon | 80/20 by subject (p.8) | AAMI 5 beats | F1 99.55% (p.10) | F F1 90.06% (p.10) | Fine-tuned INCART 99.33% (p.10) |
| [16] Qin | 28/9/11 records (p.8) | AAMI N, S, V, F | Acc 99.39% (p.14) | **F F1 20.69%, 4 test beats** (p.14) | INCART, no fine-tuning, 98.75% (p.18) |
| [15] Ibrahim | Beat-wise vs 34/14 records (p.13) | AAMI 5 | 99.00% → 91.69% (p.1) | **F recall 0.021, S 0.209** (p.16–17) | None |

### d. Agreement, disagreement, and what is missing
- **Agree:**
  - Patient-independent testing is harder.
  - **F and S are where it shows** ([15] p.16–17; [16] p.14).
- **Disagree:**
  - [14] reports near-perfect inter-patient F1 (99.55%), while [15] reports macro-F1 of 0.547.
  - Both are "patient-wise", but they use **different subject splits**, and neither uses DS1/DS2.
  - **Lesson:** "inter-patient" is not one single protocol. You must name the exact record lists. That is why we will use the standard **DS1/DS2** lists, so our result is comparable.
- **Missing:**
  - **None of the four reports XAI** beyond [14]'s branch weights. This is Gap 2: explainability is not combined with patient-independent evaluation.
  - Only [14] tests noise, and only with AWGN.

### e. New terms introduced in this batch
- **Adversarial learning (for invariance):** train a main network together with an "adversary" that tries to recover unwanted information, here the patient's identity. The main network is rewarded for *fooling* the adversary, so its features stop encoding who the patient is. λ2 sets how hard it tries ([13] uses 0.075, p.12).
- **Scalogram (CWT):** a time-frequency image produced by the continuous wavelet transform. Similar to the S-transform in Batch 4.
- **Beat-score map:** a grid of the per-beat class probabilities over a time window, used as the input for rhythm classification ([13]).
- **Capsule network:** neurons grouped into vectors ("capsules") whose length means "this part is present" and whose direction encodes its pose or properties. **Dynamic routing** decides which higher-level capsule each lower capsule sends its output to.
- **Margin-based loss:** forces the correct class score to beat the others by at least a margin m. EAMCL makes m bigger for rare classes, so they get pushed further away ([14]).
- **AWGN and SNR:**
  - AWGN (additive white Gaussian noise) is random noise of equal strength at all frequencies.
  - SNR (signal-to-noise ratio, in dB) = 10 · log10(P_signal / P_noise).
  - *Example:* signal power 1 and noise power 0.316 give 10 · log10(3.16) = **5 dB**. At 0 dB, signal and noise are equally strong.
- **Fine-tuning vs linear probe vs no fine-tuning:**
  - Fine-tuning re-trains the network on the new dataset.
  - A linear probe freezes the network and only trains the last layer.
  - **No fine-tuning** (as in [16]) is the strictest test of generalisation.
- **Confidence interval (CI):** a range likely to contain the true value. *Example:* 91.69%, CI 91.41–91.99, from bootstrapping ([15]).
- **Bootstrap:** resample the test set with replacement many times (e.g. 10,000), recompute the metric each time, and take the middle 95% of results as the CI.
- **McNemar's test:** compares two classifiers on the *same* test samples by counting where only A is right (b) and where only B is right (c).

  χ² = (|b − c| − 1)² / (b + c)

  *Example:* b = 30, c = 10 gives (20 − 1)² / 40 = 9.03, which is significant at p < 0.01.
- **Statistical vs clinical significance:** a difference can be real (statistically significant) but too small to matter clinically. *Example:* [15]'s S recall of 0.209 is a significant improvement but still misses 79% of S beats.

### f. Examiner questions with model answers
1. **"Why use DS1/DS2 rather than your own random patient split?"**
   *Answer:* "Inter-patient" results vary hugely depending on which patients land in the test set. Hassoon's 80/20 subject split gives 99.55% F1, while Ibrahim's record split gives macro-F1 of 0.547. DS1/DS2 is the de Chazal standard, used by 82% of inter-patient studies in Xiao's review. It makes our numbers comparable, and it keeps all classes represented in both sets, unlike Qin's random split, which left only 4 F beats in the test set.
2. **"What happens to minority classes under inter-patient testing?"**
   *Answer:* They collapse. In Ibrahim's paper, S recall is 0.209 and F recall 0.021 patient-wise, compared with 74% and 73% beat-wise. So per-class reporting is essential, and we treat improvement on S and F as the real test of our model.
3. **"Hassoon et al. report 99.55% under an inter-patient split. Why is that not the state of the art you should beat?"**
   *Answer:* Their split is a random 80/20 of subjects, not DS1/DS2, so it is not directly comparable. Their model also drops to 32.46% F1 at 5 dB of white noise, so high clean accuracy does not mean it is usable in practice. We compare on the standard split, and we report robustness and explanation quality alongside accuracy.

---

## Batch 7: Robustness (noise, denoising and uncertainty)

### a. What question this batch tries to answer
*"Real ECGs are noisy (Stage 1 §1.4). How do papers remove noise, how do they test whether a classifier survives noise, and can a model tell us when it is unsure?"*

### b. Paper by paper

#### [32] Mallikarjunamallu & Khasim, 2024: "Arrhythmia Classification Using Noise Filtering and 1D CNN" (*Traitement du Signal*)
- **Problem:** Does adding noise and then filtering it before a 1D-CNN improve robustness?
- **Dataset:** MIT-BIH, modified lead II. **27,789** beats: N **8,965**, S 2,779, V 7,236, F 803, Q 8,006 (p.4, p.7).
- **Method:**
  1. Add "Gaussian noise".
  2. Apply a notch filter around 50/60 Hz.
  3. Classify with a 1D-CNN (input **187 × 1**, p.7).
- **Split:** Not stated.
- **Results:**
  - Accuracy **99%** (p.9).
  - Per-class F1: N **0.99**, S **0.86**, V **0.96**, F **0.80**, Q **0.99** (p.9).
  - Specificity: N **0.706**, Q **0.408** (p.9).
- **Limitation:** Clinical validation still needed (p.10).
- **Serious method problems** (CSV reviewer, which I checked in the PDF):
  - The "Gaussian noise" algorithm actually adds a **50 Hz sine wave**: `noise = a·sin(2π·50·t)` (p.5). That is powerline interference, not Gaussian noise.
  - The N count (8,965) is far below MIT-BIH's total.
  - A specificity of 0.408 for Q is inconsistent with 99% accuracy.
- **Relation to our project:** A good example of *mislabelled* robustness testing. If you add exactly the noise your filter removes, you have tested nothing. We will use **real NSTDB noise** instead.

#### [31] Pashikanti et al., 2022: "Adaptive Predictive Control-Based Noise Cancellation With Deep Learning for Arrhythmia Classification from ECG Signals" (IEEE ICIIET)
- **Problem:** Use adaptive filtering to cancel noise, then classify with handcrafted features and a deep network.
- **Dataset:** MIT-BIH combined with the MIT-BIH Normal Sinus Rhythm database. The task is normal vs arrhythmia (p.5).
- **Method:**
  - An **adaptive LMS filter** for noise cancellation.
  - Features: wavelet-based wave detection (P, Q, R, S, T), intervals (PP, PR, RR, QT), statistics, and Empirical Mode Decomposition.
  - Classifier: a **Deep Maxout Network**. Implemented in MATLAB.
- **Split:** Varying training percentages from 50% to 90%, and K-fold. Patient separation not described.
- **Results:**
  - At **90%** training data: accuracy **92.1%**, sensitivity **92.6%**, specificity **91.9%** (p.1, p.8).
  - Comparators at the same setting: CNN+LSTM **0.887**, DRN+LSTM **0.872** (p.6–7).
- **Limitation:** Not stated beyond testing on other datasets (p.8). The CSV reviewer notes a specificity mismatch (0.926 in the text vs 0.919 in the table, p.6–7).
- **Relation to our project:** Introduces **adaptive filtering**. Its explicit interval features (PR, RR, QT) are naturally interpretable. That is a reminder that handcrafted features can be a fair comparison point for "explainable".

#### [35] Maurya et al., 2025: "A proposed deep learning model for multichannel ECG noise reduction" (*Discover Artificial Intelligence*)
- **Problem:** Remove baseline wander, muscle artifact and electrode-motion noise with a deep denoising autoencoder.
- **Dataset:**
  - Clean signals: the **PhysioNet QT Database**.
  - Noise: **NSTDB** baseline wander (BW), muscle artifact (MA) and electrode motion (EM) (p.7).
  - **72,002** training and **13,316** test windows of **512** points (p.7).
- **Method:**
  - A **fully convolutional denoising autoencoder**: dilated conv encoder, transposed-conv decoder, skip connections.
  - Loss = MSE + λ · **Jacobian regularisation** (p.5–9).
- **Split:** 72,002 / 13,316 samples (p.7). Patient separation not described.
- **Results:**
  - Abstract: SSD **4.763** × 10⁻² mV², MAD **0.288** mV, RMSE **1.859** (p.1).
  - Best with Jacobian (Table 3): SSD **4.03**, RMSE **1.112** (p.11).
  - The DRNN baseline is worse: SSD **11.486–12.630** (p.11).
  - SNR improves by **9.5–10.6 dB** vs **6.3–7.4 dB** for DRNN (p.13). Example: record sel0357 goes from **5.2 → 15.8 dB**.
- **Limitation:** Jacobian regularisation is computationally heavy, and **the denoised signals have not been tested for diagnosis or classification** (p.13–14).
- **CSV reviewer notes:** The abstract's SSD and MAD values match the "without Jacobian" row rather than the proposed model. RMSE is given as 0.1112 in the text vs 1.112 in Table 3.
- **Relation to our project:**
  - It shows how to **use NSTDB properly**: clean ECG + real noise at known levels.
  - It also shows the gap: nobody checked whether denoising *helps the classifier* or *keeps the explanation the same*.

#### [33] Zhang et al., 2024: "Cardiac arrhythmia classification with rejection of ECG recordings based on uncertainty estimation from deep neural networks" (*Neural Computing and Applications*)
- **Problem:** Can the model say "I don't know" and hand doubtful cases to a doctor?
- **Dataset:** CPSC 2018 training set: **6,877** 12-lead recordings at 500 Hz from 11 hospitals, 9 classes (p.2).
- **Method:**
  - A **61-layer** 1D CNN with residual bottleneck blocks and SE (p.2).
  - **Monte Carlo dropout**: dropout is kept *on* at test time and each input is run **50** times (p.3).
  - From the spread of predictions, it computes **data (aleatoric)** and **model (epistemic)** uncertainty.
  - A prediction is **rejected** if its uncertainty is above a threshold.
- **Split:** **80/10/10 by subjects** (p.4).
- **Results:**
  - Macro F1 without rejection: **0.6635** (p.5).
  - At threshold **0.400**, only **45.28%** of predictions are accepted, and macro F1 on them rises to **0.8688** (+**0.2053**) (p.5).
  - False-positive rate on accepted predictions: **2.3%** vs **23.3%** without rejection (p.3, p.7).
  - **Cardiologists traced high data uncertainty mainly to noise** (large interference, baseline drift) (p.7–9).
- **Limitation:** Only works for models with dropout; multiple passes at inference raise the cost; it is unclear how to set thresholds (p.10).
- **Relation to our project:** **This is the uncertainty component of our objective 3.** MC dropout is easy to add to our CNN-LSTM. It links directly to noise, and it gives clinicians a "please review" flag.

#### [34] Ashhad et al., 2025: "Uncertainty-Aware Multi-view Arrhythmia Classification from ECG" (arXiv; states it was published at IJCNN 2024)
- **Problem:** Combine two "views" of a beat (the raw time series and a 2D image) so that, when noise corrupts one view, the model trusts the other.
- **Dataset:**
  - MIT-BIH, lead II, AAMI 5.
  - INCART, lead II, **3** classes.
  - **NSTDB** BW, MA and EM noise for testing (p.3, p.5).
- **Method:**
  - A **BiLSTM** on the raw beat.
  - A **Vision Transformer** on a **Gramian Angular Field** image of the beat (p.3).
  - The two softmax outputs are fused with **Dempster-Shafer theory**, which measures how much the views *conflict* and down-weights uncertain evidence (p.3).
- **Split:** **80-20 split, then SMOTE on the training split only** (p.3). Patient separation not described.
- **Results:**
  - MIT-BIH accuracy **98.8%**, recall **93.4%** (p.3–4).
  - INCART accuracy **99.5%** (p.3–4).
  - Single views: BiLSTM **98.6%**, ViT **98.5%** (MIT-BIH, p.4).
  - **More robust than score-level and feature-level fusion** under AWGN and NSTDB noise from 15 to 0 dB (p.4–5).
- **Limitation:** No limitations section. INCART had too few F and Q beats; negative SNRs were not tested (p.4–5).
- **Relation to our project:** The only paper using **real NSTDB noise on a classifier** at graded SNRs (0–15 dB), so it gives a template for our robustness test. **No XAI**, so how explanations change under noise is still open.

### c. Comparison table

| Ref | What it contributes | Noise type tested | Classifier tested on noisy data? | Split | XAI |
|---|---|---|---|---|---|
| [32] Mallikarjunamallu | Notch + 1D-CNN | "Gaussian", actually a **50 Hz sine** (p.5) | Yes, but trivially | Not stated | No |
| [31] Pashikanti | Adaptive LMS + Maxout | Not specified | Yes (acc 92.1%, p.1) | Not described | No (interval features are interpretable) |
| [35] Maurya | Denoising autoencoder | **NSTDB BW/MA/EM** (p.7) | **No** (p.13) | 72,002/13,316 windows | No |
| [33] Zhang | MC-dropout rejection | Real CPSC noise (found by cardiologists, p.7–9) | Yes; F1 0.6635 → 0.8688 with rejection (p.5) | **By subject** (p.4) | No (uncertainty, case studies) |
| [34] Ashhad | Uncertainty-aware fusion | **AWGN + NSTDB 15–0 dB** (p.4–5) | Yes | 80-20 beats (p.3) | No |

### d. Agreement, disagreement, and what is missing
- **Agree:**
  - Noise is a main cause of errors and uncertainty ([33] p.7–9).
  - Uncertainty-aware methods help ([33], [34]).
- **Disagree on how to deal with noise:**
  - **Remove it first** ([31], [32], [35]).
  - **Let the model judge its own reliability** ([33] rejects, [34] down-weights the noisy view).
  - These are complementary, not exclusive.
- **Missing (this is Gap 3):**
  - No paper here measures **explanation stability under noise**.
  - [35] does not test classification on denoised signals.
  - [32]'s robustness test is not a real noise test.
  - Only [34] uses graded real noise on a classifier, and without XAI.

### e. New terms introduced in this batch
- **NSTDB (MIT-BIH Noise Stress Test Database):** real recordings of three noise types: **BW** (baseline wander), **MA** (muscle artifact) and **EM** (electrode motion). They are added to clean ECGs at chosen SNRs to stress-test algorithms.
- **Adding noise at a target SNR (worked example):**
  - The clean beat has power P_s = 0.5 mV². For a 6 dB SNR, P_n = P_s / 10^(6/10) = 0.5 / 3.98 = 0.126 mV².
  - If the raw noise segment has power 0.5, scale it by √(0.126/0.5) = **0.50** before adding.
- **Adaptive LMS filter:** a filter whose weights update every sample to minimise error: w ← w + μ · e · x. μ is a small step size, e is the error and x is the input.
  - *Example:* w = 0.5, μ = 0.1, e = 0.2, x = 1 gives w = 0.52.
- **Autoencoder / denoising autoencoder:** a network that squeezes the input into a small code (encoder) and rebuilds it (decoder). A *denoising* one is trained to output the **clean** signal when given the **noisy** one.
- **Transposed convolution:** the "reverse" of a strided convolution. It makes a signal longer (upsampling) in the decoder.
- **Jacobian regularisation:** penalises how sharply the output changes when the input changes slightly, which is the size of the Jacobian matrix of derivatives. A smaller Jacobian means smaller output changes for small input noise ([35]).
- **SSD / MAD / RMSE:**
  - SSD (sum of squared differences) = Σ(clean − denoised)².
  - MAD (maximum absolute difference) = max |clean − denoised|.
  - RMSE = √(mean squared error).
  - *Example:* clean [1, 2], denoised [1.1, 1.8] gives SSD = 0.01 + 0.04 = **0.05**, MAD = **0.2**, RMSE = √(0.025) = **0.158**.
- **Aleatoric vs epistemic uncertainty:**
  - **Aleatoric (data) uncertainty:** noise or ambiguity in the input itself. More training will not remove it.
  - **Epistemic (model) uncertainty:** the model has not seen enough similar data. More data reduces it.
- **Monte Carlo dropout:** keep dropout active at test time and run the same input T times. The spread of the outputs estimates uncertainty.
  - *Example:* five runs give p(V) = [0.9, 0.85, 0.2, 0.88, 0.3]. The mean is 0.63, with a wide spread, so the model is uncertain and the beat should be flagged.
- **Predictive entropy:** H = −Σ p_c · ln p_c over the averaged probabilities.
  - *Example:* p = [0.5, 0.5] gives H = **0.693** (maximally unsure for 2 classes).
  - p = [0.99, 0.01] gives H = 0.01·4.6 + 0.99·0.01 ≈ **0.056** (confident).
- **Classification with rejection:** refuse to predict when uncertainty is above a threshold, and pass the case to a human. Trade-off: fewer predictions, but more accurate ones ([33]).
- **Gramian Angular Field (GAF):** turns a 1D signal into a 2D image. Each value is rescaled to [−1, 1] and turned into an angle φ = arccos(x). Pixel (i, j) = cos(φ_i + φ_j).
- **Dempster-Shafer theory:** a way to combine evidence from several sources that also tracks **conflict** between them. Strongly conflicting sources lead to lower trust in the combined result.

### f. Examiner questions with model answers
1. **"How will you test robustness, and why not just add Gaussian noise?"**
   *Answer:* Gaussian (white) noise is not what real ECGs suffer from. Real contamination is baseline wander, muscle artifact and electrode motion. NSTDB provides real recordings of all three. We will add them to the DS2 test beats at graded SNRs, for example 24, 18, 12, 6 and 0 dB, and report per-class F1 at each level. Hassoon et al. show that even a strong model can drop to 32% F1 at 5 dB of white noise, and Mallikarjunamallu's "Gaussian" noise turned out to be a 50 Hz sine wave, which shows how easily robustness tests can be misleading.
2. **"What does explanation stability under noise mean, and why does it matter?"**
   *Answer:* If adding a small amount of realistic noise changes the Grad-CAM or SHAP map completely while the prediction stays the same, the explanation cannot be trusted. A clinician would see different reasons for the same diagnosis. We will measure the similarity between clean and noisy explanation maps (for example correlation or top-k overlap) as the SNR falls. None of the papers we reviewed measures this.
3. **"How can your model say it is unsure?"**
   *Answer:* With Monte Carlo dropout, as in Zhang et al. We keep dropout on at test time, run each beat several times, and compute predictive entropy. Beats above a threshold are flagged for review. Zhang et al. raised macro-F1 from 0.6635 to 0.8688 on accepted predictions, and cardiologists traced most high-uncertainty cases to noise. That links our uncertainty component to our noise experiments.

---

## Batch 8: 12-lead data, PTB-XL, and clinically checked explanations

### a. What question this batch tries to answer
*"How does the picture change on 12-lead, record-level, multi-label data such as PTB-XL? And what does it look like when explanations are compared with clinical knowledge rather than just displayed?"*

### b. Paper by paper

#### [27] Smigiel et al., 2021: "ECG Signal Classification Using Deep Learning Techniques Based on the PTB-XL Dataset" (*Entropy*)
- **Problem:** Compare a very light CNN, a SincNet, and a CNN with entropy features on PTB-XL at three difficulty levels.
- **Dataset:** PTB-XL at **100 Hz** (p.3–4). **17,232** records after filtering (p.4). Tasks: 2 classes (NORM vs abnormal), 5 superclasses, and 20 subclasses.
- **Method:**
  1. A light 1D CNN with **8,882** weights for the binary task (p.6).
  2. **SincNet**, with **6,109,922** parameters (p.11).
  3. A CNN plus per-lead **entropy features**, with about **58,178** parameters (p.11).
- **Split:** **70/15/15** of records (p.1, p.4). Patient separation not described. **Note:** the paper does not use PTB-XL's patient-respecting folds, and PTB-XL has more records than patients (Stage 1 §1.8), so the same patient could appear on both sides.
- **Results** (p.11):

  | Model | Task | Accuracy | F1 | AUC |
  |---|---|---|---|---|
  | CNN + entropy | 2 classes | **0.892** | 0.891 | 0.96 |
  | CNN + entropy | 5 classes | **0.765** | **0.68** | |
  | CNN + entropy | 20 classes | **0.698** | **0.332** | |
  | Plain CNN | 2 classes | 0.882 | | 0.953 |

- **Limitation:** Overfitting; only 100 Hz used; SincNet not adapted to ECG (p.17–18). The CSV reviewer notes the text says the network "was trained on the test dataset" (p.6), and the 2-class accuracy is given as both 89.82% and 89.2% (p.10).
- **Relation to our project:** Shows how **performance collapses as the label space grows**: F1 goes from 0.891 to 0.68 to 0.332. PTB-XL is much harder than MIT-BIH beat classification.

#### [30] Mehdi & Drigh, 2026: "ECG Classification on PTB-XL: A Data-Centric Approach with Simplified CNN-VAE" (arXiv)
- **Problem:** Can careful data handling plus a small model compete with big models on PTB-XL?
- **Dataset:** PTB-XL, 12 leads, 100 Hz, 5 superclasses, multi-label.
- **Method:**
  - 3 Conv1D blocks, global average pooling, a VAE-style 32-dimensional latent, and 5 sigmoid outputs.
  - **197,093** parameters (p.1, p.3).
  - Balancing: HYP oversampled and NORM downsampled to **4,000** each (p.2), plus extra weight for HYP.
- **Split:** PTB-XL **strat_fold**: folds 1–9 for training and fold 10 for testing (p.2). These folds are patient-respecting by design (Stage 1 §1.8), although the paper does not discuss patient separation.
- **Results:**
  - Binary accuracy **87.01%** (p.1); weighted F1 **0.745**; AUC **0.8958** (p.3).
  - Per-class F1: NORM **0.849**, STTC **0.735**, CD **0.713**, MI **0.703**, HYP **0.537** (p.3).
  - **HYP recall 50.2%**, with **131 of 263** HYP cases missed (p.3–4).
  - Model size **769.89 KB** (p.3). Compared with ResNet-50 at **82.3%** (p.2, p.5).
- **Limitation:** PTB-XL only; no cross-validation; latent space not interpreted; weak HYP (p.5–6). The CSV reviewer notes the validation set comes from the already-oversampled training set.
- **Relation to our project:** A **small model with careful data handling** beats a large one. That supports a "data-centric" story for our baseline.

#### [28] Anand et al., 2022: "Explainable AI decision model for ECG data of cardiac disorders" (*BSPC*)
- **Problem:** Find a compact 12-lead model that beats larger ones, and show that its SHAP explanations match clinical ECG criteria.
- **Dataset:**
  - PTB-XL, 100 Hz, 5 superclasses, multi-label.
  - Chapman-Shaoxing: **10,646** patients, 4 rhythm classes (p.4).
- **Method:**
  - **ST-CNN-GAP-5**: 5 *temporal* conv layers (along time), plus 1 *spatial* layer (across the 12 leads), skip connections and global average pooling.
  - It has **165,061** parameters, reduced from **8,078,309** (p.5).
  - Benchmarked against ResNet-18/34/50/101, Attention-56 and SENet.
- **XAI:** **SHAP Gradient Explainer** (p.8). The top 500 SHAP values are highlighted on each lead.
- **Split:** **Inter-patient**, using PTB-XL's folds. "One subject's data occurs in only one of these folds". Folds 1–9 are used for training and validation (88/12), and **fold 10** for testing (p.4).
- **Results:**
  - PTB-XL macro AUC **93.41%**, vs prior state of the art **93.00%** (p.7, p.10).
  - Accuracy **89.73%**; micro F1 **79.28%** (p.7).
  - Chapman macro F1 **95.79%** at 100 Hz (p.10).
  - SHAP highlights clinically recognised features (p.10–14):
    - a slurred S wave for RBBB (p.10–11);
    - prominent Q waves for MI;
    - **Sokolow-Lyon** voltage criteria for LVH (p.14).
- **Limitation:** No explicit limitations section. Generalisation is acknowledged as a challenge (p.4, p.10).
- **On "clinical validation":** In the text I could extract, the explanations are *compared against established clinical criteria* by the authors. One co-author is from a medical college's Pharmacology department (p.1). I did **not** find a described protocol in which cardiologists rated the explanations. See the Stage 4 contradiction check.
- **Relation to our project:** **The best model in our set for "explanation matched to named clinical criteria".** It also shows that **small models with GAP can outperform large ResNets**, and that GAP layers make CAM/Grad-CAM natural.

#### [3] Kolliyil & Brindise, 2025: "Automated detection of arrhythmias using a novel interpretable feature set extracted from 12-lead electrocardiogram" (*Computers in Biology and Medicine*)
- **Problem:** Can interpretable handcrafted features with XGBoost match deep learning, and generalise better?
- **Dataset:**
  - Development: CPSC 2018, **6,877** records, of which **6,400** single-label records were used (p.6).
  - External test: CPSC-extra, PTB-XL and Georgia G12EC, **1,072** records (p.7).
  - 9 classes.
- **Method:**
  - **654** features of 60 types: rhythm, morphology, time-frequency, and others (p.1, p.5).
  - SHAP-based selection down to **159** features (p.1, p.8).
  - Classifier: **XGBoost**.
- **XAI:** SHAP, for both feature selection and per-class explanations.
- **Split:** Stratified 10-fold CV by record on CPSC, plus independent external datasets.
- **Results:**
  - CV macro F1 **77%** (p.8).
  - External macro F1 **0.65**, vs **0.16** for the Chen et al. CNN and **0.63** for the Lai et al. model (p.10).
  - SHAP top features match clinical criteria: **PR interval for 1st-degree AV block**, and HRV/RR volatility for AF (p.6, p.11).
- **Limitation:** Features are limited for PVC, ST depression and ST elevation; about 16% lower performance on external data; depends on accurate wave detection (CSV, p.9–10, p.12–13).
- **Relation to our project:** A strong **"interpretable by design" comparison point**. On external data, the deep CNN it compares against collapsed (macro F1 0.16) while the feature model held up (0.65). A useful sentence for the viva: explainability and generalisation can go together.

#### [29] Jang et al., 2025: "A novel XAI framework for explainable AI-ECG using generative counterfactual XAI (GCX)" (*Scientific Reports*)
- **Problem:** Saliency maps show *where* a model looks, but not *what change* would alter its decision. Can generated counterfactual ECGs show that?
- **Dataset:**
  - PTB-XL: **21,799** ECGs from **18,869** patients, including **1,514** AF (p.3–4).
  - MIMIC-IV ECG: **238,262** ECGs from **104,804** patients, with potassium levels (p.3–4).
- **Method:**
  - A **StyleGAN2** generator creates ECGs that push a trained model's output up (positive counterfactual) or down (negative counterfactual) (p.3).
  - ECG features are then measured, and paired t-tests check what changed.
  - Applied to eight ResNet models, including AF classification and potassium regression.
  - Compared with saliency maps.
- **Split:** Not stated in the main text; model details are in the supplementary material (p.3).
- **Results:**
  - No classification accuracy is reported. The study evaluates *explanations*.
  - For AF, positive counterfactuals show **P-wave absence and irregular rhythm**.
  - For hyperkalaemia: taller T waves, a longer PR interval, and QRS widening.
  - The listed changes were statistically significant (p < 0.05).
  - Saliency maps only highlighted the T wave or P wave, while GCX captured **rhythm irregularity**, which saliency maps miss (CSV findings).
- **Limitation:** Counterfactuals may be physiologically implausible; a proprietary feature extractor limits reproducibility (p.8).
- **Relation to our project:** It shows a limit of Grad-CAM and SHAP: they cannot express *timing irregularity* well. That matters for S beats and AF. Counterfactuals are a possible future-work extension.

### c. Comparison table

| Ref | Dataset | Split | Model | XAI | Result | Explanation checked against clinical criteria? |
|---|---|---|---|---|---|---|
| [27] Smigiel | PTB-XL (17,232) | 70/15/15 random (p.4) | Light CNN / SincNet / CNN + entropy | Not stated | 5-class F1 0.68 (p.11) | No |
| [30] Mehdi | PTB-XL | Folds 1–9 / 10 (p.2) | CNN-VAE, 197,093 params | Not stated | Bin. acc 87.01%, HYP F1 0.537 (p.1, p.3) | No |
| [28] Anand | PTB-XL; Chapman | **Patient-separated folds** (p.4) | ST-CNN-GAP-5, 165,061 params | SHAP (Gradient) | Macro AUC 93.41% (p.7) | **Yes**, mapped to named criteria (p.10–14) |
| [3] Kolliyil | CPSC 2018 → external incl. PTB-XL | 10-fold CV + external | Features + XGBoost | SHAP | External macro F1 0.65 vs 0.16 CNN (p.10) | **Yes**, e.g. PR interval for AV block (p.6, p.11) |
| [29] Jang | PTB-XL; MIMIC-IV | Not stated (supplement) | ResNets | Counterfactual (GCX) vs saliency | Changes significant, p < 0.05 | **Yes**, AF → absent P, irregular RR |

### d. Agreement, disagreement, and what is missing
- **Agree:**
  - 12-lead, record-level classification is harder, especially fine-grained classes ([27] 20-class F1 0.332, p.11; [30] HYP F1 0.537, p.3).
  - **Explanations become convincing when they are expressed in clinical terms**: named waves, intervals and voltage criteria ([28], [3], [29]).
- **Disagree:**
  - **Deep models vs feature models:** [28] says a small deep CNN is best, while [3] shows deep CNNs can collapse on external data (0.16) where features hold up (0.65, p.10).
  - **Saliency vs counterfactuals:** [29] argues saliency misses rhythm information. Beck [2] (Batch 5) found clinicians *preferred* saliency maps. So which explanation is "better" depends on who is asking and for what.
- **Missing:**
  - None of these checks how explanations behave under **noise** or across **patients**.
  - None reports a formal **faithfulness** metric.

### e. New terms introduced in this batch
- **Multi-label classification:** one record can have several labels at once, for example MI *and* conduction disturbance. Each class gets its own **sigmoid** output (probability between 0 and 1), not a shared softmax.
- **Binary accuracy / Hamming loss / subset accuracy** (multi-label metrics). For a record with true labels [1, 0, 1, 0, 0] and predictions [1, 0, 0, 0, 0]:
  - **Hamming loss** = 1/5 = **0.2** (fraction of label slots wrong).
  - **Binary accuracy** = 4/5 = **0.8** (fraction right).
  - **Subset accuracy** = **0**, because not all labels are exactly right.
- **Micro vs macro F1:** macro averages the per-class F1 scores, so each class counts equally. Micro pools all TP, FP and FN first, so big classes dominate.
- **Macro AUC:** the AUC computed per class, then averaged. It is the standard PTB-XL benchmark metric ([28]).
- **Spatial vs temporal convolution:** temporal convolution slides along time within a lead. Spatial convolution mixes across the 12 leads at the same moment ([28]).
- **Global Average Pooling (GAP):** average each feature map over time to give one number per channel. It cuts parameters (165,061 vs 8,078,309 in [28], p.5) and enables CAM.
- **Entropy features:** numbers describing how irregular or unpredictable a signal is (e.g. Shannon, sample or permutation entropy). Higher entropy means more irregular.
- **SincNet:** a CNN whose first-layer filters are constrained to band-pass shapes, with only two learnable cut-off frequencies each. It was designed for speech ([27]).
- **VAE (variational autoencoder):** an autoencoder whose code is a probability distribution (a mean and a variance) rather than one point.
- **XGBoost (gradient-boosted trees):** builds many small decision trees, each one correcting the previous trees' errors. Strong on tabular features, and works naturally with SHAP.
- **StyleGAN2:** a high-quality GAN architecture, originally for faces, used in [29] to generate realistic ECGs.
- **Counterfactual ECG:** a generated ECG that is minimally different from the original but changes the model's output. The difference *is* the explanation.
- **Sokolow-Lyon criterion:** a clinical voltage rule for left ventricular hypertrophy. S in V1 + R in V5 or V6 ≥ 35 mm (3.5 mV) **(verify the exact threshold in a clinical text)**.

### f. Examiner questions with model answers
1. **"Why is your main dataset MIT-BIH rather than PTB-XL?"**
   *Answer:* Our task is beat-level arrhythmia classification under the AAMI standard. MIT-BIH is beat-annotated and has the standard DS1/DS2 inter-patient split. PTB-XL is record-level and multi-label, with diagnostic superclasses like MI and HYP rather than beat classes, so it suits a different task. We plan to use PTB-XL, or INCART for beat-level work, as an external test. Its patient-respecting folds, used by Anand et al., are the right protocol for that.
2. **"What would a clinically meaningful explanation look like for your model?"**
   *Answer:* It would point to the waveform regions a cardiologist uses. For example: a wide QRS with no preceding P wave for a V beat; an early beat with an abnormal P wave or short pre-RR for an S beat. Anand et al. show SHAP highlighting a slurred S wave for RBBB and Sokolow-Lyon voltage for LVH. Kolliyil et al. show the PR interval driving the AV-block decision. We will measure how much of the attribution falls inside the annotated P, QRS and T windows for each class.
3. **"Deep learning or handcrafted features: which generalises better?"**
   *Answer:* In Kolliyil et al., on external datasets, the interpretable XGBoost feature model kept macro-F1 0.65 while a published CNN fell to 0.16. On the other hand, Anand's compact deep model reached 93.41% macro AUC on PTB-XL under patient-separated folds. Our position is to use a compact deep model but feed it RR-interval features and judge it on external or inter-patient data. Its explanations are then compared with the same clinical features that interpretable models use.

---

# STAGE 4: Synthesis

## 4.1 One table across all 37 papers

Split codes:
- **IP** = inter-patient / patient-separated.
- **BL** = beat- or segment-level random split, or a split whose patient separation is not described.
- **—** = not applicable (review).

| Ref | Paper | Model | Dataset(s) | Split | XAI | Key result (page) |
|---|---|---|---|---|---|---|
| [8] | Ebrahimi 2020 | Review (75 studies) | Many | — | Not stated | CNN for features in 52% (p.9) |
| [9] | Ansari 2023 | Review (78 studies, accuracy ≥ 96% filter) | Many | — | Not stated | Accuracies 96.00–99.80% (p.13) |
| [10] | Xiao 2023 | Review (368 studies) | Many | — | Not stated | F1 95.52 → 83.89% intra → inter (p.16) |
| [11] | Silva 2025 | Review (122 studies) | Many | — | Not stated | 30.3% inter-patient; 4.1% meet E3C (p.11) |
| [12] | Kulkarni 2026 | Review + meta-analysis (119 studies) | Many | — | Not stated | External validation 18.5%, −8.7% accuracy (p.50); < 10% validate maps (p.40) |
| [17] | Ahmed 2023 | 1D-CNN | MIT-BIH (4 classes) | BL (p.6) | Not stated | Acc 0.99, macro F1 0.93 (p.11) |
| [25] | Pramkeaw 2026 | CNN-LSTM vs ANN/CNN/RNN/LSTM | MIT-BIH (5) | IP, 33/7/8 records (p.6) | Not stated | CNN-LSTM 98.5 ± 0.5% (p.7) |
| [26] | Wang 2026 | CNN → LSTM + attention | MIT-BIH (5) | BL (p.9) | Not stated | Acc 99.20%, Se 94.07% (p.13) |
| [24] | Reddy 2025 | Multi-scale CNN + dense + BiLSTM | MIT-BIH (N, V, A, R, L) | BL / unclear | Not stated | 5-fold acc 98.22% (p.21) |
| [37] | Akan 2024 (ECGformer) | Encoder-only Transformer | MIT-BIH Kaggle (5) | BL (p.3) | Not stated | Acc 0.98, macro F1 0.86 (p.4) |
| [18] | El-Ghaish 2024 | Multi-scale CNN + bidirectional Transformer | MIT-BIH Kaggle (5); PTB | BL (p.6) | Not stated | Macro F1 94.26% (p.7) |
| [20] | Ikram 2025 | Transformer on PCA features | MIT-BIH (Kaggle) | BL / not stated | Not stated | Acc 97%; 43.8% of F beats → N (p.11) |
| [23] | Liu 2025 | CNN + BERT | MIT-BIH (5; 9) | BL (p.6) | Not stated | 9-class acc 99.12% (p.9); V F1 84.47% (p.8) |
| [36] | Huang 2026 | Multi-scale CNN + channel attention + Transformer | MIT-BIH (5); INCART (2) | BL, 65/15/20 (p.3) | Not stated | Macro F1 93.97% (p.7) |
| [21] | Kim 2025 | S-transform + ResNeXt + Transformer | MIT-BIH (5); Icentia11k | Not stated | CAM (p.8) | Acc 99.58% / 97.80% (p.7) |
| [5] | Tenepalli 2025 | Beat image + EfficientNetB0 + Transformer | MIT-BIH (PVC vs non-PVC) | BL, 80/20 (p.6) | Grad-CAM, attention | Acc ~99%, AUC 0.997 (p.1, p.10) |
| [22] | Lee 2025 | Graph CNN on P/QRS/T nodes | Private (328 patients) | IP, 5-fold (p.6) | Not stated | Macro F1 88.61% (p.8) |
| [19] | Chen 2025 | Multi-scale Transformer + TCN + LLM prompts | PTB-XL; SPH | Not stated (~80/10/10, p.6) | Grad-CAM (p.11) | Super AUC 91.30, F1 77.56 (p.7) |
| [1] | Alamatsaz 2024 | Lightweight CNN-LSTM | MIT-BIH + LTAF (9 rhythms) | BL, 85/15 (p.3–4) | SHAP | Acc 98.24%, 0.16 MB (p.5) |
| [4] | Talukder 2025 | 1D CNN + ROS | MITDB, PTBDB, NSTDB (binary) | Not described | SHAP, LIME, FIA | MITDB 99.74% (p.11) |
| [6] | Asha 2026 | Proposed GAN → distilled CNN | Planned MIT-BIH, PTB-XL | IP planned (p.3) | SHAP (planned) | **No results; projected** (p.5) |
| [7] | Kavitha 2026 | Cycle-GAN + CNN | MIT-BIH, SVDB, PTB-XL, + external | IP DS1/DS2 (p.4) | SHAP | 99.87% claimed; Table 7 recalls ≤ 99.2% (p.6) |
| [2] | Beck 2025 | 1D CNN (LSTM removed) | MIT-BIH; 12-lead | BL, 80/20 (p.4) | 4 SHAP variants; saliency vs counterfactual | Val 98.30%, combined 73.45% (p.5) |
| [13] | Jeong 2024 | Adversarial SE-ResNet + beat-score maps | MIT-BIH; SPH | IP, DS2 → DS1 (p.9) | Not stated | AFib F1 61.0 → 77.9% (p.11) |
| [14] | Hassoon 2026 | Dual-branch CNN-BiLSTM + CapsNet | MIT-BIH; PTB, INCART, SVDB | IP, 80/20 subjects (p.8) | Branch weights | F1 99.55%; 32.46% at 5 dB AWGN (p.10, p.17) |
| [16] | Qin 2026 | Dilated multi-scale ResNet + BiLSTM | MIT-BIH; INCART | IP, 28/9/11 records (p.8) | Not stated | Acc 99.39%; F F1 20.69% on 4 beats (p.14) |
| [15] | Ibrahim 2026 | CNN-BiLSTM + cGAN | MIT-BIH | Both; IP 34/14 (p.13) | Not stated | 99.00% → 91.69%; F recall 0.021 (p.1, p.16–17) |
| [32] | Mallikarjunamallu 2024 | Notch + 1D-CNN | MIT-BIH (5) | Not stated | Not stated | Acc 99%; "Gaussian" noise is a 50 Hz sine (p.5, p.9) |
| [31] | Pashikanti 2022 | Adaptive LMS + Deep Maxout Network | MIT-BIH + NSR | Not described | Not stated | Acc 92.1% (p.1) |
| [35] | Maurya 2025 | Denoising autoencoder + Jacobian regularisation | QT DB + NSTDB | Not described | Not stated | SNR gain 9.5–10.6 dB (p.13) |
| [33] | Zhang 2024 | 61-layer CNN + MC dropout | CPSC 2018 | IP by subjects (p.4) | Uncertainty (not XAI) | Macro F1 0.6635 → 0.8688 with rejection (p.5) |
| [34] | Ashhad 2025 | BiLSTM + ViT (GAF), Dempster-Shafer fusion | MIT-BIH; INCART; NSTDB | BL, 80-20 (p.3) | Not stated | Acc 98.8%; robust 15–0 dB (p.3–5) |
| [27] | Smigiel 2021 | Light CNN / SincNet / entropy CNN | PTB-XL | BL, 70/15/15 (p.4) | Not stated | 5-class F1 0.68 (p.11) |
| [30] | Mehdi 2026 | CNN-VAE (197,093 params) | PTB-XL | Folds 1–9 / 10 (p.2) | Not stated | Binary acc 87.01%; HYP F1 0.537 (p.1, p.3) |
| [28] | Anand 2022 | ST-CNN-GAP-5 (165,061 params) | PTB-XL; Chapman | IP folds (p.4) | SHAP (Gradient) | Macro AUC 93.41% (p.7) |
| [3] | Kolliyil 2025 | Handcrafted features + XGBoost | CPSC 2018 → CPSC-extra, PTB-XL, G12EC | Record 10-fold + external | SHAP | External macro F1 0.65 vs 0.16 CNN (p.10) |
| [29] | Jang 2025 | ResNets + StyleGAN2 counterfactuals | PTB-XL; MIMIC-IV | Not stated (supplement) | Counterfactual (GCX) vs saliency | Changes significant at p < 0.05 |

**Counts from this table (my tally):**
- **XAI:** 12 of the 32 non-review papers report some explanation or visualisation method: [1], [2], [3], [4], [5], [7], [14], [19], [21], [28], [29], plus [6], which is planned only.
- **Inter-patient or patient-separated splits:** 10 papers: [7], [13], [14], [15], [16], [22], [25], [28], [33], plus [30] by using the folds.
- **Both XAI and a patient-separated split:** only **[7]** (whose numbers are internally inconsistent), **[28]** (PTB-XL, record-level) and **[14]** (branch weights only).

## 4.2 Research gaps, each traced to papers

**Gap 1: Explanations are shown, but rarely measured.**
- Fewer than 10% of studies validated explanation maps against clinical structures ([12] p.40).
- Explanations are typically shown as examples: [1] p.6, p.8; [5] p.8–9; [21] p.8; [19] p.11.
- Or as raw sample indices: [4] p.17–18.
- Beck & John found explanations for APB and PVC inconsistent with clinical understanding and variable within a class, not validated by trained professionals ([2] p.8–10).
- The strongest clinical mapping comes from [28] (p.10–14), [3] (p.6, p.11) and [29], but none reports a **faithfulness** test or a **within-class consistency** score.

**Gap 2: Explainability is rarely combined with a trustworthy patient-independent evaluation on beat-level data.**
- XAI papers without patient separation: [1] (p.3–4), [2] (p.4), [4], [5] (p.6), [21].
- Patient-independent papers without XAI: [13], [15], [16], [25].
- The exceptions are weak:
  - [7] uses DS1/DS2 + SHAP, but its accuracy (99.87%) is impossible given its own per-class recalls (≤ 99.2%, p.6).
  - [28] uses patient-separated folds + SHAP, but on PTB-XL record-level superclasses, not AAMI beats.
- The size of the inflation: F1 95.52 → 83.89% ([10] p.16); 99.00 → 91.69% ([15] p.1).

**Gap 3: Robustness to realistic noise is narrowly tested, and never linked to explanations.**
- AWGN only: [14] (F1 32.46% at 5 dB, p.17).
- Gaussian only: [24] (p.11–12).
- A mislabelled sine wave: [32] (p.5).
- No noise test at all: [5] (p.13), [36] (p.11).
- Denoising without any downstream classification check: [35] (p.13).
- Only [34] uses graded real NSTDB noise on a classifier (p.4–5), and it has no XAI.
- Noise is the main source of predictive uncertainty ([33] p.7–9).
- **No paper of the 37 measures explanation stability under noise.**

**Gap 4: Minority classes and external generalisation remain weak.**
- Patient-wise S and F recall of 0.209 and 0.021 ([15] p.16–17).
- F F1 of 20.69% on 4 test beats ([16] p.14).
- S/F the hardest classes in [18] (p.9), [25] (p.7), [32] (p.9), [36] (p.11) and [37] (p.4).
- External validation in only 18.5% of studies, with −8.7% accuracy and −13.2% F1 ([12] p.50).
- External collapse of a deep CNN to macro F1 0.16 ([3] p.10).
- Adding a second dataset dropped [2] from 98.30% to 73.45% (p.5).

## 4.3 Our objectives and the gaps they answer

These are taken from `literature_review.md` §4, with refinements suggested by Stage 3 in *italics*.

| Objective | What we do | Gaps answered | Evidence that it is needed |
|---|---|---|---|
| **O1: Patient-independent baseline** | A hybrid CNN-(Bi)LSTM with RR features, trained on DS1 and tested on DS2. Report per-class Se, +P and F1, plus macro-F1, accuracy, size and latency. *External test on INCART (beat-level, AAMI-mappable) without fine-tuning.* | 2, 4 | [10] p.16; [11] p.11, p.25; [15] p.1; [16] p.18; [12] p.50 |
| **O2: Validated explanations** | Grad-CAM + Gradient SHAP on the O1 model. Measure: (a) **faithfulness** (deletion test); (b) **within-class consistency** (similarity of maps across beats of the same class); (c) **clinical plausibility** (share of attribution inside P, QRS and RR/timing regions, per class). *Add a small clinician rating if one can be arranged.* | 1, 2 | [2] p.8–10; [12] p.40; [28] p.10–14; [3] p.6, p.11 |
| **O3: Robustness of predictions and explanations** | Add NSTDB BW/MA/EM noise to DS2 at graded SNRs. Track per-class F1, **explanation stability** (clean vs noisy map similarity), and **MC-dropout uncertainty**, with flagging of uncertain beats. | 3, 4 | [14] p.17; [32] p.5; [34] p.4–5; [35] p.13; [33] p.5, p.7–9 |

## 4.4 Proposed framework: block diagram with justification

```
          +--------------------------------------------------------------+
          |  DATA                                                        |
          |  MIT-BIH (44 non-paced records) -> DS1 (train) / DS2 (test)  |
          |  INCART (external test)       NSTDB noise (bw, ma, em)       |
          +-------------------------------+------------------------------+
                                          |
                                          v
 [B1] Preprocessing: band-pass (~0.5-40 Hz) / baseline removal, 360 Hz
                                          |
                                          v
 [B2] R-peak detection (Pan-Tompkins); compare against annotation positions
                                          |
                                          v
 [B3] Beat segmentation: fixed window around R  +  RR features
      (pre-RR, post-RR, local average RR) ; per-beat z-score
                                          |
                                          v
 [B4] Model: 1D-CNN (multi-scale kernels) -> BiLSTM -> dense -> softmax(N,S,V,F)
      loss = class-weighted cross-entropy (or focal); dropout layers kept
                                          |
            +-----------------------------+-----------------------------+
            v                             v                             v
 [B5] Evaluation            [B6] Explanation module         [B7] Uncertainty
   per-class Se/+P/F1,        Grad-CAM (last conv layer)      MC dropout (T passes)
   macro-F1, confusion        Gradient SHAP (whole net)       predictive entropy
   matrix, size, latency      -> maps over time aligned       -> flag "review"
   DS2 + INCART               with P / QRS / T                    |
            |                             |                       |
            +-----------------------------+-----------------------+
                                          v
 [B8] Explanation & robustness evaluation
      faithfulness (deletion) | within-class consistency | clinical-region overlap
      repeat on DS2 + NSTDB noise at SNR = 24, 18, 12, 6, 0 dB
      -> F1(SNR), explanation-stability(SNR), uncertainty(SNR)
```

| Block | Why it is there | Supporting evidence |
|---|---|---|
| Data: DS1/DS2 | Standard, comparable inter-patient protocol; keeps every class in both sets | [10] p.14–15 (82% of IP studies); [11] p.7; contrast [16] p.14 (4 F beats) and [14] vs [15] |
| Data: INCART | External test without fine-tuning | [16] p.18; [12] p.50; [9] p.15–17 |
| Data: NSTDB | Real noise types, not synthetic AWGN | [34] p.4–5; [35] p.7; problems in [14] p.17 and [32] p.5 |
| B1 Preprocessing | Remove baseline wander and powerline noise before R-peak detection | Stage 1 §1.5; [21] p.6 (detrending was the most impactful step) |
| B2 Pan-Tompkins + comparison with annotations | A real deployment has no expert R-peak file. We report how much detection errors matter | Stage 1 §1.5 honesty point; [25], [15] use Pan-Tompkins |
| B3 RR features | S beats are defined by timing; single-beat windows lose it | [22] p.4, p.8 (S F1 73.59 → 81.00% with distance features); [2] p.8–10 (no inter-beat context) |
| B4 CNN → BiLSTM | Shape + timing; efficient size band | [25] p.7 (CNN-LSTM > CNN); [12] p.47 (0.5–1.5 M parameter balance); [24], [14] multi-scale kernels |
| B4 Class-weighted / focal loss | Imbalance; avoids leakage from oversampling before the split | [24] p.4 (all-N collapse without balancing); [18] p.8; [15] p.3 |
| B5 Per-class metrics | Accuracy hides minority failure | [37] p.4; [10] p.16; [11] p.25 reporting guideline |
| B6 Grad-CAM + Gradient SHAP | Two methods, so their agreement can be checked. Gradient SHAP works through the LSTM, while Grad-CAM uses the CNN layers | [2] p.5–6 (Gradient/Deep SHAP smoother; LSTM issue); [5], [19] (Grad-CAM on ECG) |
| B7 MC dropout | Flags doubtful beats; noise drives uncertainty | [33] p.5, p.7–9 |
| B8 Explanation metrics under noise | The open gap: nobody measures faithfulness, consistency or stability | Gap 1 and Gap 3 evidence above |

## 4.5 Check against `literature_review.md`: contradictions and corrections

| # | Where in `literature_review.md` | What it says | What the PDFs show | Suggested fix |
|---|---|---|---|---|
| 1 | Header and Gap 3 | "36 papers" | The CSV now has **37** rows. ECGformer was added as row 37 (see the progress log) | Change to 37, or remove row 37 if you prefer to exclude ECGformer |
| 2 | Gap 1 | "Only a few papers had clinicians or cardiologists check the highlighted waveforms [28], [29]" | In the extracted text, **[28]** compares SHAP with clinical criteria itself; one co-author is from a medical college's Pharmacology department (p.1). **No clinician rating protocol is described.** **[29]** validates its counterfactuals with feature statistics and paired t-tests, not clinician review. The only clinician involvement in the set is [2] (5 "clinical stakeholders" stating a *preference*, p.5) and [33] (cardiologist case studies of *uncertainty*, not explanations) | Reword: "A few papers compare explanations against named clinical criteria [3], [28], [29], but none reports a structured clinician evaluation of explanation correctness" |
| 3 | §1.2 | "SHAP is … used in [1], [2], [3], [4], [6], [7] and [28]" | [6] is a **conceptual paper with no results**. Its SHAP is only planned (p.5) | Mark [6] as "proposed" |
| 4 | §1.2 | "survey of 5 clinicians" ([2]) | The PDF says "five **clinical stakeholders**" (p.5) | Use the paper's wording |
| 5 | Gap 2 | "Explainability is seldom combined with patient-independent evaluation" (no counter-examples given) | **[7]** combines SHAP with MIT-BIH DS1/DS2 (p.4), and **[28]** combines SHAP with patient-separated PTB-XL folds (p.4) | Acknowledge [7] and [28], and sharpen the gap: [7]'s numbers are internally inconsistent (99.87% vs per-class recall ≤ 99.2%, p.6), and [28] is record-level PTB-XL, not AAMI beats |
| 6 | §2 table, row [28] | "Inter-patient (PTB-XL folds)"; "No explicit limitations section" | Confirmed (p.4) | No change |
| 7 | §1.1 | "a 0.16 MB CNN-LSTM ran at 5.127 ms per rhythm on a Raspberry Pi [1]" | Confirmed (p.5) | No change |
| 8 | §1.3 | "Kolliyil and Brindise [3] saw about 16% lower performance on external data" | Confirmed: "16% lower than that observed during cross-validation" (p.10) | No change |
| 9 | §1.3 | "Dual-branch fusion reached 99.55% on a subject-level split [14]" | Confirmed (p.10). Note it is an 80/20 *random* subject split, not DS1/DS2 (p.8) | Add "(random 80/20 subject split)" |
| 10 | Objective 1 | "external testing on a second database" | Not named | Name **INCART** (beat-level, used for external testing by [16] p.18 and [36] p.9) |

**No numeric contradictions were found** between `literature_review.md` and the PDFs. Every number I checked appears on the cited page or in the CSV page references. The issues above are about wording, framing and paper count. I have **not** edited `literature_review.md`; tell me if you want these fixes applied.

---

# STAGE 5: What we do next

> Library calls below come from general knowledge and are marked **(verify)**. Check each against the library's documentation when you first run it.

## 5.1 Step-by-step build plan for the baseline

| Step | What to do | Why |
|---|---|---|
| **0. Environment** | Python 3.10+, `numpy`, `scipy`, `wfdb`, `torch`, `scikit-learn`, `matplotlib`, `captum` (for Grad-CAM/SHAP). Fix the random seeds. Keep one config file holding every setting. | Reproducibility. Only about 6% of studies share code ([10] p.17), so ours should be rerunnable. |
| **1. Download data** | `wfdb.dl_database('mitdb', 'data/mitdb')`. Later also `'nstdb'` and `'incartdb'` **(verify database names on PhysioNet)**. | MIT-BIH for training and testing; NSTDB for noise; INCART for external testing (Stage 4 §4.4). |
| **2. Read records and labels** | `rec = wfdb.rdrecord('data/mitdb/100')` and `ann = wfdb.rdann('data/mitdb/100', 'atr')`. Use `ann.sample` (R positions) and `ann.symbol` (beat labels). Use channel 0 (MLII) **(verify which channel is MLII in each header)**. | The annotation file gives the expert beat label at each R peak. |
| **3. Map to AAMI** | `N: N L R e j`; `S: A a J S`; `V: V E`; `F: F`; `Q: / f Q`. Drop non-beat symbols. | Standard classes (Stage 1 §1.3; [11] p.25). |
| **4. Fix the split** | Exclude paced records 102, 104, 107 and 217. **DS1 → train**, **DS2 → test** (lists in Stage 1 §1.9, **verify against de Chazal 2004**). Inside DS1, hold out about 4 *whole records* for validation. | Inter-patient protocol, comparable with 82% of inter-patient studies ([10] p.14–15). The validation set must also be patient-separated, or model selection leaks. |
| **5. Filter** | `b, a = scipy.signal.butter(3, [0.5, 40], btype='band', fs=360)`, then `filtfilt(b, a, x)`. | Removes baseline wander and high-frequency noise (Stage 1 §1.5). `filtfilt` gives zero phase shift, so the R peaks don't move. |
| **6. R peaks** | **Baseline v1:** use the annotation R positions, and say so. **v2:** Pan-Tompkins. Count a detection as correct if it lands within ±150 ms of an annotation **(verify the EC57 tolerance)**. Report detection Se and +P. | v1 isolates classifier performance. v2 shows the real-world pipeline (Stage 1 §1.5 honesty point). |
| **7. Segment beats** | 90 samples before R + 162 after = **252** samples. Z-score each beat. | Covers P to T (Stage 1 §1.5). Z-scoring removes amplitude differences between patients. |
| **8. RR features** | For each beat: pre-RR, post-RR, local mean RR (e.g. last 10 beats), and pre-RR / local mean. | S beats are defined by prematurity ([22] p.4, p.8). |
| **9. Class counts table** | Count N/S/V/F/Q in DS1 and DS2. **Decide on Q:** most papers drop it after removing paced records. Our default is **4 classes (N, S, V, F)**; state this in the report. | Shows the imbalance up front (Stage 1 §1.10). Q is tiny once paced beats are removed **(verify the counts)**. |
| **10. Model v0 (CNN)** | Conv1d(1→32, k=7) → BN → ReLU → MaxPool(2) → Conv1d(32→64, k=5) → … → GAP. Concatenate the RR features → Dense → softmax. | The simplest baseline ([17]), so later gains can be measured against it. |
| **11. Model v1 (CNN-BiLSTM)** | Same convolutional front end, but feed the conv feature *sequence* into a BiLSTM (64 units), then concatenate RR → Dense → softmax. Aim for well under 1 M parameters. | Shape + timing ([25] p.7); efficient size ([12] p.42, p.47). |
| **12. Train** | Class-weighted cross-entropy, Adam (lr 1e-3), early stopping on **validation macro-F1** (not accuracy). No oversampling before the split. | Macro-F1 is what we care about (Stage 1 §1.10). Avoids the leakage seen in [21] and [24]. |
| **13. Evaluate on DS2** | Confusion matrix; per-class Se, +P and F1; macro-F1; accuracy; parameters; ms per beat. Add a 95% bootstrap CI ([15] p.15). | The [11] p.25 reporting guideline. Sanity check: accuracy must lie between the smallest and largest per-class recall (Batch 5 lesson). |
| **14. Grad-CAM** | Hook the last Conv1d. Compute the class-score gradient, average it over time to get α_k, form ReLU(Σ α_k A_k), upsample to 252 samples, and overlay on the beat. `captum.attr.LayerGradCam` **(verify)**. | First explanations (Stage 1 §1.11). Works with the CNN layers even though an LSTM follows ([2] p.8–10 warning). |
| **15. Gradient SHAP** | `captum.attr.GradientShap`, with baselines such as zeros and the mean training beat **(verify)**. | A second method, so the two can be compared ([2] p.5–6: gradient-based SHAP is smoother). |
| **16. First XAI checks** | (a) **Deletion test:** zero the top 10% Grad-CAM samples and measure the drop in p(class), compared with zeroing 10% random samples. (b) **Consistency:** mean pairwise correlation of maps within each class. (c) **Region overlap:** fraction of attribution in the P window (about 0.25–0.05 s before R) vs QRS (about ±0.05 s) vs T, per class **(verify the windows; better to delineate)**. | Turns "pretty pictures" into numbers (Gap 1). |

Minimal code shape for the AAMI mapping and beat extraction (sketch, not tested):

```python
AAMI = {**dict.fromkeys(list("NLRej"), "N"), **dict.fromkeys(list("aJAS"), "S"),
        **dict.fromkeys(list("VE"), "V"), "F": "F"}
PRE, POST = 90, 162
def beats(record_path):
    rec = wfdb.rdrecord(record_path); ann = wfdb.rdann(record_path, "atr")
    x = filtfilt(b, a, rec.p_signal[:, 0])           # MLII assumed in channel 0 (verify)
    r = ann.sample; out = []
    for i in range(1, len(r) - 1):
        lab = AAMI.get(ann.symbol[i])
        if lab is None or r[i] - PRE < 0 or r[i] + POST > len(x): continue
        seg = x[r[i] - PRE: r[i] + POST]; seg = (seg - seg.mean()) / (seg.std() + 1e-8)
        pre_rr, post_rr = (r[i] - r[i-1]) / 360, (r[i+1] - r[i]) / 360
        out.append((seg, [pre_rr, post_rr], lab))
    return out
```
*(The local-average RR is left out for brevity. Note that `i` runs over all annotations, so non-beat symbols such as rhythm markers should be filtered out of `r` first.)*

## 5.2 What we can honestly show at the mid-evaluation vs future work

| Can show (true today, or once Steps 0–14 are run) | Must be presented as future work (not yet done) |
|---|---|
| Problem statement and motivation (Stage 1) | Validated explanation metrics (faithfulness, consistency, region overlap) as *results* |
| Literature review of 37 papers, with the comparison table (Stage 4 §4.1) | Pan-Tompkins pipeline results (if still using annotation R peaks) |
| Four research gaps, each traced to specific papers (Stage 4 §4.2) | INCART external test |
| Three objectives and the framework diagram (Stage 4 §4.3–4.4) | NSTDB robustness curves and explanation stability under noise |
| Dataset protocol: DS1/DS2, AAMI mapping, class-count table | MC-dropout uncertainty and flagging |
| **If run before the evaluation:** baseline CNN (and ideally CNN-BiLSTM) results on DS2 with a confusion matrix and per-class F1 | Ablations, statistical tests, final model |
| **If run:** a few Grad-CAM overlays for N, S, V and F beats, labelled clearly as *qualitative, not yet validated* | Clinician feedback (only if arranged) |

**Rules for the evaluation:**
- Never present an intra-patient number as our result.
- If the baseline's S or F recall is low, show it. The literature shows this is the expected outcome under DS1/DS2 (e.g. [15] p.16–17), and showing it demonstrates you understand the problem.

## 5.3 Week-by-week plan to the final evaluation

> **Assumption:** I don't know your dates. This plan uses **Week 1 = the week starting 2026-10-05** and assumes about **14 weeks** to the final evaluation, with the mid-evaluation around the end of **Week 3**. Tell me the real dates and I will re-time it.

| Week | Goal | Deliverable |
|---|---|---|
| 1 | Environment; download MIT-BIH; AAMI mapping; DS1/DS2 beat extraction; class-count table | `data/` pipeline + counts table |
| 2 | Baseline CNN v0 trained on DS1, tested on DS2 | Confusion matrix, per-class Se/+P/F1 |
| 3 | CNN-BiLSTM v1 + RR features; first Grad-CAM overlays; **mid-evaluation slides** | Baseline comparison table; 4 example maps |
| 4 | Gradient SHAP; compare with Grad-CAM qualitatively | Side-by-side maps per class |
| 5 | XAI metric 1: deletion-based faithfulness | Faithfulness curves (target vs random deletion) |
| 6 | XAI metrics 2–3: within-class consistency; P/QRS/T region overlap (decide on delineation) | Per-class consistency and overlap table |
| 7 | Replace annotation R peaks with Pan-Tompkins; measure the impact | Detection Se/+P; classifier F1 with detected peaks |
| 8 | External test on INCART (resample to 360 Hz, AAMI mapping, no fine-tuning) | External per-class table |
| 9 | Download NSTDB; build a noise-injection function at target SNRs (24, 18, 12, 6, 0 dB) for bw/ma/em | F1-vs-SNR curves |
| 10 | Explanation stability under noise (map similarity between clean and noisy versions) | Stability-vs-SNR curves per class |
| 11 | MC-dropout uncertainty; entropy vs SNR; rejection curve | Uncertainty plots; accepted-only F1 |
| 12 | Ablations (no RR, no BiLSTM, no class weights); bootstrap CIs; McNemar tests | Ablation table with CIs |
| 13 | Write the report (using the UG template in `templates/`); final figures | Draft report |
| 14 | Slides, demo, viva rehearsal with Stage 5.4 questions | Final submission |

## 5.4 Fifteen likely viva questions, with short answers

1. **What is your project in one sentence?**
   A CNN-BiLSTM that classifies ECG beats into AAMI classes, evaluated on unseen patients (DS1/DS2), whose Grad-CAM and SHAP explanations are measured for faithfulness, consistency, clinical plausibility and stability under real noise.
2. **What is an arrhythmia, and what are the AAMI classes?**
   An abnormal heart rate, rhythm, origin or conduction. The AAMI classes are N (normal), S (supraventricular ectopic), V (ventricular ectopic), F (fusion) and Q (unknown or paced).
3. **Why MIT-BIH?**
   It is beat-annotated by cardiologists at 360 Hz and is the standard benchmark (61% of 368 studies, [10] p.2). It also has the standard DS1/DS2 inter-patient split.
4. **What is the inter-patient split, and why does it matter?**
   Test patients never appear in training. Under it, F1 drops from 95.52% to 83.89% ([10] p.16), so intra-patient results overstate real performance.
5. **Why not report accuracy only?**
   About 90% of beats are N. ECGformer reports 98% accuracy but misses 42% of S beats ([37] p.4). We report per-class Se, +P, F1 and macro-F1.
6. **Why a CNN-BiLSTM?**
   The CNN learns waveform shape and the BiLSTM learns temporal context. It beat a CNN alone in a head-to-head comparison ([25] p.7), and hybrids in the 0.5–1.5 M parameter range give a good balance of efficiency and accuracy ([12] p.47).
7. **Why add RR-interval features?**
   S beats are mostly defined by prematurity. Timing features raised S F1 from 73.59% to 81.00% in [22] (p.4, p.8).
8. **How do you handle class imbalance?**
   Class-weighted loss, applied only to the training data. Without balancing, models collapse to predicting N ([24] p.4).
9. **What does Grad-CAM compute?**
   It weights the last convolutional feature maps by the time-averaged gradient of the class score, sums them, and applies ReLU. The result is a heatmap over time showing which waveform regions supported the class.
10. **What does SHAP compute?**
    Shapley values: each input's average marginal contribution to the output over all orderings. The contributions add up exactly to the prediction minus a baseline.
11. **How do you know an explanation is correct?**
    Three checks:
    - **Faithfulness:** deleting the highlighted region should drop the prediction more than deleting random regions.
    - **Consistency:** maps should be similar within a class.
    - **Plausibility:** attribution should fall on clinically relevant regions, such as the QRS for V beats or the P wave and RR timing for S beats.
12. **What is new compared with existing XAI-ECG papers?**
    They mostly show example maps without patient-independent testing ([1], [2], [4], [5]). Fewer than 10% validate maps clinically ([12] p.40), and none measures explanation stability under noise. We combine DS1/DS2, quantitative XAI metrics and NSTDB noise.
13. **How do you test robustness?**
    Add real NSTDB baseline wander, muscle artifact and electrode-motion noise to DS2 at graded SNRs. Then track per-class F1, explanation stability and MC-dropout uncertainty. Only testing with white noise can mislead, as in [14] p.17 and [32] p.5.
14. **What are the main limitations?**
    - MIT-BIH has only 47 patients and old, two-lead recordings.
    - F beats are very rare.
    - Explanation "ground truth" is approximate.
    - Clinician validation may not be possible within the project.
    - Grad-CAM resolution is limited to the last convolutional layer.
15. **What would you do with more time?**
    - Evaluate externally on more datasets (PTB-XL record-level, wearable data).
    - Add a structured clinician rating of explanations.
    - Try counterfactual explanations for rhythm-level features ([29]).
    - Try patient-invariant training ([13]).
    - Compress the model for a wearable.
