import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for server-side rendering
import matplotlib.pyplot as plt
import base64
from io import BytesIO

def compute_afracture(df: pd.DataFrame):
    """
    Compute counts for fracture types.
    Focuses on:
    1. Not a pathological or atypical fracture
    2. Pathological fracture
    3. Atypical fracture
    """
    if 'afracture' not in df.columns:
        return {}

    counts = df['afracture'].value_counts()
    
    # We allow for slight variation in the "Not a pathological..." string 
    # to ensure compatibility between App.jsx filters and the provided data description
    not_path_count = counts.get('Not a pathological or atypical fracture', 0)
    if not_path_count == 0:
        not_path_count = counts.get('Not pathological or atypical fracture', 0)

    stats = {
        'Not a pathological or atypical fracture': int(not_path_count),
        'Pathological fracture': int(counts.get('Pathological fracture', 0)),
        'Atypical fracture': int(counts.get('Atypical fracture', 0))
    }

    return stats

def generate_afracture_chart(stats: dict):
    """
    Generate a pie chart for atypical fracture status.
    Returns a data URI (base64 PNG) or None if insufficient data.
    """
    # Filter out zero values
    labels = list(stats.keys())
    sizes = list(stats.values())
    
    clean_data = [(l, s) for l, s in zip(labels, sizes) if s > 0]
    
    if not clean_data:
        return None
        
    labels, sizes = zip(*clean_data)
    
    # Shorten labels for better chart display
    display_labels = []
    for l in labels:
        if 'Not a pathological' in l or 'Not pathological' in l:
            display_labels.append('Standard Fracture') # Shortened for readability
        else:
            display_labels.append(l)

    fig, ax = plt.subplots(figsize=(8, 6))
    
    # Define colors
    # Standard: Blue, Pathological: Red, Atypical: Orange
    colors = ['#4a90e2', '#e24a4a', '#f5a623']
    
    wedges, texts, autotexts = ax.pie(
        sizes, 
        labels=None, 
        autopct='%1.1f%%',
        startangle=90,
        colors=colors[:len(sizes)],
        textprops=dict(color="black")
    )
    
    ax.set_title('Fracture Classification', fontsize=13, fontweight='bold', pad=20)
    
    ax.axis('equal')  

    # Add legend on the right
    ax.legend(
        wedges,
        display_labels,
        title="Fracture Type",
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