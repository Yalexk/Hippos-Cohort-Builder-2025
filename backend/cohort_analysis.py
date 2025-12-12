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

        return results
    except Exception as e:
        print(f"Error analysing cohort {cohort_id}: {str(e)}")
        raise e

if __name__ == "__main__":
    print("Cohort analysis module loaded")