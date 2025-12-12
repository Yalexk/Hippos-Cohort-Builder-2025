import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import base64
from io import BytesIO

def compute_timelines(df: pd.DataFrame):
    """
    Compute average Length of Stay (LoS) for Hospital and Acute Ward.
    Rounds to 1 decimal place (standard rounding).
    """
    stats = {}
    
    # Calculate means, ignoring NaNs automatically
    if 'los_hospital_days' in df.columns:
        stats['avg_hospital_days'] = round(df['los_hospital_days'].mean(), 1)
    else:
        stats['avg_hospital_days'] = 0.0

    if 'los_acute_ward_days' in df.columns:
        stats['avg_acute_days'] = round(df['los_acute_ward_days'].mean(), 1)
    else:
        stats['avg_acute_days'] = 0.0

    return stats

def generate_timelines_chart(stats: dict):
    """
    Generate a bar chart for Hospital and Acute Ward stay (Days).
    """
    # Extract data for the bar chart
    labels = ['Total Hospital Stay', 'Acute Ward Stay']
    values = [stats.get('avg_hospital_days', 0), stats.get('avg_acute_days', 0)]
    
    if sum(values) == 0:
        return None

    # Create figure
    fig, ax = plt.subplots(figsize=(8, 6))

    # Define colors (Blue for Hospital, Green/Teal for Acute)
    colors = ['#4a90e2', '#50c878']
    
    # Plot Vertical Bars
    bars = ax.bar(labels, values, color=colors, width=0.5)
    
    # Formatting
    ax.set_ylabel('Average Duration (Days)', fontsize=10, fontweight='bold')
    ax.set_title('Average Length of Stay', fontsize=12, fontweight='bold', pad=15)
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    
    # Add value labels on top of bars
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{height} days',
                ha='center', va='bottom', fontsize=10, fontweight='bold')

    plt.tight_layout()
    
    # Save to Base64
    buf = BytesIO()
    plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
    buf.seek(0)
    img64 = base64.b64encode(buf.read()).decode('utf-8')
    plt.close(fig)

    return f"data:image/png;base64,{img64}"