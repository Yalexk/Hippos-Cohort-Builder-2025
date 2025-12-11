import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for server-side rendering
import matplotlib.pyplot as plt
import base64
from io import BytesIO

def compute_fwalk2(df: pd.DataFrame):
    """
    Compute counts for walking ability at 120 days (fwalk2).
    Excludes 'Not recorded' or 'Not relevant' entries from the total count
    for percentage calculations.
    """
    if 'fwalk2' not in df.columns:
        return {}

    # Define the valid categories we want to track
    # Note: We check for both "Walks without aids" (user prompt) and 
    # "Walks without walking aids" (standard schema) to be safe.
    valid_categories = [
        'Walks without walking aids', 
        'Walks without aids',
        'Walks with either a stick or crutch', 
        'Walks with two aids or frame', 
        'Uses a wheelchair / bed bound'
    ]

    # Filter data to only include the specific categories (effectively excluding "Not recorded", "Not relevant", etc.)
    df_clean = df[df['fwalk2'].isin(valid_categories)].copy()
    
    # Normalize 'Walks without walking aids' if there are naming variations
    df_clean['fwalk2'] = df_clean['fwalk2'].replace('Walks without walking aids', 'Walks without aids')

    counts = df_clean['fwalk2'].value_counts()
    
    # Calculate the valid total (excluding Not recorded/Not relevant)
    valid_total = len(df_clean)

    # Return raw counts and the valid total for context if needed
    stats = {
        'counts': {
            'Walks without aids': int(counts.get('Walks without aids', 0)),
            'Walks with either a stick or crutch': int(counts.get('Walks with either a stick or crutch', 0)),
            'Walks with two aids or frame': int(counts.get('Walks with two aids or frame', 0)),
            'Uses a wheelchair / bed bound': int(counts.get('Uses a wheelchair / bed bound', 0))
        },
        'valid_total': valid_total
    }

    return stats

def generate_fwalk2_chart(stats: dict):
    """
    Generate a pie chart for walking ability at 120 days.
    Returns a data URI (base64 PNG) or None if insufficient data.
    """
    counts = stats.get('counts', {})
    valid_total = stats.get('valid_total', 0)
    
    if valid_total == 0:
        return None

    labels = list(counts.keys())
    sizes = list(counts.values())
    
    # Filter out zero values
    clean_data = [(l, s) for l, s in zip(labels, sizes) if s > 0]
    
    if not clean_data:
        return None
        
    labels, sizes = zip(*clean_data)
    
    # Create simpler labels for the chart key to save space
    short_labels = {
        'Walks without aids': 'Unaided',
        'Walks with either a stick or crutch': 'Stick/Crutch',
        'Walks with two aids or frame': '2 Aids/Frame',
        'Uses a wheelchair / bed bound': 'Wheelchair/Bed'
    }
    display_labels = [short_labels.get(l, l) for l in labels]

    fig, ax = plt.subplots(figsize=(8, 6))
    
    # Define colors
    colors = ['#50c878', '#4a90e2', '#f5a623', '#e24a4a']
    
    wedges, texts, autotexts = ax.pie(
        sizes, 
        labels=display_labels, 
        autopct='%1.1f%%',
        startangle=90,
        colors=colors[:len(sizes)],
        textprops=dict(color="black")
    )
    
    plt.setp(texts, size=10, weight="bold")
    plt.setp(autotexts, size=9, weight="bold", color="white")
    
    ax.set_title('Walking Ability After 120 Days\n(Excluding Not Recorded)', fontsize=13, fontweight='bold', pad=20)
    
    ax.axis('equal')  

    plt.tight_layout()
    buf = BytesIO()
    plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
    buf.seek(0)
    img64 = base64.b64encode(buf.read()).decode('utf-8')
    plt.close(fig)

    return f"data:image/png;base64,{img64}"