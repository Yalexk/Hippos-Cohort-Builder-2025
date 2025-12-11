import pandas as pd
from mortality_analysis import compute_mortality, generate_mortality_chart
from residence_analysis import compute_residence, generate_residence_chart
from fwalk2_analysis import compute_fwalk2, generate_fwalk2_chart

# EXPANDABLE CONFIGURATION
CHART_BLOCKING_RULES = {
    'residence_chart': ['uresidence'],
    'fwalk2_chart': ['fwalk2'],
}

def should_generate_chart(chart_key, applied_filters):
    """
    Checks if a chart should be generated based on applied filters.
    Returns True if the chart should be displayed, False if it should be hidden.
    """
    if applied_filters is None:
        return True
        
    blocking_keys = CHART_BLOCKING_RULES.get(chart_key, [])
    
    # If any blocking key is present in the filters and has values, hide the chart
    for key in blocking_keys:
        if key in applied_filters and applied_filters[key]:
            return False
            
    return True

def analyse_cohort(cohort_id, cohort_csv_path, filters=None):
    """
    Analyse a cohort and return statistics. Delegates computation and
    chart generation to specific analysis modules.
    """
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

        # 2. Walking Ability (120 Days) Analysis - NEW
        fwalk2_stats = compute_fwalk2(df)
        results['fwalk2'] = fwalk2_stats

        if should_generate_chart('fwalk2_chart', filters):
            results['fwalk2_chart'] = generate_fwalk2_chart(fwalk2_stats)
        else:
            results['fwalk2_chart'] = None

        # 3. Residence Analysis
        residence_stats = compute_residence(df)
        results['residence'] = residence_stats
        
        if should_generate_chart('residence_chart', filters):
            results['residence_chart'] = generate_residence_chart(residence_stats)
        else:
            results['residence_chart'] = None

        # Add total patients to top level
        if 'total_patients' in mortality_stats:
            results['total_patients'] = mortality_stats['total_patients']

        return results
    except Exception as e:
        print(f"Error analysing cohort {cohort_id}: {str(e)}")
        raise e

if __name__ == "__main__":
    print("Cohort analysis module loaded")