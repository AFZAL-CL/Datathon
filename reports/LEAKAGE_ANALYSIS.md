# Leakage Analysis

**Scenario A: Early/Admission Risk.** Uses only enrolment/admission-time fields and `early_admission_risk`, whose thresholds are observed admission-grade tertiles. It excludes semester performance features.

**Scenario B: Current Academic Risk.** Adds semester grades, enrolled/approved/evaluated units, and derived academic rates. These are post-enrolment and can be highly predictive of Target; they must not be described as admission-time prediction. `current_academic_risk` uses observed academic-progress tertiles.

Unemployment rate, Inflation rate, and GDP are national contextual variables shared by cohorts. They are retained for descriptive context, not treated as individual causal risk factors. Target is never used to create a feature.
