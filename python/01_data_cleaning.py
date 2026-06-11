"""
Phase 1: Data Cleaning Pipeline
St. Martin's Hospital — Heart Disease Risk & Cost Analysis
-----------------------------------------------------------
Takes the raw, messy hospital extract and produces a clean,
analysis-ready dataset.

Run from inside the python/ folder:
    python 01_data_cleaning.py

Reads from  ../data/st_martins_hospital_raw.csv
Writes to   ../data/st_martins_hospital_cleaned.csv
"""

import pandas as pd
import numpy as np

# ── LOAD ────────────────────────────────────────────────
df = pd.read_csv('../data/st_martins_hospital_raw.csv')
print(f"Raw shape: {df.shape}")

# ── 1. REMOVE DUPLICATES ────────────────────────────────
# Why: Prevents double-counting patients in risk and cost analysis
before = len(df)
df = df.drop_duplicates()
print(f"Removed {before - len(df)} duplicates -> {len(df)} rows remain")

# ── 2. STANDARDISE GENDER ───────────────────────────────
# Why: "M", "male", "MALE" must all become "Male" for accurate splits
df['Gender'] = df['Gender'].str.strip().str.lower()
df['Gender'] = df['Gender'].map({
    'male': 'Male', 'm': 'Male',
    'female': 'Female', 'f': 'Female'
})

# ── 3. CLEAN BLOOD PRESSURE ─────────────────────────────
# Why: Mixed types ("152 mmHg", "130/85") prevent numeric analysis
def clean_bp(val):
    if pd.isna(val):
        return np.nan
    val = str(val).replace(' mmHg', '').strip()
    if '/' in val:
        val = val.split('/')[0]          # keep systolic
    try:
        result = float(val)
        if result > 250:                 # physiologically implausible
            return np.nan
        return result
    except ValueError:
        return np.nan

df['Blood_Pressure_Systolic'] = df['Blood_Pressure_Systolic'].apply(clean_bp)

# ── 4. CLEAN CHOLESTEROL — cap outliers ─────────────────
# Why: Values like 15 or 950 are lab errors that skew means
df.loc[df['Cholesterol_Level'] < 100, 'Cholesterol_Level'] = np.nan
df.loc[df['Cholesterol_Level'] > 400, 'Cholesterol_Level'] = np.nan

# ── 5. CLEAN BMI — cap outliers ─────────────────────────
# Why: BMI of 5 or 85 is impossible; distorts obesity analysis
df.loc[df['BMI'] < 12, 'BMI'] = np.nan
df.loc[df['BMI'] > 60, 'BMI'] = np.nan

# ── 6. STANDARDISE SMOKING STATUS ───────────────────────
# Why: "Yes", "Smoker", "Current" all mean the same thing
smoking_map = {
    'never': 'Never', 'non-smoker': 'Never', 'no': 'Never',
    'former': 'Former', 'ex-smoker': 'Former', 'previously': 'Former',
    'current': 'Current', 'smoker': 'Current', 'yes': 'Current'
}
df['Smoking_Status'] = df['Smoking_Status'].str.strip().str.lower().map(smoking_map)

# ── 7. STANDARDISE DIABETES ─────────────────────────────
# Why: "1", "True", "Y" must all become "Yes" for binary analysis
yes_vals = ['yes', 'y', '1', 'true']
no_vals = ['no', 'n', '0', 'false']
df['Diabetes_Diagnosis'] = df['Diabetes_Diagnosis'].str.strip().str.lower()
df['Diabetes_Diagnosis'] = df['Diabetes_Diagnosis'].apply(
    lambda x: 'Yes' if x in yes_vals else ('No' if x in no_vals else np.nan)
)

# ── 8. STANDARDISE HEART DISEASE RISK ───────────────────
# Why: "high", "HIGH", "High" must merge for risk stratification
df['Heart_Disease_Risk'] = df['Heart_Disease_Risk'].str.strip().str.title()

# ── 9. FIX HOSPITAL VISITS — replace -1 with NaN ────────
# Why: Negative visits are system errors, not real data
df.loc[df['Hospital_Visits'] < 0, 'Hospital_Visits'] = np.nan

# ── 10. CLEAN TREATMENT COST ────────────────────────────
# Why: "£8500.00" and "6200 GBP" can't be summed as-is
def clean_cost(val):
    if pd.isna(val):
        return np.nan
    val = str(val).replace('£', '').replace('GBP', '').replace(',', '').strip()
    try:
        return float(val)
    except ValueError:
        return np.nan

df['Treatment_Cost'] = df['Treatment_Cost'].apply(clean_cost)

# ── 11. STANDARDISE DISCHARGE STATUS ────────────────────
# Why: "Sent Home" = "Discharged", "Still In" = "Admitted", etc.
discharge_map = {
    'discharged': 'Discharged', 'sent home': 'Discharged',
    'admitted': 'Admitted', 'still in': 'Admitted',
    'transferred': 'Transferred', 'moved': 'Transferred',
    'deceased': 'Deceased', 'dead': 'Deceased'
}
df['Discharge_Status'] = df['Discharge_Status'].str.strip().str.lower().map(discharge_map)

# ── 12. ENFORCE FINAL DATA TYPES ────────────────────────
for col in ['Blood_Pressure_Systolic', 'Cholesterol_Level', 'BMI',
            'Treatment_Cost', 'Hospital_Visits']:
    df[col] = pd.to_numeric(df[col], errors='coerce')

# ── SAVE ────────────────────────────────────────────────
df.to_csv('../data/st_martins_hospital_cleaned.csv', index=False)

print(f"\nCleaned shape: {df.shape}")
print(f"\nNull counts after cleaning:\n{df.isnull().sum()}")
print(f"\nStandardised category values:")
for col in ['Gender', 'Smoking_Status', 'Diabetes_Diagnosis',
            'Heart_Disease_Risk', 'Discharge_Status']:
    print(f"  {col}: {sorted(df[col].dropna().unique())}")
print("\nCleaning complete. Saved as st_martins_hospital_cleaned.csv")
