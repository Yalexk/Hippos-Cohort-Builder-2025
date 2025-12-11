import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for server-side rendering
import matplotlib.pyplot as plt
import base64
from io import BytesIO

def compute_residence(df: pd.DataFrame):
    """
    Compute counts for pre-admission residence status (uresidence).
    Merges 'Not recorded' into 'Other'.
    Returns a dictionary of counts.
    """
    if 'uresidence' not in df.columns:
        return {}

    # Create a copy to avoid SettingWithCopy warnings on the original df
    res_data = df['uresidence'].copy()
    
    # Standardize/Merge values
    # We want 3 categories: Private residence, Residential aged care facility, Other
    res_data = res_data.replace('Not recorded', 'Other')
    
    # Handle any potential nulls as Other
    res_data = res_data.fillna('Other')

    counts = res_data.value_counts()
    
    # Ensure all keys exist for consistency, even if 0
    stats = {
        'Private residence': int(counts.get('Private residence', 0)),
        'Residential aged care facility': int(counts.get('Residential aged care facility', 0)),
        'Other': int(counts.get('Other', 0))
    }
    
    # If there were other categories in the data not accounted for, add them to Other
    # (This ensures the chart represents 100% of the cohort)
    known_sum = sum(stats.values())
    total_rows = len(df)
    if known_sum < total_rows:
        stats['Other'] += (total_rows - known_sum)

    return stats

def generate_residence_chart(stats: dict):
    """
    Generate a pie chart for residence status.
    Returns a data URI (base64 PNG) or None if insufficient data.
    """
    labels = list(stats.keys())
    sizes = list(stats.values())
    
    # Filter out zero values to avoid cluttering the chart
    clean_data = [(l, s) for l, s in zip(labels, sizes) if s > 0]
    
    if not clean_data:
        return None
        
    labels, sizes = zip(*clean_data)
    
    # Shorten long labels for the chart display
    display_labels = [l.replace('Residential aged care facility', 'RACF') for l in labels]

    fig, ax = plt.subplots(figsize=(8, 6))
    
    # Define colors (Safe pastel palette)
    colors = ['#4a90e2', '#50c878', '#e24a4a', '#f5a623']
    
    wedges, texts = ax.pie(
        sizes, 
        labels=None,
        startangle=90,
        colors=colors[:len(sizes)],
        textprops=dict(color="black")
    )
    
    ax.set_title('Pre-Admission Residence Status', fontsize=13, fontweight='bold', pad=20)
    
    ax.axis('equal')
    
    # Add legend on the right
    ax.legend(
        wedges,
        display_labels,
        title="Residence Type",
        loc="center left",
        bbox_to_anchor=(1, 0.5),
        fontsize=10
    )  

    plt.tight_layout()
    buf = BytesIO()
    plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
    buf.seek(0)
    img64 = base64.b64encode(buf.read()).decode('utf-8')
    plt.close(fig)

    return f"data:image/png;base64,{img64}"