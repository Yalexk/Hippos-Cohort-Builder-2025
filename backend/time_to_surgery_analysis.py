import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import base64
from io import BytesIO

def compute_time_to_surgery(df: pd.DataFrame):
    """
    Extracts the raw time_to_surgery_hrs data for the box plot.
    Filters out unrealistic values (< 0 or > 336 hours).
    Calculates summary statistics for display.
    """
    stats = {}
    
    if 'time_to_surgery_hrs' in df.columns:
        # Drop NaNs first
        clean_data = df['time_to_surgery_hrs'].dropna()
        
        # FILTER: Keep only values between 0 and 336 hours (14 days)
        clean_data = clean_data[(clean_data >= 0) & (clean_data <= 336)]
        
        stats['raw_data'] = clean_data.tolist()
        
        # Calculate summary stats for text display
        if not clean_data.empty:
            stats['mean'] = round(clean_data.mean(), 1)
            stats['median'] = round(clean_data.median(), 1)
            stats['min'] = round(clean_data.min(), 1)
            stats['max'] = round(clean_data.max(), 1)
            stats['count'] = len(clean_data)
        else:
            stats['raw_data'] = []
            stats['mean'] = 0
            stats['median'] = 0
            stats['max'] = 0
    else:
        stats['raw_data'] = []
        
    return stats

def generate_time_to_surgery_chart(stats: dict):
    """
    Generate a Box Plot for Time to Surgery (Hours).
    """
    data = stats.get('raw_data', [])
    
    if not data:
        return None

    # Create figure
    fig, ax = plt.subplots(figsize=(8, 6))
    
    # Create boxplot
    # vert=True (vertical), patch_artist=True (fill color)
    bp = ax.boxplot(data, vert=True, patch_artist=True, labels=['Time to Surgery'])
    
    # Customize colors
    for patch in bp['boxes']:
        patch.set_facecolor('#e24a4a') # Reddish tone
        patch.set_alpha(0.6)
        
    for median in bp['medians']:
        median.set(color='black', linewidth=1.5)

    # Formatting
    ax.set_ylabel('Hours', fontsize=10, fontweight='bold')
    ax.set_title('Distribution of Time to Surgery', fontsize=12, fontweight='bold', pad=15)
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    
    # Add summary text annotation
    summary_text = (
        f"Mean: {stats.get('mean', 0)} hrs\n"
        f"Median: {stats.get('median', 0)} hrs\n"
        f"Max: {stats.get('max', 0)} hrs"
    )
    
    # Position text in top right
    ax.text(0.95, 0.95, summary_text, transform=ax.transAxes, 
            verticalalignment='top', horizontalalignment='right',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
            
    # Add caption about the filter
    ax.text(0.5, -0.1, "Note: Values < 0 hours and > 336 hours (2 weeks) are excluded.", 
            transform=ax.transAxes, ha='center', fontsize=8, color='#666')

    plt.tight_layout()
    
    # Save to Base64
    buf = BytesIO()
    plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
    buf.seek(0)
    img64 = base64.b64encode(buf.read()).decode('utf-8')
    plt.close(fig)

    return f"data:image/png;base64,{img64}"