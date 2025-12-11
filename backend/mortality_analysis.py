import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for server-side rendering
import matplotlib.pyplot as plt
import base64
from io import BytesIO

def compute_mortality(df: pd.DataFrame):
    """
    Compute mortality counts/rates for timeframes present in the dataset.
    Expects columns: mort30d, mort90d, mort120d, mort365d with values 'Alive'/'Deceased'.
    Returns dict with counts and rates.
    """
    total_patients = len(df)

    def calc(col):
        if col in df.columns:
            deceased = (df[col] == 'Deceased').sum()
            return {
                'count': int(deceased),
                'rate': float(deceased / total_patients * 100) if total_patients > 0 else 0.0
            }
        return None

    return {
        '30_day': calc('mort30d'),
        '90_day': calc('mort90d'),
        '120_day': calc('mort120d'),
        '365_day': calc('mort365d'),
        'total_patients': total_patients,
    }


def generate_mortality_chart(mortality: dict):
    """
    Generate a grouped bar chart (Alive vs Deceased) for each timeframe.
    Returns a data URI (base64 PNG) or None if insufficient data.
    """
    total_patients = mortality.get('total_patients', 0)

    # Prepare series
    frames = []
    alive_counts = []
    deceased_counts = []

    def add_frame(label, key):
        data = mortality.get(key)
        if data:
            frames.append(label)
            deceased_counts.append(data['count'])
            alive_counts.append(max(total_patients - data['count'], 0))

    add_frame('30-day', '30_day')
    add_frame('90-day', '90_day')
    add_frame('120-day', '120_day')
    add_frame('365-day', '365_day')

    if not frames:
        return None

    fig, ax = plt.subplots(figsize=(10, 6))
    x = range(len(frames))
    width = 0.6

    # Stacked bars: Alive at bottom, Deceased stacked on top
    bars_alive = ax.bar(x, alive_counts, width, label='Alive', color='#4a90e2')
    bars_deceased = ax.bar(x, deceased_counts, width, bottom=alive_counts, label='Deceased', color='#e24a4a')

    ax.set_xlabel('Time Frame', fontsize=11, fontweight='bold')
    ax.set_ylabel('Number of Patients', fontsize=11, fontweight='bold')
    ax.set_title('Mortality Status Across Time Frames', fontsize=13, fontweight='bold', pad=20)
    ax.set_xticks(list(x))
    ax.set_xticklabels(frames)
    ax.legend()
    ax.grid(axis='y', alpha=0.3, linestyle='--')

    # Add labels for each segment and total
    for i, (alive, deceased) in enumerate(zip(alive_counts, deceased_counts)):
        if alive > 0:
            ax.text(i, alive, f'{int(alive)}', ha='center', va='bottom', fontsize=9, color='#173a5e')
        if deceased > 0:
            ax.text(i, alive + deceased, f'{int(deceased)}', ha='center', va='bottom', fontsize=9, color='#7a1f1f')
        total = alive + deceased
        ax.text(i, total + max(total_patients * 0.02, 1), f'Total {int(total)}', ha='center', va='bottom', fontsize=9, color='#444')

    plt.tight_layout()
    buf = BytesIO()
    plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
    buf.seek(0)
    img64 = base64.b64encode(buf.read()).decode('utf-8')
    plt.close(fig)

    return f"data:image/png;base64,{img64}"
