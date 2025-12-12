"""
clean_data.py
Full offline cleaning pipeline tailored to the variable list you provided (ANZHFR-style).
- Paste your local CSV in the same folder.
- Edit INPUT_CSV to your filename.
- Run: python clean_data.py
This script performs:
  - mapping of labelled numeric codes to text labels (all provided dbl+lbl variables)
  - constructs datetime-like fields from year/month/hms components (sets day=1)
  - derives LOS and time_to_surgery
  - basic bounds checking and missing-value handling
  - saves cleaned CSV locally
"""


import os
import sys
from datetime import datetime
import pandas as pd
import numpy as np
from sklearn.impute import KNNImputer


print("Python is looking in:", os.getcwd())
print("Files in this directory:", os.listdir())


# ===== CONFIG - change INPUT_CSV to your local confidential file =====
INPUT_CSV = "unsw_datathon_2025.csv"
OUTPUT_CSV = "cleaned_anzhfr_full.csv"
BACKUP_CSV = "backup_original.csv"
# ===================================================================


def safe_read_csv(path):
    if not os.path.exists(path):
        print(f"ERROR: file not found: {path}")
        sys.exit(1)
    return pd.read_csv(path)


def backup_original(df):
    print(f">>> Saving local backup to {BACKUP_CSV}")
    df.to_csv(BACKUP_CSV, index=False)


def overview(df, title="Overview"):
    print(f"\n=== {title} ===")
    print("Shape:", df.shape)
    print("Columns:", ", ".join(df.columns.tolist()))
    print("Missing (top 20):")
    print(df.isna().sum().sort_values(ascending=False).head(20))
    print("====================\n")


# ---------- mapping dictionaries based on your labels ----------
sex_map = {1: "Male", 2: "Female", 3: "Intersex or indeterminate"}


ptype_map = {1: "Public", 2: "Private", 3: "Overseas"}


uresidence_map = {
    1: "Private residence",
    2: "Residential aged care facility",
    3: "Other"
}


e_dadmit_map = {
    1: "Yes",
    2: "No - transferred from another hospital (via ED)",
    3: "No - in-patient fall",
    4: "No - transferred from another hospital (direct to ward)"
}


painassess_map = {
    1: "Within 30 minutes of ED presentation",
    2: "Greater than 30 minutes of ED presentation",
    3: "Pain assessment not documented or not done"
}


painmanage_map = {
    1: "Given within 30 minutes of ED presentation",
    2: "Given more than 30 minutes after ED presentation",
    3: "Not required – already provided by paramedics",
    4: "Not required – no pain documented on assessment"
}


tfanalges_map = {1: "No", 2: "Yes"}


ward_map = {
    1: "Hip fracture unit/Orthopaedic ward/preferred ward",
    2: "Outlying ward",
    3: "HDU / ICU / CCU"
}


walk_map = {
    1: "Walks without walking aids",
    2: "Walks with either a stick or crutch",
    3: "Walks with two aids or frame",
    4: "Uses a wheelchair / bed bound"
}


cogassess_map = {
    1: "Not assessed",
    2: "Assessed and normal",
    3: "Assessed and abnormal or impaired"
}


cogstat_map = {
    1: "Normal cognition",
    2: "Impaired cognition or known dementia"
}


addelassess_map = {
    1: "Not assessed",
    2: "Assessed and not identified",
    3: "Assessed and identified"
}


bonemed_map = {
    1: "No bone protection medication",
    2: "Calcium and/or vitamin D only",
    3: "Bisphosphonates/denosumab/romosozumab/teriparitide/raloxifene/HRT"
}


passess_map = {
    1: "No assessment conducted",
    2: "Geriatrician / Geriatric Team",
    3: "Physician / Physician Team",
    4: "GP",
    5: "Specialist nurse"
}


afracture_map = {
    1: "Not pathological or atypical fracture",
    2: "Pathological fracture",
    3: "Atypical fracture"
}


ftype_map = {
    1: "Intracapsular undisplaced/impacted displaced",
    2: "Intracapsular displaced",
    3: "Per/intertrochanteric",
    4: "Subtrochanteric"
}


asa_map = {
    1: "Healthy individual with no systemic disease",
    2: "Mild systemic disease not limiting activity",
    3: "Severe systemic disease that limits activity but is not incapacitating",
    4: "Incapacitating systemic disease constantly life threatening",
    5: "Moribund not expected to survive 24 hours"
}


frailty_map = {
    1: "Very Fit",
    2: "Well",
    3: "Well, with treated comorbid disease",
    4: "Vulnerable",
    5: "Mildly frail",
    6: "Moderately frail",
    7: "Severely frail",
    8: "Very severely frail",
    9: "Terminally ill",
    10: "Frailty assessment using other validated tool"
}


delay_map = {
    1: "No delay, surgery completed <48 hours",
    2: "Delay: patient medically unfit",
    3: "Delay: anticoagulation issues",
    4: "Delay: theatre availability",
    5: "Delay: surgeon availability",
    6: "Delay: delayed diagnosis of hip fracture",
    7: "Other (state reason)"
}


anaesth_map = {
    1: "General anaesthesia",
    2: "Spinal anaesthesia",
    3: "General and spinal anaesthesia",
    4: "Spinal / regional anaesthesia",
    5: "General and spinal/regional anaesthesia",
    6: "Other"
}


analges_map = {
    1: "Nerve block before OT",
    2: "Nerve block in OT",
    3: "Both",
    4: "Neither"
}


consult_map = {1: "No", 2: "Yes"}


wbear_map = {
    1: "Unrestricted weight bearing",
    2: "Restricted / non weight bearing"
}


mobil_map = {
    1: "Mobilised day 1 (opportunity given)",
    2: "Not mobilised day 1"
}


pulcers_map = {1: "No", 2: "Yes"}


fassess_map = {
    1: "No",
    2: "Performed during admission",
    3: "Awaits falls clinic assessment",
    4: "Further intervention not appropriate",
    5: "Not relevant"
}


dbonemed1_map = {
    1: "No bone protection medication",
    2: "Yes - Calcium and/or vitamin D only",
    3: "Yes - Bisphosphonates/denosumab/romosozumab/teriparitide/raloxifene/HRT",
    4: "No but received prescription at separation from hospital"
}


delassess_map = {
    1: "Not assessed",
    2: "Assessed and not identified",
    3: "Assessed and identified"
}


malnutrition_map = {
    1: "Not done",
    2: "Malnourished",
    3: "Not malnourished"
}


ons_map = {1: "No", 2: "Yes"}


mobil2_map = {1: "No", 2: "Yes"}


wdest_map = {
    1: "Private residence",
    2: "Residential aged care facility",
    3: "Rehabilitation unit public",
    4: "Rehabilitation unit private",
    5: "Other hospital / ward / specialty",
    6: "Deceased",
    7: "Short term care in residential care facility (NZ only)",
    8: "Other"
}


dresidence_map = {
    1: "Private residence",
    2: "Residential aged care facility",
    3: "Deceased",
    4: "Other"
}


fresidence2_map = wdest_map  # same set as wdest/residence mapping


weight_bear120_map = {
    1: "Unrestricted weight bearing",
    2: "Restricted / non weight bearing"
}


fwalk2_map = {
    1: "Walks without walking aids",
    2: "Walks with either a stick or crutch",
    3: "Walks with two aids or frame",
    4: "Uses a wheelchair / bed bound",
    5: "Not relevant"
}


fbonemed2_map = {
    1: "No bone protection medication",
    2: "Calcium and/or vitamin D only",
    3: "Bisphosphonates/denosumab/romosozumab/teriparitide/raloxifene/HRT"
}


fop2_map = {
    1: "No reoperation",
    2: "Reduction of dislocated prosthesis",
    3: "Washout or debridement",
    4: "Implant removal",
    5: "Revision of internal fixation",
    6: "Conversion to hemiarthroplasty",
    7: "Conversion to total hip replacement",
    8: "Excision arthroplasty",
    9: "Periprosthetic fracture",
    10: "Revision arthroplasty",
    11: "Not relevant"
}


# surgery flag mapping
surg_map = {
    1: "No",
    2: "Yes",
    3: "No – surgical fixation not clinically indicated",
    4: "No – patient for palliation",
    5: "No – other reason"
}


# geriatric medicine assessed: note original had [0] No; [1] Yes; [8], [9]
gerimed_map = {
    0: "No",
    1: "Yes",
    8: "No geriatric medicine service available",
    9: "Not known"
}


mort_map = {1: "Alive", 2: "Deceased"}


# ---------------- end mappings ----------------


def apply_mappings(df):
    # Helper to map many columns, skip if column not present
    mapping_pairs = [
        ("sex", sex_map),
        ("ptype", ptype_map),
        ("uresidence", uresidence_map),
        ("e_dadmit", e_dadmit_map),
        ("painassess", painassess_map),
        ("painmanage", painmanage_map),
        ("tfanalges", tfanalges_map),
        ("ward", ward_map),
        ("walk", walk_map),
        ("cogassess", cogassess_map),
        ("cogstat", cogstat_map),
        ("addelassess", addelassess_map),
        ("bonemed", bonemed_map),
        ("passess", passess_map),
        ("afracture", afracture_map),
        ("ftype", ftype_map),
        ("asa", asa_map),
        ("frailty", frailty_map),
        ("delay", delay_map),
        ("anaesth", anaesth_map),
        ("analges", analges_map),
        ("consult", consult_map),
        ("wbear", wbear_map),
        ("mobil", mobil_map),
        ("pulcers", pulcers_map),
        ("fassess", fassess_map),
        ("dbonemed1", dbonemed1_map),
        ("delassess", delassess_map),
        ("malnutrition", malnutrition_map),
        ("ons", ons_map),
        ("mobil2", mobil2_map),
        ("wdest", wdest_map),
        ("dresidence", dresidence_map),
        ("fresidence2", fresidence2_map),
        ("weight_bear120", weight_bear120_map),
        ("fwalk2", fwalk2_map),
        ("fbonemed2", fbonemed2_map),
        ("fop2", fop2_map),
        ("surg", surg_map),
        ("gerimed", gerimed_map),
        ("mort30d", mort_map),
        ("mort90d", mort_map),
        ("mort120d", mort_map),
        ("mort365d", mort_map)
    ]


    for col, mdict in mapping_pairs:
        if col in df.columns:
            # Some columns may be floats (NaN); convert to Int where possible before mapping
            # We'll map using pd.Series.map which handles floats and NaN
            df[col] = df[col].map(mdict).fillna("Not recorded")
    return df


# ---------- Date construction ----------
def build_datetime_from_parts(df, prefix):
    """
    Given a prefix like 'arrdatetime', tries to build a datetime from:
      prefix + _year, prefix + _month, prefix + _datediff, prefix + _hms
    Creates column: prefix + '_dt'
    Uses the _datediff to determine the actual day within the month.
    """
    ycol = f"{prefix}_year"
    mcol = f"{prefix}_month"
    dcol = f"{prefix}_datediff"  # Day offset within month
    hmscol = f"{prefix}_hms"
    outcol = f"{prefix}_dt"
    
    # only attempt if at least year, month, and datediff exist in dataframe
    if ycol in df.columns and mcol in df.columns and dcol in df.columns:
        # Build base date from year-month-01
        y = df[ycol].fillna(0).astype(int).astype(str).replace("0", "")
        m = df[mcol].fillna(0).astype(int).astype(str).replace("0", "")
        
        # Create base datetime (first of month)
        base_strings = y + "-" + m + "-01"
        base_dt = pd.to_datetime(base_strings, errors="coerce", dayfirst=False)
        
        # Add the day offset from datediff
        day_offset = pd.to_timedelta(df[dcol].fillna(0), unit='D', errors='coerce')
        result_dt = base_dt + day_offset
        
        # Handle HMS component if it exists
        if hmscol in df.columns:
            hms = df[hmscol].fillna("00:00:00").astype(str)
            # Clean common formats like "12:00" -> "12:00:00"
            hms = hms.apply(lambda v: v if ":" in v and v.count(":")==2 else (v + ":00" if ":" in v else "00:00:00"))
            
            # Extract time components and add to date
            time_parts = hms.str.split(':', expand=True)
            time_parts.columns = ['hour', 'minute', 'second']
            time_parts = time_parts.apply(pd.to_numeric, errors='coerce').fillna(0)
            
            time_delta = pd.to_timedelta(
                time_parts['hour'].astype(int), unit='h'
            ) + pd.to_timedelta(
                time_parts['minute'].astype(int), unit='m'
            ) + pd.to_timedelta(
                time_parts['second'].astype(int), unit='s'
            )
            
            result_dt = result_dt + time_delta
        
        df[outcol] = result_dt
    else:
        # column components not present -> create empty dt col
        df[outcol] = pd.NaT
    return df


# ---------- derived durations ----------
def derive_durations(df):
    # Common pairs from your variable list:
    # transfer arrival: tarrdatetime_dt
    # operating hospital arrival: arrdatetime_dt
    # surgery: sdatetime_dt
    # discharge from hospital: hdisch_dt
    # discharge from acute ward: wdisch_dt (if present)
    # inpatient fracture/admission: admdatetimeop_dt
    pairs = [
        ("arrdatetime_dt", "hdisch_dt", "los_hospital_days"),
        ("arrdatetime_dt", "wdisch_dt", "los_acute_ward_days"),
        ("arrdatetime_dt", "sdatetime_dt", "time_to_surgery_hrs"),
        ("tarrdatetime_dt", "arrdatetime_dt", "transfer_to_operating_days")
    ]
    for start, end, newcol in pairs:
        if start in df.columns and end in df.columns:
            if "hrs" in newcol or "time" in newcol:
                # hours
                df[newcol] = (df[end] - df[start]).dt.total_seconds() / 3600.0
            else:
                df[newcol] = (df[end] - df[start]).dt.days
        else:
            df[newcol] = np.nan
    return df


# ---------- numeric and bounds cleaning ----------
def numeric_and_bounds(df):
    # Age
    if 'age' in df.columns:
        df['age'] = pd.to_numeric(df['age'], errors='coerce')
        # null out obviously wrong ages
        df.loc[(df['age'] < 40) | (df['age'] > 110), 'age'] = np.nan
   
    # LOS reasonable bounds
    los_cols = ['los_hospital_days', 'los_acute_ward_days']
    for c in los_cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors='coerce')
            # negative or extremely large values -> NaN
            df.loc[(df[c] < 0) | (df[c] > 365), c] = np.nan


    # time_to_surgery hours reasonable bounds
    if 'time_to_surgery_hrs' in df.columns:
        df['time_to_surgery_hrs'] = pd.to_numeric(df['time_to_surgery_hrs'], errors='coerce')
        df.loc[(df['time_to_surgery_hrs'] < 0) | (df['time_to_surgery_hrs'] > 10000), 'time_to_surgery_hrs'] = np.nan


    return df


# ---------- KNN imputation for continuous variables ----------
def knn_impute_continuous(df, n_neighbors=5):
    """
    Use KNN imputation for continuous variables with missing values.
    This provides more sophisticated imputation than simple mean/median filling.
    Also tracks which rows had imputed values for data quality assessment.
    """
    # Identify continuous variables that may have missing values
    continuous_vars = [
        'age',
        'los_hospital_days',
        'los_acute_ward_days', 
        'time_to_surgery_hrs',
        'transfer_to_operating_days'
    ]
    
    # Core clinical variables to track for data quality (excludes transfer_to_operating_days)
    # Transfer is expected to be missing for most patients (not transferred)
    core_clinical_vars = [
        'age',
        'los_hospital_days',
        'time_to_surgery_hrs'
    ]
    
    # Filter to only columns that exist in the dataframe
    continuous_vars = [col for col in continuous_vars if col in df.columns]
    core_clinical_vars = [col for col in core_clinical_vars if col in df.columns]
    
    if not continuous_vars:
        print("No continuous variables found for KNN imputation.")
        return df
    
    # Check which columns have missing values
    cols_with_missing = [col for col in continuous_vars if df[col].isna().any()]
    
    if not cols_with_missing:
        print("No missing values found in continuous variables.")
        return df
    
    print(f"Applying KNN imputation to: {', '.join(cols_with_missing)}")
    print(f"Missing counts before imputation:")
    
    # Track which rows had missing values BEFORE imputation
    imputation_map = {}
    for col in cols_with_missing:
        n_missing = df[col].isna().sum()
        print(f"  {col}: {n_missing} missing values")
        # Create boolean mask: True where originally NaN
        imputation_map[col] = df[col].isna().copy()
    
    # Create KNN imputer
    imputer = KNNImputer(n_neighbors=n_neighbors, weights='distance')
    
    # Apply imputation only to continuous variables
    df[continuous_vars] = imputer.fit_transform(df[continuous_vars])
    
    print(f"KNN imputation complete with {n_neighbors} neighbors.")
    print(f"Missing counts after imputation:")
    for col in cols_with_missing:
        print(f"  {col}: {df[col].isna().sum()} missing values")
    
    # Track imputation ONLY for core clinical variables (not transfer-related)
    # This gives a more meaningful data quality metric
    core_imputation_map = {col: imputation_map[col] for col in core_clinical_vars if col in imputation_map}
    
    if core_imputation_map:
        # Sum across CORE clinical fields only
        core_imputation_df = pd.DataFrame(core_imputation_map)
        df['n_imputed_fields'] = core_imputation_df.sum(axis=1).astype(int)
        
        # Summary statistics for core fields
        patients_with_imputation = (df['n_imputed_fields'] > 0).sum()
        total_patients = len(df)
        imputation_rate = round(patients_with_imputation / total_patients * 100, 1)
        
        print(f"\nCore Clinical Fields Imputation Summary (age, LOS, time_to_surgery):")
        print(f"  Patients with imputed values: {patients_with_imputation} ({imputation_rate}%)")
        print(f"  Core fields tracked: {len(core_imputation_map)}")
        
        # Show breakdown by field for core variables
        for col in core_clinical_vars:
            if col in imputation_map:
                n_imputed = imputation_map[col].sum()
                rate = round(n_imputed / total_patients * 100, 1)
                print(f"    {col}: {n_imputed} imputed ({rate}%)")
        
        # Save individual field flags for detailed per-cohort analysis
        for col in core_clinical_vars:
            if col in imputation_map:
                df[f'{col}_was_missing'] = imputation_map[col].astype(int)
    else:
        df['n_imputed_fields'] = 0
    
    return df


# ---------- other fill-ins ----------
def fill_defaults(df):
    # For mapped categorical columns we've already replaced missing with "Not recorded"
    # For boolean-like where appropriate, convert to bool
    # Example: ons (Oral nutritional supplements) is Yes/No already mapped above to text.
    # Ensure hospital identifier exists as string
    if 'ahos_code' in df.columns:
        df['ahos_code'] = df['ahos_code'].astype(str).fillna("Unknown")
    # gerimed may have numeric codes -> mapping above set Not recorded if missing
    return df


# ---------- main pipeline ----------
def main():
    print("Starting local cleaning pipeline...")
    df = safe_read_csv(INPUT_CSV)
    backup_original(df)
    overview(df, "Before cleaning")


    # 1) Apply value-label mappings
    df = apply_mappings(df)
    print("Applied label mappings.")


    # 2) Build datetime-like columns for each prefix you provided
    prefixes = [
        "tarrdatetime", "arrdatetime", "depdatetime", "admdatetimeop",
        "sdatetime", "gdate", "wdisch", "hdisch"
    ]
    for p in prefixes:
        df = build_datetime_from_parts(df, p)
    print("Constructed datetime-like columns (suffix _dt).")


    # 3) Derive durations (LOS, time to surgery, transfer diff)
    df = derive_durations(df)
    print("Derived duration columns.")


    # 4) Clean numeric and bounds
    df = numeric_and_bounds(df)
    print("Cleaned numeric ranges and bounds.")

    # 5) Apply KNN imputation for continuous variables
    df = knn_impute_continuous(df, n_neighbors=5)
    print("Applied KNN imputation for continuous variables.")

    # 6) Fill defaults and minor fixes
    df = fill_defaults(df)
    print("Filled defaults for misc columns.")

    # 7) Final overview and save
    overview(df, "After cleaning")
    df.to_csv(OUTPUT_CSV, index=False)
    print(f">>> Cleaned file saved locally as: {OUTPUT_CSV}")
    print("Done. Keep this file local. Do NOT upload confidential data anywhere.")


if __name__ == "__main__":
    main()

