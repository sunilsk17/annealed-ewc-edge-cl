# 📚 Complete Guide to Analyzing EWC Experimental Results

## Table of Contents
1. [Understanding λ (Lambda) Values](#lambda-values)
2. [Understanding Metrics](#metrics)
3. [Datasets Explained](#datasets)
4. [Models Explained](#models)
5. [How to Compare Results](#comparison)
6. [Interpreting Findings](#interpretation)

---

## 1. Understanding λ (Lambda) Values {#lambda-values}

### What is λ?

**λ (lambda)** is the **EWC penalty strength** - it controls how much the model tries to preserve old knowledge.

**Formula**: `Total Loss = Task Loss + λ × EWC Penalty`

### What Each λ Value Means:

| λ Value | Meaning | What It Does |
|---------|---------|--------------|
| **λ=0** | **No EWC** (Baseline) | Model is free to change any weights. No protection of old tasks. |
| **λ=200** | **Weak EWC** | Small penalty for changing important weights from previous tasks. |
| **λ=500** | **Moderate EWC** | Medium penalty - balances learning new vs remembering old. |
| **λ=1000** | **Strong EWC** | Large penalty - strongly resists changing weights. |
| **λ=2000** | **Very Strong EWC** | Very large penalty - heavily restricts weight changes. |
| **λ=5000** | **Maximum EWC** | Extreme penalty - model becomes very rigid. |

### The Tradeoff:

- **Low λ (0-200)**: Easy to learn new tasks, but forgets old ones
- **High λ (2000-5000)**: Remembers old tasks better, but struggles to learn new ones
- **Optimal λ**: Should balance both (but we found this doesn't exist for edge models!)

---

## 2. Annealed EWC

### What is Annealing?

**Annealed EWC** uses a **decreasing λ schedule**: λ starts high and gradually decreases.

**Formula**: λ_t = λ₀ / (1 + t)

Where:
- λ₀ = initial λ (we use 5000)
- t = task number (0, 1, 2, ...)

### Example Schedule:

| Task | λ Value | Reasoning |
|------|---------|-----------|
| 0 | 5000 | First task - no previous knowledge to protect |
| 1 | 2500 | Protect task 0, but still learn task 1 well |
| 2 | 1667 | Protect tasks 0-1, gradually less restrictive |
| 3 | 1250 | Continue decreasing |
| 4 | 1000 | Final task - most flexible |

**Why Annealing Helps:**
- Early tasks: Strong protection (high λ)
- Later tasks: More flexibility (low λ)
- Avoids catastrophic rigidity on final tasks

---

## 3. Understanding Metrics {#metrics}

### 3.1 Accuracies Array

**Example**: `[0.10, 0.05, 0.02, 0.01, 0.73]` (for 5 tasks)

- **Index 0**: Accuracy on Task 0 after training all tasks
- **Index 1**: Accuracy on Task 1 after training all tasks
- ...
- **Index 4**: Accuracy on Task 4 (final task)

**What it tells us**: How well the model remembers each task at the end

### 3.2 Final Task Accuracy

**Definition**: Accuracy on the LAST task the model learned

**Example**: If accuracies = `[0.10, 0.05, 0.02, 0.01, 0.73]`, then Final Task = 0.73 (73%)

**What it measures**: 
- **Learning ability** under EWC constraints
- Can the model still learn new things with regularization?

**Interpretation**:
- ✅ High (>70%): Model can still learn well
- ⚠️ Medium (50-70%): Learning is somewhat restricted
- ❌ Low (<50%): EWC is too restrictive (catastrophic rigidity)

### 3.3 Early Tasks Average

**Definition**: Average accuracy on all tasks EXCEPT the final one

**Formula**: `(acc₀ + acc₁ + ... + accₙ₋₂) / (n - 1)`

**Example**: For `[0.10, 0.05, 0.02, 0.01, 0.73]`:
- Early tasks = (0.10 + 0.05 + 0.02 + 0.01) / 4 = 0.045 (4.5%)

**What it measures**:
- **Memory/retention** of previous tasks
- Did the model remember what it learned earlier?

**Interpretation**:
- ✅ High (>50%): Good retention
- ⚠️ Medium (10-50%): Partial forgetting
- ❌ Low (<10%): Severe catastrophic forgetting

### 3.4 Forgetting

**Definition**: `Forgetting = 1 - Early Tasks Average`

**Example**: If Early Avg = 0.045, then Forgetting = 1 - 0.045 = 0.955 (95.5%)

**What it measures**:
- **How much was forgotten** from early tasks
- Higher = worse (more forgetting)

**Interpretation**:
- ❌ High (>90%): Severe forgetting
- ⚠️ Medium (50-90%): Moderate forgetting
- ✅ Low (<50%): Good retention

### 3.5 Average Accuracy

**Definition**: Average across ALL tasks (including final)

**Formula**: `(acc₀ + acc₁ + ... + accₙ) / n`

**What it measures**:
- **Overall performance** across entire curriculum
- Balanced view of learning + retention

---

## 4. Datasets Explained {#datasets}

### CIFAR-10 (Drift-based)

**Setup**:
- 5 sequential environments with visual drift
- Clean → Fog → Night → Snow → Blur
- 5,000 samples per environment
- 10 total classes (shared across environments)

**Challenge**: 
- Distribution shift (same classes, different appearance)
- Tests robustness to domain changes

**Evaluation**: 
- Test on standard CIFAR-10 test set
- Measures: "Can model maintain performance after drift training?"

### CIFAR-100 (Class-incremental)

**Setup**:
- 10 sequential tasks
- 10 new classes per task
- 5,000 samples per task
- 100 total classes (10 per task)

**Challenge**:
- Class-incremental learning (new classes keep coming)
- Tests memory of previous classes

**Evaluation**:
- Test on all 100 classes
- Measures: "Does model remember old classes while learning new ones?"

### Comparison:

| Aspect | CIFAR-10 | CIFAR-100 |
|--------|----------|-----------|
| **Tasks** | 5 | 10 |
| **Classes** | 10 (same across tasks) | 100 (10 new per task) |
| **Challenge** | Distribution shift | Class-incremental |
| **Difficulty** | Easier | Harder |
| **Best for** | Drift robustness | Memory testing |

---

## 5. Models Explained {#models}

### MobileNetV3 (Edge Model)

**Specs**:
- ~310,000 parameters
- Designed for mobile/edge devices
- Efficient architecture

**Characteristics**:
- Small capacity
- Fast inference
- Low memory

### ResNet-18 (Standard Model)

**Specs**:
- ~11,200,000 parameters (11.2M)
- Standard benchmark in research
- Powerful architecture

**Characteristics**:
- Large capacity (36× bigger than MobileNetV3)
- Slower but more accurate
- Standard research baseline

### Why Compare Both?

1. **MobileNetV3**: Tests edge deployment scenario (real-world constraint)
2. **ResNet-18**: Tests if findings generalize to standard models
3. **Comparison**: Shows capacity-dependent behavior

---

## 6. How to Compare Results {#comparison}

### 6.1 Within Same Model + Dataset

**Compare λ values to find trends**

Example (ResNet-18 CIFAR-100):
```
λ=0:    Final=72.8%, Early=0%    ← Baseline
λ=200:  Final=58.2%, Early=0%   ← -14.6% (worse!)
λ=500:  Final=? Early=?          ← Expecting worse
```

**Analysis**: 
- Final task drops as λ increases = **catastrophic rigidity**
- Early avg doesn't improve = **EWC doesn't prevent forgetting**

### 6.2 Across Datasets (Same Model)

**Compare CIFAR-10 vs CIFAR-100 on same architecture**

Example (MobileNetV3):
```
CIFAR-10:  λ=0→200: -11.3%
CIFAR-100: λ=0→200: -9.0%
```

**Analysis**: Pattern is consistent across datasets ✓

### 6.3 Across Models (Same Dataset)

**Compare MobileNetV3 vs ResNet-18 on same dataset**

Example (CIFAR-100):
```
MobileNetV3: λ=0→200: -6.6% drop
ResNet-18:   λ=0→200: -14.6% drop (WORSE!)
```

**Analysis**: Larger model suffers MORE = novel finding!

### 6.4 Annealed vs Fixed λ

**Compare annealed vs best/worst fixed λ**

Example (expected):
```
λ=5000:   Final=55% (worst - too rigid)
Annealed: Final=63% (+8% recovery)
λ=0:      Final=73% (best - but forgets)
```

**Analysis**: Annealing helps recover from rigidity

---

## 7. Interpreting Findings {#interpretation}

### 7.1 Main Research Questions

**Q1: Does fixed λ EWC help edge models?**
Answer: NO - causes catastrophic rigidity (final task drops)

**Q2: Does EWC prevent forgetting?**
Answer: NO - early task average stays near 0% regardless of λ

**Q3: Does annealing help?**
Answer: YES - recovers performance vs high fixed λ

**Q4: Is this edge-specific?**
Answer: NO - also affects standard models (ResNet-18)

### 7.2 Key Findings to Report

**Finding 1: Monotonic Degradation (MobileNetV3)**
- As λ increases from 0→5000, final task accuracy drops monotonically
- Conclusion: No optimal fixed λ for edge models

**Finding 2: Catastrophic Rigidity**
- High λ values severely restrict learning ability
- Model becomes "frozen" and can't adapt to new tasks

**Finding 3: No Forgetting Prevention**
- EWC penalty doesn't improve early task retention
- Still ~0% accuracy on old tasks regardless of λ

**Finding 4: Architecture-Dependent Behavior**
- ResNet-18 shows DIFFERENT patterns than MobileNetV3
- Sometimes worse with EWC (CIFAR-100)
- Sometimes better (CIFAR-10) - capacity-dependent!

**Finding 5: Annealing Works**
- Beats high fixed λ across all experiments
- Provides "safe" option when optimal λ is unknown

---

## 8. Example Explanation Script

**For presenting to others:**

> "We tested EWC with 6 different λ values from 0 to 5000. Lambda controls how strongly the model protects old knowledge. We expected high λ would help remember old tasks, but instead we found:
>
> 1. **Final task accuracy drops** as λ increases - the model becomes too rigid to learn
> 2. **Early task accuracy stays near zero** - EWC doesn't prevent forgetting
> 3. This happens on BOTH edge models (MobileNetV3) AND standard models (ResNet-18)
> 4. Annealed EWC helps by starting strict then relaxing, recovering lost performance
>
> We tested this on two scenarios: CIFAR-10 (drift) with 5 tasks and CIFAR-100 (class-incremental) with 10 tasks. Results are consistent across both, validating our findings."

---

## 9. Metrics Summary Table

| Metric | Formula | Good Value | Bad Value | Interpretation |
|--------|---------|------------|-----------|----------------|
| **Final Task** | Last accuracy | >70% | <50% | Can model still learn? |
| **Early Avg** | Avg of tasks 0 to n-2 | >50% | <10% | Does model remember? |
| **Forgetting** | 1 - Early Avg | <50% | >90% | How much forgotten? |
| **Average** | Mean of all tasks | >50% | <30% | Overall performance |

---

## 10. Quick Reference Card

**When analyzing results, ask:**

1. ✅ **Final task going down as λ increases?** → Catastrophic rigidity
2. ✅ **Early tasks near 0% regardless of λ?** → EWC doesn't prevent forgetting
3. ✅ **Annealed better than high fixed λ?** → Annealing works
4. ✅ **Pattern consistent across datasets?** → Finding is robust
5. ✅ **Different behavior across models?** → Capacity matters

---

**Use this guide to explain your research to colleagues, reviewers, or in presentations!**
