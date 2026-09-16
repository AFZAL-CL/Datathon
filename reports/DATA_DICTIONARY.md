# DATA DICTIONARY — UCI Student Dropout & Academic Success Dataset

**Source:** Realinho, V., Machado, J., Baptista, L., & Martins, M. V. (2022).  
**UCI ML Repository:** https://archive.ics.uci.edu/dataset/697/predict+students+dropout+and+academic+success  
**File:** `data/raw/student_dropout.csv` | Separator: `;` | Rows: 4 424 | Cols: 37

---

## Column Index

| # | Column Name | Raw dtype | Category | Description |
|---|-------------|-----------|----------|-------------|
| 0 | Marital status | int64 | Categorical | Civil status at time of enrolment |
| 1 | Application mode | int64 | Categorical | Application channel / mode used for admission |
| 2 | Application order | int64 | Ordinal | Application preference order (0=not preferred; 1=1st choice) |
| 3 | Course | int64 | Categorical | Programme/course enrolled in |
| 4 | Daytime/evening attendance | int64 | Binary | 1=daytime, 0=evening shift |
| 5 | Previous qualification | int64 | Categorical | Type of previous qualification before enrolment |
| 6 | Previous qualification (grade) | float64 | Continuous | Grade of previous qualification (0–200 scale) |
| 7 | Nacionality | int64 | Categorical | Student nationality code |
| 8 | Mother's qualification | int64 | Categorical | Mother's highest level of education |
| 9 | Father's qualification | int64 | Categorical | Father's highest level of education |
| 10 | Mother's occupation | int64 | Categorical | Mother's occupational group code |
| 11 | Father's occupation | int64 | Categorical | Father's occupational group code |
| 12 | Admission grade | float64 | Continuous | Admission exam / entry grade (0–200 scale) |
| 13 | Displaced | int64 | Binary | 1=student is a displaced person |
| 14 | Educational special needs | int64 | Binary | 1=student has educational special needs |
| 15 | Debtor | int64 | Binary | 1=student has outstanding financial debt to institution |
| 16 | Tuition fees up to date | int64 | Binary | 1=student's tuition fees are paid; 0=in arrears |
| 17 | Gender | int64 | Binary | 1=male, 0=female |
| 18 | Scholarship holder | int64 | Binary | 1=scholarship recipient |
| 19 | Age at enrollment | int64 | Discrete | Age (in years) at time of enrolment (17–70) |
| 20 | International | int64 | Binary | 1=international student |
| 21 | Curricular units 1st sem (credited) | int64 | Count | Units credited (recognised from prior learning) in semester 1 |
| 22 | Curricular units 1st sem (enrolled) | int64 | Count | Units enrolled in semester 1 |
| 23 | Curricular units 1st sem (evaluations) | int64 | Count | Number of evaluations in semester 1 |
| 24 | Curricular units 1st sem (approved) | int64 | Count | Units passed/approved in semester 1 |
| 25 | Curricular units 1st sem (grade) | float64 | Continuous | Average grade of approved units in semester 1 (0–20 scale) |
| 26 | Curricular units 1st sem (without evaluations) | int64 | Count | Units with no recorded evaluation in semester 1 |
| 27 | Curricular units 2nd sem (credited) | int64 | Count | Units credited (prior learning) in semester 2 |
| 28 | Curricular units 2nd sem (enrolled) | int64 | Count | Units enrolled in semester 2 |
| 29 | Curricular units 2nd sem (evaluations) | int64 | Count | Number of evaluations in semester 2 |
| 30 | Curricular units 2nd sem (approved) | int64 | Count | Units passed/approved in semester 2 |
| 31 | Curricular units 2nd sem (grade) | float64 | Continuous | Average grade of approved units in semester 2 (0–20 scale) |
| 32 | Curricular units 2nd sem (without evaluations) | int64 | Count | Units with no recorded evaluation in semester 2 |
| 33 | Unemployment rate | float64 | Macro-economic | National unemployment rate (%) at enrolment period |
| 34 | Inflation rate | float64 | Macro-economic | National inflation rate (%) at enrolment period |
| 35 | GDP | float64 | Macro-economic | GDP growth rate (%) at enrolment period |
| 36 | Target | object | **TARGET** | Outcome: `Graduate`, `Dropout`, or `Enrolled` |

---

## Categorical Code Mappings

### Marital Status (col 0)
| Code | Meaning |
|------|---------|
| 1 | Single |
| 2 | Married |
| 3 | Widower |
| 4 | Divorced |
| 5 | Facto union |
| 6 | Legally separated |

### Application Mode (col 1) — Selected
| Code | Meaning |
|------|---------|
| 1 | 1st phase — general contingent |
| 2 | Ordinance No. 612/93 |
| 5 | 1st phase — special contingent (Azores Island) |
| 7 | Holders of other higher courses |
| 10 | Ordinance No. 854-B/99 |
| 15 | International student (bachelor) |
| 16 | 1st phase — special contingent (Madeira Island) |
| 17 | 2nd phase — general contingent |
| 18 | 3rd phase — general contingent |
| 26 | Ordinance No. 533-A/99, item b2 (Different Plan) |
| 27 | Ordinance No. 533-A/99, item b3 (Other Institution) |
| 39 | Over 23 years old |
| 42 | Transfer |
| 43 | Change of course |
| 44 | Technological specialisation diploma holders |
| 51 | Change of institution/course |
| 53 | Short cycle diploma holders |
| 57 | Change of institution/course (International) |

### Course (col 3) — Selected
| Code | Meaning |
|------|---------|
| 33 | Biofuel Production Technologies |
| 171 | Animation and Multimedia Design |
| 8014 | Social Service (evening attendance) |
| 9003 | Agronomy |
| 9070 | Communication Design |
| 9085 | Veterinary Nursing |
| 9119 | Informatics Engineering |
| 9130 | Equiniculture |
| 9147 | Management |
| 9238 | Social Service |
| 9254 | Tourism |
| 9500 | Nursing |
| 9556 | Oral Hygiene |
| 9670 | Advertising and Marketing Management |
| 9773 | Journalism and Communication |
| 9853 | Basic Education |
| 9991 | Management (evening attendance) |

### Previous Qualification (col 5) — Selected
| Code | Meaning |
|------|---------|
| 1 | Secondary education |
| 2 | Higher education — bachelor's degree |
| 3 | Higher education — degree |
| 4 | Higher education — master's |
| 5 | Higher education — doctorate |
| 6 | Frequency of higher education |
| 9 | 12th year of schooling — not completed |
| 10 | 11th year of schooling — not completed |
| 12 | Other — 11th year of schooling |
| 14 | 10th year of schooling |
| 15 | 10th year of schooling — not completed |
| 19 | Basic education 3rd cycle (9th/10th/11th year) or equivalent |
| 38 | Basic education 2nd cycle (6th/7th/8th year) or equivalent |
| 39 | Technological specialisation course |
| 40 | Higher education — degree (1st cycle) |
| 42 | Professional higher technical course |
| 43 | Higher education — master's (2nd cycle) |

### Qualification Codes (Cols 8–9: Mother's/Father's Qualification) — Selected
| Code | Meaning |
|------|---------|
| 1 | Secondary Education - 12th Year of Schooling or Eq. |
| 2 | Higher Education - Bachelor's Degree |
| 3 | Higher Education - Degree |
| 4 | Higher Education - Master's |
| 5 | Higher Education - Doctorate |
| 6 | Frequency of Higher Education |
| 9 | 12th Year of Schooling - Not Completed |
| 10 | 11th Year of Schooling - Not Completed |
| 11 | 7th Year (Old) |
| 12 | Other - 11th Year of Schooling |
| 14 | 10th Year of Schooling |
| 18 | General commerce course |
| 19 | Basic Education 3rd Cycle (9th/10th/11th Year) or Equivalent |
| 22 | Technical-professional course |
| 26 | 7th year of schooling |
| 27 | 2nd cycle of the general high school course |
| 29 | 9th Year of Schooling - Not Completed |
| 30 | 8th year of schooling |
| 34 | Unknown |
| 35 | Can't read or write |
| 36 | Can read without having a 4th year of schooling |
| 37 | Basic education 1st cycle (4th/5th year) or equivalent |
| 38 | Basic Education 2nd Cycle (6th/7th/8th Year) or equivalent |
| 39 | Technological specialisation course |
| 40 | Higher education - degree (1st cycle) |
| 41 | Specialised higher studies course |
| 42 | Professional higher technical course |
| 43 | Higher Education - Master (2nd cycle) |
| 44 | Higher Education - Doctorate (3rd cycle) |

### Gender (col 17)
| Code | Meaning |
|------|---------|
| 0 | Female |
| 1 | Male |

---

## Feature Groups

### Group A — Socio-Demographic (at enrolment)
`Marital status`, `Nationality`, `Gender`, `Age at enrollment`, `International`, `Displaced`, `Educational special needs`

### Group B — Academic Background
`Previous qualification`, `Previous qualification (grade)`, `Admission grade`, `Application mode`, `Application order`, `Course`

### Group C — Parental Background
`Mother's qualification`, `Father's qualification`, `Mother's occupation`, `Father's occupation`

### Group D — Financial Status
`Debtor`, `Tuition fees up to date`, `Scholarship holder`

### Group E — Academic Performance (in-programme)
`Curricular units 1st/2nd sem (enrolled, evaluations, approved, grade, credited, without evaluations)`

### Group F — Macro-Economic Context
`Unemployment rate`, `Inflation rate`, `GDP`

### Target
`Target` → 3 classes: `Graduate` (50 %), `Dropout` (32 %), `Enrolled` (18 %)

---

## Known Schema Issues

| Column | Issue | Recommended Fix |
|--------|-------|----------------|
| `Daytime/evening attendance\t` | Trailing `\t` tab in name | Strip to `Daytime/evening attendance` |
| `Nacionality` | Typo | Rename to `Nationality` |
| `Target` | 3-class string; needs numeric encoding | Map: `Dropout`→1, `Graduate`→0; treat `Enrolled` per task scope |

---

## Value Ranges Summary

| Column | Min | Max | Notes |
|--------|----:|----:|-------|
| Previous qualification (grade) | 95.0 | 190.0 | Standardised scale |
| Admission grade | 95.0 | 190.0 | Standardised scale |
| Curricular units Xth sem (grade) | 0.0 | ~18.9 | 0.0 = no approved units (structural) |
| Age at enrollment | 17 | 70 | Right-skewed; most students 17–25 |
| Unemployment rate | 7.6 % | 16.2 % | 10 distinct values |
| Inflation rate | -0.8 % | 3.7 % | 9 distinct values |
| GDP | -4.06 % | 3.51 % | 10 distinct values |
