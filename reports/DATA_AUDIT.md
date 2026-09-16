# DATA AUDIT — UCI Student Dropout & Academic Success Dataset

**File:** `data/raw/student_dropout.csv`  
**Audit Date:** 2026-09-16  
**Separator:** semicolon (`;`)  
**Encoding:** UTF-8 with BOM

---

## 1. Dataset Dimensions

| Metric | Value |
|--------|-------|
| Rows | **4 424** |
| Columns | **37** (36 features + 1 target) |
| File size (on disk) | ~533 KB |

---

## 2. Data Types Overview

| Category | Count | Columns |
|----------|-------|---------|
| Binary integer (0/1) | 8 | `Daytime/evening attendance`, `Displaced`, `Educational special needs`, `Debtor`, `Tuition fees up to date`, `Gender`, `Scholarship holder`, `International` |
| Low-cardinality integer (3–50 unique) | 21 | Coded categoricals + academic unit counts |
| Float (continuous) | 7 | Grades, admission score, macro-economic indicators |
| String / object | 1 | `Target` (the outcome label) |

> **Note:** All 36 feature columns are numeric (int64 or float64). The target is the only object/string column.

---

## 3. Missing Values

| Metric | Value |
|--------|-------|
| Total nulls across all 37 columns | **0** |
| Missing % | **0.00 %** |

✅ **The dataset is complete — no imputation required.**

---

## 4. Duplicate Rows

| Metric | Value |
|--------|-------|
| Duplicate rows | **0** |

✅ **No exact duplicate records detected.**

---

## 5. Target Variable Distribution

| Class | Count | Share |
|-------|------:|------:|
| **Graduate** | 2 209 | **49.93 %** |
| **Dropout** | 1 421 | **32.12 %** |
| **Enrolled** | 794 | **17.95 %** |

> **Important:** The dataset has **3 classes**. For binary dropout prediction, `Enrolled` must be either merged with `Graduate` or excluded. Class imbalance (Dropout vs non-Dropout ≈ 32:68) is moderate but must be addressed.

---

## 6. Categorical Variables (Encoded as Integers)

| Column | Unique Values | Notes |
|--------|:---:|-------|
| Marital status | 6 | 1=single dominant (3 919/4 424) |
| Application mode | 18 | Highly skewed toward code 1 |
| Application order | 8 | 1st-choice dominant (3 026 records) |
| Course | 17 | 17 distinct programme codes |
| Previous qualification | 17 | Code 1 (secondary) = 3 717 records |
| Nationality | 21 | Code 1 (Portuguese) = vast majority |
| Mother's qualification | 29 | Coded 1–44 |
| Father's qualification | 34 | Coded 1–44 |
| Mother's occupation | 32 | Coded 0–194 (sparse high codes) |
| Father's occupation | 46 | Coded 0–195 (sparse high codes) |

---

## 7. Numerical Variables

### 7a. Continuous (float)

| Column | Min | Mean | Max | Std |
|--------|----:|-----:|----:|----:|
| Previous qualification (grade) | 95.0 | 132.61 | 190.0 | 13.19 |
| Admission grade | 95.0 | 126.98 | 190.0 | 14.48 |
| Curricular units 1st sem (grade) | 0.0 | 10.64 | 18.88 | 4.84 |
| Curricular units 2nd sem (grade) | 0.0 | 10.23 | 18.57 | 5.21 |
| Unemployment rate | 7.6 | 11.57 | 16.2 | 2.66 |
| Inflation rate | -0.8 | 1.23 | 3.7 | 1.38 |
| GDP | -4.06 | 0.00 | 3.51 | 2.27 |

> **Note:** Grades of 0.0 are structural zeros (students who never sat evaluations) — NOT missing data.

### 7b. Count-based integers (academic units)

| Column | Min | Mean | Max |
|--------|----:|-----:|----:|
| Curricular units 1st sem (enrolled) | 0 | 6.27 | 26 |
| Curricular units 1st sem (evaluations) | 0 | 8.30 | 45 |
| Curricular units 1st sem (approved) | 0 | 4.71 | 26 |
| Curricular units 1st sem (credited) | 0 | 0.71 | 20 |
| Curricular units 1st sem (without evaluations) | 0 | 0.14 | 12 |
| Curricular units 2nd sem (enrolled) | 0 | 6.23 | 23 |
| Curricular units 2nd sem (evaluations) | 0 | 8.06 | 33 |
| Curricular units 2nd sem (approved) | 0 | 4.44 | 20 |
| Curricular units 2nd sem (credited) | 0 | 0.54 | 19 |
| Curricular units 2nd sem (without evaluations) | 0 | 0.15 | 12 |
| Age at enrollment | 17 | 23.27 | 70 |

---

## 8. Binary Variables

| Column | Value=1 (%) | Value=0 (%) |
|--------|:-----------:|:-----------:|
| Daytime/evening attendance | 89.1 % (daytime) | 10.9 % (evening) |
| Displaced | 54.8 % | 45.2 % |
| Educational special needs | 1.2 % | 98.8 % |
| Debtor | 11.4 % | 88.6 % |
| Tuition fees up to date | 88.1 % | 11.9 % |
| Gender | 35.2 % (male) | 64.8 % (female) |
| Scholarship holder | 24.8 % | 75.2 % |
| International | 2.5 % | 97.5 % |

> **Warning:** `Educational special needs` and `International` are highly imbalanced (>97% in one class) — near-zero variance; risk of overfitting.

---

## 9. Macro-Economic Features

These three columns take only **9–10 discrete values** (national quarterly statistics shared across students in the same enrolment period):

| Column | Unique Values |
|--------|:---:|
| Unemployment rate | 10 |
| Inflation rate | 9 |
| GDP | 10 |

> **Warning:** These are time-linked contextual variables, NOT student-level features. Treat carefully to avoid data leakage in time-based splits.

---

## 10. Dropout-Risk Feature Ranking

Ranked by **absolute Pearson correlation** with binary dropout label (`Dropout=1`, others=0):

| Rank | Feature | |Corr| |
|------|---------|--------|
| 1 | Curricular units 2nd sem (grade) | **0.572** |
| 2 | Curricular units 2nd sem (approved) | **0.570** |
| 3 | Curricular units 1st sem (grade) | **0.481** |
| 4 | Curricular units 1st sem (approved) | **0.479** |
| 5 | Tuition fees up to date | **0.429** |
| 6 | Age at enrollment | 0.254 |
| 7 | Scholarship holder | 0.245 |
| 8 | Debtor | 0.229 |
| 9 | Gender | 0.204 |
| 10 | Application mode | 0.198 |
| 11 | Curricular units 2nd sem (evaluations) | 0.155 |
| 12 | Curricular units 2nd sem (enrolled) | 0.142 |
| 13 | Curricular units 1st sem (enrolled) | 0.125 |
| 14 | Displaced | 0.107 |
| 15 | Admission grade | 0.096 |
| 16 | Marital status | 0.094 |
| 17 | Curricular units 1st sem (evaluations) | 0.090 |
| 18 | Daytime/evening attendance | 0.080 |
| 19 | Curricular units 2nd sem (without evaluations) | 0.080 |
| 20 | Previous qualification (grade) | 0.078 |

> **Tip:** The top 5 features (academic performance + tuition payment status) explain the bulk of dropout variance. A logistic regression on these alone likely achieves a strong baseline AUC.

---

## 11. Data Quality Issues & Notes

| Issue | Severity | Detail |
|-------|----------|--------|
| Column name has trailing tab | Low | `"Daytime/evening attendance\t"` — tab character in header |
| Typo in column name | Low | `Nacionality` (should be `Nationality`) |
| Imbalanced binary features | Info | `Educational special needs`, `International` — near-zero variance |
| Grade=0 for dropouts | Info | Structural zeros — students who did not attempt exams |
| Macro features are time-grouped | Medium | 9–10 unique values; risk of target leakage in time-naive splits |
| 3-class target for binary task | Medium | `Enrolled` class must be handled explicitly before modelling |

---

## 12. Summary Verdict

| Dimension | Assessment |
|-----------|-----------|
| Completeness | ✅ 100% — zero nulls |
| Uniqueness | ✅ Zero duplicates |
| Scale | ✅ 4 424 rows — sufficient for ML |
| Target suitability | ⚠️ 3-class; needs binarisation or multi-class decision |
| Feature quality | ✅ Rich academic + demographic + economic mix |
| Ready for cleaning? | **Yes — schema confirmed, issues catalogued** |
