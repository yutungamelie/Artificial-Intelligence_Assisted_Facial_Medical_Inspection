# Tabular Data Preprocessing

## 表格資料前處理 | Tabular Data Preprocessing

This document describes how the hospital raw tabular data in the **Risk-Aware Clinical AI Screening System for Cognitive Function** project was converted into a model-ready dataset for cognitive-risk modeling.

The goal of this file is to make the data preprocessing workflow transparent, reproducible, and safe for a public portfolio repository. It explains the original cleaning logic, variable coding decisions, feature grouping, correlation-matrix exploration, and modeling-ready data preparation.

This document does **not** release any real patient-level data.

---

## 1. Purpose | 目的

The tabular data preprocessing workflow was designed to transform heterogeneous clinical research data into a structured modeling table.

The original data came from two major sources:

```text
1. Participant questionnaire forms
2. Physiological indicator forms
```

These sources were cleaned, coded, merged, renamed, filtered, and explored through pairwise correlation analysis before downstream modeling.

The final modeling direction was:

```text
physiological / psychological / behavioral indicators
→ MoCA cognitive score prediction
→ cognitive-risk screening
→ uncertainty-aware triage
```

---

## 2. Input Data Sources | 輸入資料來源

### 2.1 Hospital-Organized Raw Data

Original internal file:

```text
Raw Data (醫院整理).xlsx
```

This file represented the hospital-organized version of raw clinical research data.

It should not be included in a public GitHub repository because it may contain patient-level information.

### 2.2 Merged and Coded Raw Data

Intermediate internal file:

```text
Raw Data with Coding (已將兩個表格合併).xlsx
```

This file was created by merging and organizing two major tables into one cleaner Excel file.

The purpose was to create a structured data source that could support:

```text
variable coding
variable filtering
questionnaire score selection
physiological indicator selection
pairwise correlation analysis
modeling table construction
```

### 2.3 Questionnaire Data

The questionnaire data were derived from:

```text
訪談大綱
MoCA 量表
心理與行為問卷
```

Preprocessing decisions:

```text
only total-score variables were retained
questionnaire item-level columns were removed
Chinese variable names were translated into English
subject IDs were preserved only for internal linkage
```

Rationale:

- total scores are more stable and interpretable than individual questionnaire items;
- item-level variables increase dimensionality and redundancy;
- English variable names reduce encoding problems in statistical packages;
- subject IDs are necessary internally for merging, but should not be public.

### 2.4 Physiological Indicator Data

The physiological data included:

```text
disease history
medication information
blood test indicators
urine test indicators
body composition measures
vital signs
```

Important note:

Disease history and medication variables required careful interpretation. In the project notes, yellow-highlighted disease columns represented whether a participant had a disease diagnosis, while the following columns recorded whether related medications were used.

Example:

```text
HTN = 1
→ indicates hypertension diagnosis history or hypertension medication use

ARB / CCB / β-blocker columns
→ indicate related antihypertensive medication use
```

This means disease coding should not be treated as a purely mechanical transformation. It may require clinical interpretation and manual review.

---

## 3. Table Merging | 表格合併

The original preprocessing workflow merged questionnaire data and physiological indicator data into a single table.

Conceptual workflow:

```text
Questionnaire Table
    ├── subject ID
    ├── demographic variables
    ├── MoCA
    ├── CES-D
    ├── CPSQI
    ├── WHO-5
    └── Big Five personality scores

Physiological Indicator Table
    ├── subject ID
    ├── disease history
    ├── medication variables
    ├── blood markers
    ├── urine markers
    └── body composition variables

Merged Modeling Table
    ├── subject ID
    ├── demographics
    ├── physiological indicators
    ├── psychological questionnaire scores
    ├── cognitive target
    └── coding / data-quality notes
```

For the public portfolio version, this merging logic should be represented using synthetic data only:

```text
examples/synthetic_patient_examples.csv
```

---

## 4. Variable Coding | 變數 Coding

A separate coding table was used to document variable definitions, data status, and preprocessing decisions.

The coding documentation included:

```text
participant questionnaire coding
physiological indicator coding
variable retention status
notes on suspicious or inconsistent coding
```

### 4.1 Example: Group Coding

The project notes flagged possible coding inconsistencies for `Group`.

Example issue:

```text
Some participants had Group = 1 indicating DM,
but medication-related DM columns appeared to be coded as 0.

One participant had inconsistent Group coding across two data files.
```

Risk-aware implication:

> Coding inconsistencies should be documented and flagged rather than silently corrected.

Recommended public implementation:

```python
def flag_group_coding_inconsistency(df):
    ...
```

### 4.2 Example: Sex Coding

```text
Sex
0 = female
1 = male
```

Binary categorical variables were retained as original binary encodings in the statistical modeling stage.

### 4.3 Example: Education Coding

```text
Edu<12
0 = education years >= 12
1 = education years < 12
```

This type of variable may be useful for adjustment or subgroup analysis, but should be documented clearly.

---

## 5. Chinese-to-English Variable Naming | 中文變數轉英文

Some R / Python packages may not handle Chinese column names consistently, or may produce encoding issues during analysis.

Therefore, variables were translated into English names.

Examples:

| Original Meaning | English Variable Name |
|---|---|
| 年齡 | `Age` |
| 性別 | `Sex` |
| 身高 | `BH` |
| 腰圍 | `WC` |
| 收縮壓 | `SBP` |
| 舒張壓 | `DBP` |
| 體重 | `BW` |
| 除脂體重 | `FFM` |
| 脂肪重量 | `BFM` |
| 體脂百分比 | `BFP` |
| 認知量表總分 | `MoCA` |
| 總體水分 | `TBW` |
| 血小板數 | `Plt` |

Recommended public implementation:

```python
VARIABLE_RENAME_MAP = {
    "年齡": "Age",
    "性別": "Sex",
    "身高": "BH",
    "腰圍": "WC",
    "收縮壓": "SBP",
    "舒張壓": "DBP",
    "體重": "BW",
    "認知量表總分": "MoCA"
}
```

---

## 6. Variable Filtering | 變數篩選

The final modeling dataset did not include every collected variable.

Several types of variables were removed or deprioritized before modeling.

### 6.1 Removed: Questionnaire Item-Level Columns

Questionnaire sub-items were removed when total scores already represented the construct.

Reason:

```text
item-level variables increase dimensionality
total scores are more interpretable
item-level variables may create redundancy
```

Examples of retained total scores:

```text
CES-D
CPSQI
WHO-5
MoCA
Extraversion
Agreeableness
Conscientiousness
Neuroticism
Openness
```

### 6.2 Removed or Deprioritized: Highly Subjective Self-Reported Items

Some lifestyle and behavioral variables were noted as self-reported and potentially less reliable.

Examples:

```text
ExhSleep
smoking-related detailed variables
dietary habit details
activity comparison variables
```

Reason:

```text
some variables are subjective
some variables may reflect attitude rather than objective state
some variables may be redundant with more reliable summary variables
```

### 6.3 Removed: Highly Homogeneous Variables

Variables with highly homogeneous distributions were removed because they provide limited information for modeling.

Reason:

```text
near-constant variables do not help prediction
near-constant variables can destabilize correlation analysis
near-constant variables may cause model fitting issues
```

### 6.4 Missing and Extreme Data Handling

The public portfolio version should document missingness and unusual values.

Recommended checks:

```text
missing rate per variable
number of unique values
near-zero variance
extreme min / max values
domain-plausibility checks
inconsistent disease-medication coding
```

Recommended public implementation:

```python
def filter_variables(df, missing_threshold=0.4, min_unique_values=2):
    ...
```

---

## 7. Retained Feature Groups | 保留變項群組

The retained variables can be organized into five major groups.

### 7.1 Grouping Variables

```text
Group
Sex
Age
```

Purpose:

- subject grouping;
- demographic adjustment;
- subgroup analysis.

### 7.2 Body and Vital Indicators

```text
BH
WC
SBP
DBP
BW
FFM
BFM
BFP
```

Interpretation:

| Variable | Meaning |
|---|---|
| `BH` | body height |
| `WC` | waist circumference |
| `SBP` | systolic blood pressure |
| `DBP` | diastolic blood pressure |
| `BW` | body weight |
| `FFM` | fat-free mass |
| `BFM` | body fat mass |
| `BFP` | body fat percentage |

### 7.3 Sleep-Related Indicators

```text
Chrono
Interrupt
Nap
```

Notes:

- `Chrono`: sleep timing category;
- `Interrupt`: average number of sleep interruptions;
- `Nap`: average daily nap duration.

Risk-aware note:

These variables may reflect useful behavioral signals, but some sleep-related self-report variables may require careful interpretation.

### 7.4 Questionnaire Total Scores

```text
CES-D
CPSQI
WHO-5
MoCA
Extraversion
Agreeableness
Conscientiousness
Neuroticism
Openness
```

Interpretation:

| Variable | Meaning |
|---|---|
| `CES-D` | depressive symptom score |
| `CPSQI` | Pittsburgh Sleep Quality Index |
| `WHO-5` | well-being index |
| `MoCA` | Montreal Cognitive Assessment total score |
| `Extraversion` | Big Five extraversion |
| `Agreeableness` | Big Five agreeableness |
| `Conscientiousness` | Big Five conscientiousness |
| `Neuroticism` | Big Five neuroticism |
| `Openness` | Big Five openness |

MoCA is the main cognitive outcome for this portfolio project.

### 7.5 Blood and Urine Indicators

```text
TBW
FIB4
A1C
GluAC
Insulin
TCHO
LDL
TG
HDL
Cr
GFR
UACR
UA
ALT
AST
T-Bil
D-Bil
Hb
Plt
hsCRP
Ferritin
```

These variables represent body composition, glucose metabolism, lipid metabolism, kidney function, liver function, hematology, inflammation, and iron-related status.

In the thesis modeling results, `TBW` and `Plt` were especially important because they emerged as stable predictors of MoCA across multiple modeling strategies.

---

## 8. Pairwise Correlation Matrix | 兩兩相關矩陣

Pairwise correlation analysis was used as an exploratory tool to understand the relationship structure among variables.

The original preprocessing notes reference several correlation-matrix outputs:

```text
pairwise correlation matrix.csv
cor_var_save_and_check_2.xlsx
cor_save_0702.xlsx
cor_save_0703.xlsx
```

The public portfolio version should not publish the original workbook if it contains real patient-level derived values. Instead, the repository can include:

```text
reports/feature_grouping_summary.md
examples/synthetic_correlation_summary.csv
```

### 8.1 Purpose

The pairwise correlation matrix was used to:

```text
inspect variable relationships
identify redundant variables
group related indicators
support target-selection strategy
identify |correlation| >= 0.3 variable pairs
inform downstream modeling priorities
```

### 8.2 Correlation Matrix R Workflow

The uploaded `Correlation Matrix.Rmd` shows the workflow used to generate the correlation matrix.

Core steps:

```r
origData <- read.csv(...)[2:118]
origData$ID <- 1:110

encoded_features <- read.csv("encoded_features_64.csv")
encoded_features$ID <- 1:110

merged_data <- merge(origData, encoded_features, by = "ID")
```

The workflow also defined a reusable `cor_check()` function:

```r
cor_check <- function(X_name, origData, plot_path, csv_path, w = 1200, h = 1200) {
  x <- origData[, X_name, drop = FALSE]
  x <- as.data.frame(scale(x))
  cor_data <- cor(x, use = "pairwise.complete.obs")
  corrplot.mixed(cor_data, lower = "number", upper = "color", order = "hclust")
  write.csv(cor_data, file = csv_path, row.names = TRUE)
  return(cor_data)
}
```

Important implementation details:

```text
continuous variables were standardized before correlation
correlation was computed with pairwise.complete.obs
constant columns were removed before correlation
corrplot.mixed was used for visualization
hierarchical clustering order was used in the plot
correlation matrix was exported as CSV
merged image features could also be included
```

### 8.3 Removing Constant Columns

The R workflow removed constant columns before computing the correlation matrix:

```r
constant_columns <- sapply(origData, function(col) length(unique(col)) == 1)
origData <- origData[, !constant_columns]
```

This is important because constant variables can produce undefined correlations.

### 8.4 Correlation Threshold

The project notes mention selecting variable pairs with:

```text
|correlation| >= 0.3
```

This threshold was used for exploratory grouping, not as a final causal or clinical rule.

Risk-aware interpretation:

> Correlation-based feature grouping helps understand redundancy and association structure, but it does not prove causal relationships.

---

## 9. Standardization for Modeling | 建模前標準化

Before statistical modeling, continuous variables were standardized.

The thesis preprocessing logic used:

```text
Z-score standardization
mean = 0
standard deviation = 1
```

Purpose:

```text
remove scale differences
improve model stability
make coefficients more comparable
support regularized models such as Lasso
support neural-network training
```

Categorical binary variables, such as sex, retained their original 0 / 1 encoding.

Recommended public implementation:

```python
from sklearn.preprocessing import StandardScaler

continuous_cols = [...]
binary_cols = [...]

scaler = StandardScaler()
df_scaled[continuous_cols] = scaler.fit_transform(df[continuous_cols])
df_scaled[binary_cols] = df[binary_cols]
```

---

## 10. Modeling-Ready Dataset | 最終可建模資料

The final modeling-ready table should contain:

```text
one row per participant
one subject identifier for internal linkage
demographic variables
retained physiological indicators
retained questionnaire total scores
MoCA target variable
data-quality flags
```

Public portfolio equivalent:

```text
examples/synthetic_patient_examples.csv
```

Recommended columns:

```text
synthetic_patient_id
Age
Sex
BH
WC
SBP
DBP
BW
FFM
BFM
BFP
TBW
A1C
GluAC
LDL
HDL
TG
Cr
GFR
UACR
Hb
Plt
hsCRP
Ferritin
CES-D
CPSQI
WHO-5
MoCA
missingness_flag
data_quality_flag
```

---

## 11. Suggested Public Code Mapping | 對應 Repo 程式模組

This preprocessing workflow maps to the following public repository modules:

```text
src/data_preprocessing/
├── tabular_cleaning.py
├── variable_filtering.py
└── correlation_grouping.py
```

### 11.1 `tabular_cleaning.py`

Suggested responsibilities:

```text
load synthetic CSV
validate schema
rename variables
merge questionnaire and physiological tables
remove duplicate columns
standardize continuous variables
preserve binary categorical variables
export cleaned modeling table
```

### 11.2 `variable_filtering.py`

Suggested responsibilities:

```text
calculate missing rate
detect constant / near-constant variables
flag high-missingness variables
separate retained / excluded variables
export variable filtering summary
```

### 11.3 `correlation_grouping.py`

Suggested responsibilities:

```text
compute pairwise correlation matrix
use pairwise complete observations
remove constant columns
flag |correlation| >= 0.3
group related variables
export synthetic correlation summary
```

---

## 12. Risk-Aware Data Preprocessing Principles | 風險意識前處理原則

For clinical AI, preprocessing is not just data cleaning. It is part of risk control.

### 12.1 Do Not Hide Data Problems

Suspicious coding, missingness, low variance, and inconsistent records should be flagged.

```text
bad practice:
silently overwrite suspicious values

better practice:
document coding issue + add quality flag
```

### 12.2 Do Not Treat Correlation as Causation

The correlation matrix is useful for exploration, but it cannot determine causal direction.

```text
correlation matrix
→ feature grouping / redundancy detection

not:
→ causal mechanism proof
```

### 12.3 Preserve Traceability

Each retained variable should be traceable to:

```text
original source table
coding definition
cleaning decision
feature group
modeling role
risk interpretation
```

### 12.4 Separate Internal Research Data from Public Demo Data

For the public GitHub repository:

```text
internal clinical data
→ never released

synthetic examples
→ safe for portfolio demonstration
```

---

## 13. Portfolio-Safe Output Files | 可公開展示輸出

Recommended public outputs:

```text
examples/synthetic_patient_examples.csv
examples/synthetic_patient_input_schema.json
examples/sample_risk_outputs.json
reports/feature_grouping_summary.md
reports/tabular_preprocessing_summary.md
```

Do not publish:

```text
Raw Data (醫院整理).xlsx
Raw Data with Coding (已將兩個表格合併).xlsx
original pairwise correlation matrix with real values
original patient-level MoCA or biomarker values
```

---

## 14. Key Takeaway | 核心重點

> The tabular preprocessing workflow transformed heterogeneous clinical research records into a structured, interpretable, and model-ready dataset by merging questionnaire and physiological tables, retaining clinically meaningful summary variables, translating variables into English, filtering unreliable or redundant variables, standardizing continuous indicators, and using pairwise correlation analysis to understand feature relationships.

中文版本：

> 這份 tabular data preprocessing 的核心，是把醫院 raw data 轉成可建模、可追蹤、可解釋的資料表：先合併問卷與生理指標資料，再保留臨床上有意義的總分與生理指標，將變數轉成英文，刪除不穩定或冗餘欄位，標準化連續變數，最後用 pairwise correlation matrix 理解特徵之間的關係。

---