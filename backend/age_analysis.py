import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import base64
from io import BytesIO

def compute_age(df: pd.DataFrame):
    """
    Extracts the raw age data for the box plot.
    Calculates summary statistics for display.
    """
    stats = {}
    
    if 'age' in df.columns:
        # Drop NaNs
        clean_data = df['age'].dropna()
        stats['raw_data'] = clean_data.tolist()
        
        # Calculate summary stats for text display
        if not clean_data.empty:
            stats['mean'] = round(clean_data.mean(), 1)
            stats['median'] = round(clean_data.median(), 1)
            stats['min'] = int(clean_data.min())
            stats['max'] = int(clean_data.max())
            stats['count'] = len(clean_data)
        else:
            stats['raw_data'] = []
    else:
        stats['raw_data'] = []
        
    return stats

def generate_age_chart(stats: dict):
    """
    Generate a Box Plot for Patient Age.
    """
    data = stats.get('raw_data', [])
    
    if not data:
        return None

    # Create figure
    fig, ax = plt.subplots(figsize=(8, 6))
    
    # Create boxplot
    # vert=True (vertical), patch_artist=True (fill color)
    bp = ax.boxplot(data, vert=True, patch_artist=True, labels=['Patient Age'])
    
    # Customize colors - using a Blue/Purple tone for demographics
    for patch in bp['boxes']:
        patch.set_facecolor('#646cff') 
        patch.set_alpha(0.6)
        
    for median in bp['medians']:
        median.set(color='black', linewidth=1.5)

    # Formatting
    ax.set_ylabel('Age (Years)', fontsize=10, fontweight='bold')
    ax.set_title('Distribution of Patient Age', fontsize=12, fontweight='bold', pad=15)
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    
    # Add summary text annotation
    summary_text = (
        f"Mean: {stats.get('mean', 0)} years\n"
        f"Median: {stats.get('median', 0)} years\n"
        f"Min: {stats.get('min', 0)} years\n"
        f"Max: {stats.get('max', 0)} years"
    )
    
    # Position text in top right
    ax.text(0.95, 0.95, summary_text, transform=ax.transAxes, 
            verticalalignment='top', horizontalalignment='right',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

    plt.tight_layout()
    
    # Save to Base64
    buf = BytesIO()
    plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
    buf.seek(0)
    img64 = base64.b64encode(buf.read()).decode('utf-8')
    plt.close(fig)

    return f"data:image/png;base64,{img64}"