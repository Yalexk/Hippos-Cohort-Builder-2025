import pandas as pd
from mortality_analysis import compute_mortality, generate_mortality_chart
from residence_analysis import compute_residence, generate_residence_chart
from residence_transition_analysis import compute_residence_transition, generate_residence_transition_chart
from fwalk2_analysis import compute_fwalk2, generate_fwalk2_chart
from afracture_analysis import compute_afracture, generate_afracture_chart
from timelines_analysis import compute_timelines, generate_timelines_chart
from time_to_surgery_analysis import compute_time_to_surgery, generate_time_to_surgery_chart
# IMPORT NEW MODULE
from age_analysis import compute_age, generate_age_chart

# EXPANDABLE CONFIGURATION
CHART_BLOCKING_RULES = {
    'residence_chart': ['uresidence'],
    'fwalk2_chart': ['fwalk2'],
    'afracture_chart': ['afracture'],
    'timelines_chart': [],
    'time_to_surgery_chart': [],
    'age_chart': [],
}

def should_generate_chart(chart_key, applied_filters):
    if applied_filters is None:
        return True
    blocking_keys = CHART_BLOCKING_RULES.get(chart_key, [])
    for key in blocking_keys:
        if key in applied_filters and applied_filters[key]:
            return False
    return True

def compute_enhanced_metrics(df, mortality_stats):
    """
    Compute enhanced metrics for research adequacy assessment.
    Returns metrics including:
    - Number of hospitals
    - Date range
    """
    import numpy as np
    from datetime import datetime
    
    metrics = {}
    
    # Number of Hospitals
    if 'ahos_code' in df.columns:
        unique_hospitals = df['ahos_code'].dropna().nunique()
        metrics['n_hospitals'] = int(unique_hospitals)
    else:
        metrics['n_hospitals'] = 0
    
    # Date Range
    # Try to find admission date column
    date_col = None
    for col in ['arrdatetime_dt', 'admdatetimeop_dt', 'tarrdatetime_dt']:
        if col in df.columns:
            date_col = col
            break
    
    if date_col:
        # Convert to datetime if not already
        dates = pd.to_datetime(df[date_col], errors='coerce').dropna()
        
        if len(dates) > 0:
            earliest = dates.min()
            latest = dates.max()
            
            metrics['earliest_admission'] = earliest.strftime('%Y-%m-%d')
            metrics['latest_admission'] = latest.strftime('%Y-%m-%d')
            
            # Calculate time span in years
            time_span_days = (latest - earliest).days
            time_span_years = round(time_span_days / 365.25, 1)
            metrics['time_span_years'] = time_span_years
            
            metrics['date_range'] = f"{earliest.strftime('%b %Y')} - {latest.strftime('%b %Y')}"
        else:
            metrics['earliest_admission'] = 'Unknown'
            metrics['latest_admission'] = 'Unknown'
            metrics['time_span_years'] = 0
            metrics['date_range'] = 'Unknown'
    else:
        metrics['earliest_admission'] = 'Unknown'
        metrics['latest_admission'] = 'Unknown'
        metrics['time_span_years'] = 0
        metrics['date_range'] = 'Unknown'
    
    # Gender distribution
    if 'sex' in df.columns:
        sex_counts = df['sex'].value_counts()
        total_patients = len(df)
        
        # Get counts for each gender
        male_count = sex_counts.get('Male', 0)
        female_count = sex_counts.get('Female', 0)
        other_count = sex_counts.get('Intersex or indeterminate', 0)
        
        # Calculate percentages
        male_pct = round(male_count / total_patients * 100, 1) if total_patients > 0 else 0
        female_pct = round(female_count / total_patients * 100, 1) if total_patients > 0 else 0
        
        metrics['gender_distribution'] = {
            'male': int(male_count),
            'female': int(female_count),
            'other': int(other_count),
            'male_percent': male_pct,
            'female_percent': female_pct,
            'ratio': f"M:{male_pct}% F:{female_pct}%"
        }
    
    # Imputation tracking (row-level and field-level breakdown)
    if 'n_imputed_fields' in df.columns:
        # Count patients with ANY imputed value
        patients_with_imputation = (df['n_imputed_fields'] > 0).sum()
        total_patients = len(df)
        
        metrics['patients_with_imputation'] = int(patients_with_imputation)
        metrics['imputation_rate'] = round(patients_with_imputation / total_patients * 100, 1) if total_patients > 0 else 0
        
        # Average number of imputed fields per patient (among those with imputation)
        if patients_with_imputation > 0:
            avg_imputed_fields = df[df['n_imputed_fields'] > 0]['n_imputed_fields'].mean()
            metrics['avg_imputed_fields'] = round(avg_imputed_fields, 1)
        else:
            metrics['avg_imputed_fields'] = 0
        
        # Per-field breakdown for core clinical variables
        # Check if individual imputation flag columns exist
        core_fields = ['age', 'los_hospital_days', 'time_to_surgery_hrs']
        imputation_breakdown = {}
        
        for field in core_fields:
            flag_col = f'{field}_was_missing'
            if flag_col in df.columns:
                n_imputed = df[flag_col].sum()
                imputation_breakdown[field] = {
                    'count': int(n_imputed),
                    'percent': round(n_imputed / total_patients * 100, 1) if total_patients > 0 else 0
                }
        
        if imputation_breakdown:
            metrics['imputation_by_field'] = imputation_breakdown
        
    else:
        metrics['patients_with_imputation'] = 0
        metrics['imputation_rate'] = 0
        metrics['avg_imputed_fields'] = 0
    
    return metrics

def analyse_cohort(cohort_id, cohort_csv_path, filters=None):
    try:
        df = pd.read_csv(cohort_csv_path)
        
        results = {
            'cohort_id': cohort_id,
            'total_patients': len(df)
        }
        
        # 1. Mortality Analysis
        mortality_stats = compute_mortality(df)
        results['mortality'] = mortality_stats
        if should_generate_chart('mortality_chart', filters):
            results['mortality_chart'] = generate_mortality_chart(mortality_stats)
        else:
            results['mortality_chart'] = None

        # 2. Walking Ability
        fwalk2_stats = compute_fwalk2(df)
        results['fwalk2'] = fwalk2_stats
        if should_generate_chart('fwalk2_chart', filters):
            results['fwalk2_chart'] = generate_fwalk2_chart(fwalk2_stats)
        else:
            results['fwalk2_chart'] = None
            
        # 3. Fracture Type
        afracture_stats = compute_afracture(df)
        results['afracture'] = afracture_stats
        if should_generate_chart('afracture_chart', filters):
            results['afracture_chart'] = generate_afracture_chart(afracture_stats)
        else:
            results['afracture_chart'] = None

        # 4. Residence
        residence_stats = compute_residence(df)
        results['residence'] = residence_stats
        if should_generate_chart('residence_chart', filters):
            results['residence_chart'] = generate_residence_chart(residence_stats)
        else:
            results['residence_chart'] = None

        # 5. Residence Transition
        residence_transition_stats = compute_residence_transition(df)
        results['residence_transition'] = residence_transition_stats
        if should_generate_chart('residence_transition_chart', filters):
            results['residence_transition_chart'] = generate_residence_transition_chart(residence_transition_stats)
        else:
            results['residence_transition_chart'] = None

        # 6. Length of Stay Analysis
        timelines_stats = compute_timelines(df)
        results['timelines'] = timelines_stats
        if should_generate_chart('timelines_chart', filters):
            results['timelines_chart'] = generate_timelines_chart(timelines_stats)
        else:
            results['timelines_chart'] = None

        # 7. Time to Surgery Analysis
        surgery_stats = compute_time_to_surgery(df)
        results['time_to_surgery'] = surgery_stats
        if should_generate_chart('time_to_surgery_chart', filters):
            results['time_to_surgery_chart'] = generate_time_to_surgery_chart(surgery_stats)
        else:
            results['time_to_surgery_chart'] = None

        # 8. Age Analysis (NEW)
        age_stats = compute_age(df)
        results['age'] = age_stats
        if should_generate_chart('age_chart', filters):
            results['age_chart'] = generate_age_chart(age_stats)
        else:
            results['age_chart'] = None

        if 'total_patients' in mortality_stats:
            results['total_patients'] = mortality_stats['total_patients']

        # Add enhanced metrics for research adequacy assessment
        results['enhanced_metrics'] = compute_enhanced_metrics(df, mortality_stats)

        return results
    except Exception as e:
        print(f"Error analysing cohort {cohort_id}: {str(e)}")
        raise e

if __name__ == "__main__":
    print("Cohort analysis module loaded")