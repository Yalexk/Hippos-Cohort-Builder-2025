import pandas as pd
import json
import os
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import base64
from io import BytesIO

def generate_mortality_chart(mortality_30, mortality_90, mortality_120, mortality_365, total_patients):
    """
    Generate a bar chart showing mortality rates across different time frames
    Returns base64 encoded image
    """
    try:
        # Prepare data
        timeframes = []
        alive_counts = []
        deceased_counts = []
        
        # 30-day
        if mortality_30:
            timeframes.append('30-day')
            deceased_counts.append(mortality_30['count'])
            alive_counts.append(total_patients - mortality_30['count'])
        
        # 90-day
        if mortality_90:
            timeframes.append('90-day')
            deceased_counts.append(mortality_90['count'])
            alive_counts.append(total_patients - mortality_90['count'])
        
        # 120-day
        if mortality_120:
            timeframes.append('120-day')
            deceased_counts.append(mortality_120['count'])
            alive_counts.append(total_patients - mortality_120['count'])
        
        # 365-day
        if mortality_365:
            timeframes.append('365-day')
            deceased_counts.append(mortality_365['count'])
            alive_counts.append(total_patients - mortality_365['count'])
        
        if not timeframes:
            return None
        
        # Create figure
        fig, ax = plt.subplots(figsize=(10, 6))
        
        x = range(len(timeframes))
        width = 0.35
        
        # Create bars
        bars1 = ax.bar([i - width/2 for i in x], alive_counts, width, label='Alive', color='#4a90e2')
        bars2 = ax.bar([i + width/2 for i in x], deceased_counts, width, label='Deceased', color='#e24a4a')
        
        # Customize chart
        ax.set_xlabel('Time Frame', fontsize=11, fontweight='bold')
        ax.set_ylabel('Number of Patients', fontsize=11, fontweight='bold')
        ax.set_title('Mortality Status Across Time Frames', fontsize=13, fontweight='bold', pad=20)
        ax.set_xticks(x)
        ax.set_xticklabels(timeframes)
        ax.legend()
        ax.grid(axis='y', alpha=0.3, linestyle='--')
        
        # Add value labels on bars
        def add_labels(bars):
            for bar in bars:
                height = bar.get_height()
                if height > 0:
                    ax.text(bar.get_x() + bar.get_width()/2., height,
                           f'{int(height)}',
                           ha='center', va='bottom', fontsize=9)
        
        add_labels(bars1)
        add_labels(bars2)
        
        plt.tight_layout()
        
        # Convert to base64
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
        plt.close(fig)
        
        return f"data:image/png;base64,{image_base64}"
        
    except Exception as e:
        print(f"Error generating mortality chart: {str(e)}")
        return None

def analyse_cohort(cohort_id, cohort_csv_path):
    """
    Analyse a cohort and return statistics
    
    Args:
        cohort_id: The unique identifier for the cohort
        cohort_csv_path: Path to the cohort's CSV file
    
    Returns:
        Dictionary containing analysis results
    """
    try:
        # Load the cohort data
        df = pd.read_csv(cohort_csv_path)
        
        # Basic statistics
        total_patients = len(df)
        
        # Mortality analysis (30-day)
        mortality_30_day = None
        if 'mort30d' in df.columns:
            deceased_30 = (df['mort30d'] == 'Deceased').sum()
            mortality_30_day = {
                'count': int(deceased_30),
                'rate': float(deceased_30 / total_patients * 100) if total_patients > 0 else 0
            }
        
        # 90-day mortality
        mortality_90_day = None
        if 'mort90d' in df.columns:
            deceased_90 = (df['mort90d'] == 'Deceased').sum()
            mortality_90_day = {
                'count': int(deceased_90),
                'rate': float(deceased_90 / total_patients * 100) if total_patients > 0 else 0
            }
        
        # 120-day mortality
        mortality_120_day = None
        if 'mort120d' in df.columns:
            deceased_120 = (df['mort120d'] == 'Deceased').sum()
            mortality_120_day = {
                'count': int(deceased_120),
                'rate': float(deceased_120 / total_patients * 100) if total_patients > 0 else 0
            }
        
        # 365-day mortality
        mortality_365_day = None
        if 'mort365d' in df.columns:
            deceased_365 = (df['mort365d'] == 'Deceased').sum()
            mortality_365_day = {
                'count': int(deceased_365),
                'rate': float(deceased_365 / total_patients * 100) if total_patients > 0 else 0
            }
        
        # Generate mortality chart
        mortality_chart = generate_mortality_chart(
            mortality_30_day,
            mortality_90_day,
            mortality_120_day,
            mortality_365_day,
            total_patients
        )

        
        # Compile results
        analysis_results = {
            'cohort_id': cohort_id,
            'total_patients': total_patients,
            'mortality': {
                '30_day': mortality_30_day,
                '90_day': mortality_90_day,
                '120_day': mortality_120_day,
                '365_day': mortality_365_day
            },
            'mortality_chart': mortality_chart
        }
        
        return analysis_results
        
    except Exception as e:
        print(f"Error analysing cohort {cohort_id}: {str(e)}")
        raise e

if __name__ == "__main__":
    # Example usage
    print("Cohort analysis module loaded")
