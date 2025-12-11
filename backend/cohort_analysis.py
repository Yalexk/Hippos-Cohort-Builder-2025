import pandas as pd
from mortality_analysis import compute_mortality, generate_mortality_chart

# mortality chart generation is now delegated to mortality_analysis.generate_mortality_chart

def analyse_cohort(cohort_id, cohort_csv_path):
    """
    Analyse a cohort and return statistics. Delegates mortality computation and
    chart generation to mortality_analysis for modular design.
    """
    try:
        df = pd.read_csv(cohort_csv_path)
        mortality_stats = compute_mortality(df)
        mortality_chart = generate_mortality_chart(mortality_stats)

        analysis_results = {
            'cohort_id': cohort_id,
            'total_patients': mortality_stats.get('total_patients', len(df)),
            'mortality': mortality_stats,
            'mortality_chart': mortality_chart
        }
        return analysis_results
    except Exception as e:
        print(f"Error analysing cohort {cohort_id}: {str(e)}")
        raise e

if __name__ == "__main__":
    # Example usage
    print("Cohort analysis module loaded")
