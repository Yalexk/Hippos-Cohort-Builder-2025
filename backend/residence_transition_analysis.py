import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for server-side rendering
import matplotlib.pyplot as plt
import base64
from io import BytesIO

def compute_residence_transition(df: pd.DataFrame):
    """
    Compute residence transitions from admission (uresidence) to discharge (dresidence).
    Tracks:
    - Stayed home → stayed home
    - Home → RACF (new RACF entries)
    - RACF → RACF (stayed in RACF)
    - RACF → Home (returned home)
    - Other transitions
    """
    if 'uresidence' not in df.columns or 'dresidence' not in df.columns:
        return {}

    # Create a working dataframe with both columns
    transition_df = df[['uresidence', 'dresidence']].copy()
    
    # Clean up the data - replace 'Not recorded' and nulls with 'Unknown'
    transition_df['uresidence'] = transition_df['uresidence'].fillna('Unknown').replace('Not recorded', 'Unknown')
    transition_df['dresidence'] = transition_df['dresidence'].fillna('Unknown').replace('Not recorded', 'Unknown')
    
    # Simplify categories for analysis
    def categorize_residence(value):
        if pd.isna(value) or value == 'Unknown':
            return 'Unknown'
        elif 'Residential aged care facility' in str(value) or 'RACF' in str(value):
            return 'RACF'
        elif 'Private residence' in str(value) or 'Home' in str(value):
            return 'Home'
        else:
            return 'Other'
    
    transition_df['uresidence_cat'] = transition_df['uresidence'].apply(categorize_residence)
    transition_df['dresidence_cat'] = transition_df['dresidence'].apply(categorize_residence)
    
    # Create transition labels
    def get_transition_label(row):
        u = row['uresidence_cat']
        d = row['dresidence_cat']
        
        if u == 'Home' and d == 'Home':
            return 'Home → Home'
        elif u == 'Home' and d == 'RACF':
            return 'Home → RACF (New Entry)'
        elif u == 'RACF' and d == 'RACF':
            return 'RACF → RACF'
        elif u == 'RACF' and d == 'Home':
            return 'RACF → Home (Returned)'
        elif u == 'Home' and d == 'Other':
            return 'Home → Other'
        elif u == 'RACF' and d == 'Other':
            return 'RACF → Other'
        elif u == 'Other' and d == 'Home':
            return 'Other → Home'
        elif u == 'Other' and d == 'RACF':
            return 'Other → RACF'
        else:
            return 'Other Transitions'
    
    transition_df['transition'] = transition_df.apply(get_transition_label, axis=1)
    
    # Count transitions
    transition_counts = transition_df['transition'].value_counts()
    
    # Calculate key metrics
    total_patients = len(transition_df)
    new_racf_entries = transition_counts.get('Home → RACF (New Entry)', 0)
    returned_home = transition_counts.get('RACF → Home (Returned)', 0)
    stayed_home = transition_counts.get('Home → Home', 0)
    stayed_racf = transition_counts.get('RACF → RACF', 0)
    
    stats = {
        'transitions': {
            'Home → Home': int(stayed_home),
            'Home → RACF (New Entry)': int(new_racf_entries),
            'RACF → RACF': int(stayed_racf),
            'RACF → Home (Returned)': int(returned_home),
            'Home → Other': int(transition_counts.get('Home → Other', 0)),
            'RACF → Other': int(transition_counts.get('RACF → Other', 0)),
            'Other → Home': int(transition_counts.get('Other → Home', 0)),
            'Other → RACF': int(transition_counts.get('Other → RACF', 0)),
            'Other Transitions': int(transition_counts.get('Other Transitions', 0))
        },
        'summary': {
            'total_patients': total_patients,
            'new_racf_entries': int(new_racf_entries),
            'new_racf_rate': round(new_racf_entries / total_patients * 100, 1) if total_patients > 0 else 0,
            'returned_home_from_racf': int(returned_home),
            'stayed_home': int(stayed_home),
            'stayed_racf': int(stayed_racf)
        }
    }
    
    return stats

def generate_residence_transition_chart(stats: dict):
    """
    Generate a horizontal bar chart showing residence transitions.
    Returns a data URI (base64 PNG) or None if insufficient data.
    """
    transitions = stats.get('transitions', {})
    
    if not transitions or sum(transitions.values()) == 0:
        return None
    
    # Filter out zero values and sort by count
    filtered_transitions = {k: v for k, v in transitions.items() if v > 0}
    sorted_items = sorted(filtered_transitions.items(), key=lambda x: x[1], reverse=True)
    
    if not sorted_items:
        return None
    
    labels, values = zip(*sorted_items)
    
    # Create figure
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Define colors - highlight new RACF entries
    colors = []
    for label in labels:
        if 'New Entry' in label:
            colors.append('#e24a4a')  # Red for new RACF entries
        elif 'Returned' in label:
            colors.append('#50c878')  # Green for returned home
        elif 'Home → Home' in label:
            colors.append('#4a90e2')  # Blue for stayed home
        elif 'RACF → RACF' in label:
            colors.append('#f5a623')  # Orange for stayed RACF
        else:
            colors.append('#cccccc')  # Grey for other
    
    # Create horizontal bar chart
    bars = ax.barh(range(len(labels)), values, color=colors)
    
    # Customize
    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels, fontsize=9)
    ax.set_xlabel('Number of Patients', fontsize=10, fontweight='bold')
    ax.set_title('Residence Transitions: Admission to Discharge', fontsize=12, fontweight='bold', pad=15)
    
    # Add value labels on bars
    for i, (bar, value) in enumerate(zip(bars, values)):
        width = bar.get_width()
        ax.text(width, bar.get_y() + bar.get_height()/2, 
                f' {int(value)}', 
                ha='left', va='center', fontsize=9, fontweight='bold')
    
    # Add grid for readability
    ax.grid(axis='x', alpha=0.3, linestyle='--')
    ax.set_axisbelow(True)
    
    plt.tight_layout()
    buf = BytesIO()
    plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
    buf.seek(0)
    img64 = base64.b64encode(buf.read()).decode('utf-8')
    plt.close(fig)

    return f"data:image/png;base64,{img64}"
