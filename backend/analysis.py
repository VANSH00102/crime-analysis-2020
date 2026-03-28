"""
analysis.py - Indian Crime Data Analysis 2020
Performs data preprocessing, analysis, and generates visualizations.
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import os
import json
import warnings
warnings.filterwarnings('ignore')

# ─── Paths ───────────────────────────────────────────────────────────────────
BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
DATA_PATH   = os.path.join(BASE_DIR, 'data', 'crime_data_2020.csv')
OUTPUT_DIR  = os.path.join(BASE_DIR, 'outputs')

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ─── Color Palette ────────────────────────────────────────────────────────────
PALETTE     = ['#C0392B', '#E74C3C', '#E67E22', '#F39C12', '#F1C40F',
               '#2ECC71', '#1ABC9C', '#3498DB', '#2980B9', '#9B59B6']
BG_COLOR    = '#0D1117'
TEXT_COLOR  = '#E6EDF3'
ACCENT      = '#C0392B'


def set_style():
    """Apply a dark, professional matplotlib style."""
    plt.rcParams.update({
        'figure.facecolor': BG_COLOR,
        'axes.facecolor':   '#161B22',
        'axes.edgecolor':   '#30363D',
        'axes.labelcolor':  TEXT_COLOR,
        'xtick.color':      TEXT_COLOR,
        'ytick.color':      TEXT_COLOR,
        'text.color':       TEXT_COLOR,
        'grid.color':       '#21262D',
        'grid.linestyle':   '--',
        'grid.alpha':       0.5,
        'font.family':      'DejaVu Sans',
        'font.size':        10,
        'axes.titlesize':   13,
        'axes.titleweight': 'bold',
        'figure.dpi':       150,
    })


# ══════════════════════════════════════════════════════════════════════════════
# DATA LOADING & PREPROCESSING
# ══════════════════════════════════════════════════════════════════════════════
def load_and_preprocess():
    """Load CSV, clean data, and return a clean DataFrame."""
    df = pd.read_csv(DATA_PATH)

    # Strip whitespace from string columns
    df.columns = df.columns.str.strip()
    for col in df.select_dtypes(include='object').columns:
        df[col] = df[col].str.strip()

    # Fill numeric NaN with column median
    for col in ['Cases_Registered', 'Cases_Chargesheeted',
                'Cases_Convicted', 'Persons_Arrested', 'Crime_Rate']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
        df[col].fillna(df[col].median(), inplace=True)

    # Derived columns
    df['Chargesheet_Rate'] = (df['Cases_Chargesheeted'] / df['Cases_Registered'] * 100).round(2)
    df['Conviction_Rate']  = (df['Cases_Convicted']     / df['Cases_Registered'] * 100).round(2)

    return df


# ══════════════════════════════════════════════════════════════════════════════
# ANALYSIS FUNCTIONS
# ══════════════════════════════════════════════════════════════════════════════
def get_stats(df):
    """Return key statistics as a dictionary."""
    total_crimes      = int(df['Cases_Registered'].sum())
    top_state         = df.groupby('State_UT')['Cases_Registered'].sum().idxmax()
    most_common_crime = df.groupby('Crime_Type')['Cases_Registered'].sum().idxmax()
    avg_conviction    = round(df['Conviction_Rate'].mean(), 2)
    total_arrested    = int(df['Persons_Arrested'].sum())
    num_states        = df['State_UT'].nunique()
    num_crime_types   = df['Crime_Type'].nunique()
    highest_crime_rate_state = df.groupby('State_UT')['Crime_Rate'].mean().idxmax()

    # Top 5 states
    top5_states = (df.groupby('State_UT')['Cases_Registered']
                     .sum()
                     .nlargest(5)
                     .reset_index()
                     .to_dict(orient='records'))

    # Crime type breakdown
    crime_breakdown = (df.groupby('Crime_Type')['Cases_Registered']
                         .sum()
                         .sort_values(ascending=False)
                         .reset_index()
                         .to_dict(orient='records'))

    return {
        'total_crimes':              total_crimes,
        'top_state':                 top_state,
        'most_common_crime':         most_common_crime,
        'avg_conviction_rate':       avg_conviction,
        'total_persons_arrested':    total_arrested,
        'num_states_covered':        num_states,
        'num_crime_types':           num_crime_types,
        'highest_crime_rate_state':  highest_crime_rate_state,
        'top5_states':               top5_states,
        'crime_breakdown':           crime_breakdown,
    }


# ══════════════════════════════════════════════════════════════════════════════
# VISUALIZATION FUNCTIONS
# ══════════════════════════════════════════════════════════════════════════════
def save_fig(name):
    """Save current figure to output directory."""
    path = os.path.join(OUTPUT_DIR, name)
    plt.savefig(path, bbox_inches='tight', facecolor=BG_COLOR, dpi=150)
    plt.close()
    return name


def plot_top_states_bar(df):
    """Bar chart – Top 10 states by total cases registered."""
    set_style()
    top10 = (df.groupby('State_UT')['Cases_Registered']
               .sum()
               .nlargest(10)
               .sort_values())

    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.barh(top10.index, top10.values, color=PALETTE, edgecolor='none', height=0.65)

    # Value labels
    for bar in bars:
        ax.text(bar.get_width() + top10.max() * 0.01, bar.get_y() + bar.get_height() / 2,
                f'{int(bar.get_width()):,}', va='center', fontsize=9, color=TEXT_COLOR)

    ax.set_title('Top 10 States by Cases Registered (2020)', pad=15)
    ax.set_xlabel('Total Cases Registered')
    ax.set_xlim(0, top10.max() * 1.15)
    ax.grid(axis='x')
    ax.set_axisbelow(True)
    fig.tight_layout()
    return save_fig('top_states_bar.png')


def plot_crime_type_pie(df):
    """Pie chart – Crime type distribution."""
    set_style()
    crime_totals = df.groupby('Crime_Type')['Cases_Registered'].sum().sort_values(ascending=False)

    # Group small slices into "Others"
    threshold = crime_totals.sum() * 0.02
    main   = crime_totals[crime_totals >= threshold]
    others = crime_totals[crime_totals < threshold].sum()
    if others > 0:
        main['Others'] = others

    fig, ax = plt.subplots(figsize=(9, 9))
    wedges, texts, autotexts = ax.pie(
        main.values,
        labels=main.index,
        autopct='%1.1f%%',
        colors=PALETTE[:len(main)],
        startangle=140,
        pctdistance=0.80,
        wedgeprops=dict(edgecolor=BG_COLOR, linewidth=2),
    )
    for t in texts:
        t.set_fontsize(9)
        t.set_color(TEXT_COLOR)
    for at in autotexts:
        at.set_fontsize(8)
        at.set_color(BG_COLOR)
        at.set_fontweight('bold')

    ax.set_title('Crime Type Distribution – India 2020', pad=20)
    fig.tight_layout()
    return save_fig('crime_type_pie.png')


def plot_top5_grouped_bar(df):
    """Grouped bar – Top 5 states across major crime types."""
    set_style()
    top5_states = (df.groupby('State_UT')['Cases_Registered']
                     .sum()
                     .nlargest(5)
                     .index.tolist())

    major_crimes = ['Murder', 'Rape', 'Kidnapping & Abduction', 'Theft', 'Burglary']
    pivot = (df[df['State_UT'].isin(top5_states) & df['Crime_Type'].isin(major_crimes)]
               .pivot_table(index='State_UT', columns='Crime_Type',
                            values='Cases_Registered', aggfunc='sum')
               .fillna(0))
    pivot = pivot.reindex(top5_states)

    x     = np.arange(len(pivot.index))
    width = 0.15
    fig, ax = plt.subplots(figsize=(12, 6))

    for i, crime in enumerate(major_crimes):
        if crime in pivot.columns:
            bars = ax.bar(x + i * width, pivot[crime], width,
                          label=crime, color=PALETTE[i], edgecolor='none')

    ax.set_title('Major Crime Types – Top 5 States (2020)')
    ax.set_xticks(x + width * 2)
    ax.set_xticklabels(pivot.index, rotation=15, ha='right')
    ax.set_ylabel('Cases Registered')
    ax.legend(fontsize=8, facecolor='#161B22', edgecolor='#30363D', labelcolor=TEXT_COLOR)
    ax.grid(axis='y')
    ax.set_axisbelow(True)
    fig.tight_layout()
    return save_fig('top5_grouped_bar.png')


def plot_heatmap(df):
    """Heatmap – Crime rate across states and crime types."""
    set_style()
    pivot = df.pivot_table(index='State_UT', columns='Crime_Type',
                           values='Crime_Rate', aggfunc='mean').fillna(0)

    fig, ax = plt.subplots(figsize=(14, 12))
    cmap = sns.color_palette("YlOrRd", as_cmap=True)
    sns.heatmap(
        pivot,
        ax=ax,
        cmap=cmap,
        linewidths=0.5,
        linecolor='#0D1117',
        annot=True,
        fmt='.1f',
        annot_kws={'size': 6},
        cbar_kws={'shrink': 0.6, 'label': 'Crime Rate (per lakh population)'},
    )
    ax.set_title('Crime Rate Heatmap – States vs Crime Types (2020)', pad=15)
    ax.set_xlabel('Crime Type')
    ax.set_ylabel('State / UT')
    ax.tick_params(axis='x', rotation=45, labelsize=8)
    ax.tick_params(axis='y', rotation=0, labelsize=7)
    fig.tight_layout()
    return save_fig('crime_rate_heatmap.png')


def plot_conviction_rate(df):
    """Horizontal bar – Conviction rate by crime type."""
    set_style()
    conv = (df.groupby('Crime_Type')
              .apply(lambda g: (g['Cases_Convicted'].sum() / g['Cases_Registered'].sum() * 100))
              .sort_values()
              .round(2))

    fig, ax = plt.subplots(figsize=(10, 6))
    colors = [PALETTE[int(v / 10) % len(PALETTE)] for v in conv.values]
    bars = ax.barh(conv.index, conv.values, color=colors, edgecolor='none', height=0.6)

    for bar in bars:
        ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height() / 2,
                f'{bar.get_width():.1f}%', va='center', fontsize=9, color=TEXT_COLOR)

    ax.set_title('Conviction Rate by Crime Type (2020)')
    ax.set_xlabel('Conviction Rate (%)')
    ax.set_xlim(0, conv.max() * 1.15)
    ax.grid(axis='x')
    ax.set_axisbelow(True)
    fig.tight_layout()
    return save_fig('conviction_rate_bar.png')


def plot_state_crime_rate(df):
    """Bar chart – Average crime rate per lakh population by state."""
    set_style()
    rate = (df.groupby('State_UT')['Crime_Rate']
              .mean()
              .sort_values(ascending=False)
              .head(15))

    fig, ax = plt.subplots(figsize=(11, 6))
    bar_colors = [PALETTE[i % len(PALETTE)] for i in range(len(rate))]
    bars = ax.bar(rate.index, rate.values, color=bar_colors, edgecolor='none', width=0.7)

    for bar in bars:
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5,
                f'{bar.get_height():.1f}', ha='center', fontsize=8, color=TEXT_COLOR)

    ax.set_title('Avg Crime Rate per Lakh Population – Top 15 States (2020)')
    ax.set_ylabel('Crime Rate (per lakh population)')
    ax.set_xticklabels(rate.index, rotation=40, ha='right', fontsize=8)
    ax.grid(axis='y')
    ax.set_axisbelow(True)
    fig.tight_layout()
    return save_fig('state_crime_rate.png')


def plot_arrests_vs_cases(df):
    """Scatter plot – Arrests vs cases registered."""
    set_style()
    state_df = df.groupby('State_UT')[['Cases_Registered', 'Persons_Arrested']].sum().reset_index()

    fig, ax = plt.subplots(figsize=(10, 7))
    scatter = ax.scatter(
        state_df['Cases_Registered'],
        state_df['Persons_Arrested'],
        c=range(len(state_df)),
        cmap='plasma',
        s=80,
        alpha=0.85,
        edgecolors='none',
    )

    # Label a few key states
    for _, row in state_df.nlargest(5, 'Cases_Registered').iterrows():
        ax.annotate(row['State_UT'],
                    (row['Cases_Registered'], row['Persons_Arrested']),
                    textcoords='offset points', xytext=(6, 4),
                    fontsize=7.5, color=TEXT_COLOR)

    # Trend line
    z  = np.polyfit(state_df['Cases_Registered'], state_df['Persons_Arrested'], 1)
    p  = np.poly1d(z)
    xs = np.linspace(state_df['Cases_Registered'].min(), state_df['Cases_Registered'].max(), 200)
    ax.plot(xs, p(xs), '--', color='#F39C12', linewidth=1.5, alpha=0.8, label='Trend Line')

    ax.set_title('Persons Arrested vs Cases Registered by State (2020)')
    ax.set_xlabel('Cases Registered')
    ax.set_ylabel('Persons Arrested')
    ax.legend(facecolor='#161B22', edgecolor='#30363D', labelcolor=TEXT_COLOR)
    ax.grid(True)
    ax.set_axisbelow(True)
    fig.tight_layout()
    return save_fig('arrests_vs_cases.png')


def plot_crime_composition(df):
    """Stacked bar – Crime composition for top 8 states."""
    set_style()
    top8 = (df.groupby('State_UT')['Cases_Registered']
              .sum()
              .nlargest(8)
              .index.tolist())

    pivot = (df[df['State_UT'].isin(top8)]
               .pivot_table(index='State_UT', columns='Crime_Type',
                            values='Cases_Registered', aggfunc='sum')
               .fillna(0))
    pivot = pivot.reindex(top8)
    pivot_pct = pivot.div(pivot.sum(axis=1), axis=0) * 100

    fig, ax = plt.subplots(figsize=(12, 6))
    bottom = np.zeros(len(pivot_pct))
    for i, col in enumerate(pivot_pct.columns):
        ax.bar(pivot_pct.index, pivot_pct[col], bottom=bottom,
               color=PALETTE[i % len(PALETTE)], label=col, edgecolor='none')
        bottom += pivot_pct[col].values

    ax.set_title('Crime Composition (%) – Top 8 States (2020)')
    ax.set_ylabel('Percentage of Total Crimes (%)')
    ax.set_xticklabels(pivot_pct.index, rotation=30, ha='right', fontsize=8)
    ax.legend(fontsize=7, facecolor='#161B22', edgecolor='#30363D',
              labelcolor=TEXT_COLOR, bbox_to_anchor=(1.01, 1), loc='upper left')
    ax.grid(axis='y')
    ax.set_axisbelow(True)
    fig.tight_layout()
    return save_fig('crime_composition.png')


# ══════════════════════════════════════════════════════════════════════════════
# MAIN RUN
# ══════════════════════════════════════════════════════════════════════════════
def run_all():
    """Run complete analysis pipeline and return results."""
    df      = load_and_preprocess()
    stats   = get_stats(df)
    images  = []

    print("[*] Generating visualizations...")
    images.append(plot_top_states_bar(df))
    images.append(plot_crime_type_pie(df))
    images.append(plot_top5_grouped_bar(df))
    images.append(plot_heatmap(df))
    images.append(plot_conviction_rate(df))
    images.append(plot_state_crime_rate(df))
    images.append(plot_arrests_vs_cases(df))
    images.append(plot_crime_composition(df))

    print(f"[✓] {len(images)} visualizations saved to {OUTPUT_DIR}")
    return {'stats': stats, 'images': images, 'status': 'success'}


if __name__ == '__main__':
    result = run_all()
    print(json.dumps(result['stats'], indent=2))
