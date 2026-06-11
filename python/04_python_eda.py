"""
Phase 4: Exploratory Data Analysis
St. Martin's Hospital — Heart Disease Risk & Cost Drivers
Run from the folder containing st_martins_hospital_cleaned.csv
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.ticker as mticker

# ── Theme ───────────────────────────────────────────────
sns.set_theme(style="whitegrid")
plt.rcParams['axes.titleweight'] = 'bold'
plt.rcParams['axes.titlesize'] = 13
plt.rcParams['axes.titlecolor'] = '#1F3864'

RISK_COLORS = {'Low': '#70AD47', 'Medium': '#FFC000', 'High': '#C0392B'}
RISK_ORDER = ['Low', 'Medium', 'High']
PRIMARY = '#2F5496'

# ── Load ────────────────────────────────────────────────
df = pd.read_csv('st_martins_hospital_cleaned.csv')
print("Shape:", df.shape)
print(df.describe())

# ════════════════════════════════════════════════════════
# FIGURE 1: Treatment Cost Distribution
# ════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(9, 5.5))
cost = df['Treatment_Cost'].dropna()
sns.histplot(cost, bins=50, kde=True, color=PRIMARY, alpha=0.6,
             ax=ax, edgecolor='white', linewidth=0.5)
ax.axvline(cost.mean(), color='#C0392B', linestyle='--', linewidth=2,
           label=f'Mean: £{cost.mean():,.0f}')
ax.axvline(cost.median(), color='#70AD47', linestyle='--', linewidth=2,
           label=f'Median: £{cost.median():,.0f}')
ax.set_title('Treatment Cost Is Right-Skewed: A Costly Minority Pulls the Average Up')
ax.set_xlabel('Treatment Cost (£)')
ax.set_ylabel('Number of Patients')
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, p: f'£{x/1000:.0f}k'))
ax.legend()
plt.tight_layout()
plt.savefig('fig1_cost_distribution.png', bbox_inches='tight', dpi=150)
plt.close()

# ════════════════════════════════════════════════════════
# FIGURE 2: Correlation Heatmap
# ════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(8, 6.5))
df_corr = df.copy()
df_corr['Risk_Numeric'] = df_corr['Heart_Disease_Risk'].map({'Low': 1, 'Medium': 2, 'High': 3})
df_corr['Diabetes_Numeric'] = df_corr['Diabetes_Diagnosis'].map({'No': 0, 'Yes': 1})
df_corr['Smoking_Numeric'] = df_corr['Smoking_Status'].map({'Never': 0, 'Former': 1, 'Current': 2})

corr_cols = ['Age', 'Blood_Pressure_Systolic', 'Cholesterol_Level', 'BMI',
             'Smoking_Numeric', 'Diabetes_Numeric', 'Hospital_Visits',
             'Treatment_Cost', 'Risk_Numeric']
corr_labels = ['Age', 'Blood Pressure', 'Cholesterol', 'BMI',
               'Smoking', 'Diabetes', 'Hospital Visits', 'Treatment Cost', 'Heart Risk']
corr = df_corr[corr_cols].corr()
corr.columns = corr_labels
corr.index = corr_labels

mask = np.triu(np.ones_like(corr, dtype=bool))
sns.heatmap(corr, mask=mask, annot=True, fmt='.2f', cmap='RdBu_r', center=0,
            square=True, linewidths=0.5, cbar_kws={'shrink': 0.8, 'label': 'Correlation'},
            ax=ax, vmin=-1, vmax=1, annot_kws={'size': 9})
ax.set_title('What Drives Heart Disease Risk? Age, Smoking & Diabetes Lead', pad=12)
plt.xticks(rotation=45, ha='right')
plt.yticks(rotation=0)
plt.tight_layout()
plt.savefig('fig2_correlation_heatmap.png', bbox_inches='tight', dpi=150)
plt.close()

# ════════════════════════════════════════════════════════
# FIGURE 3: Treatment Cost by Risk Group
# ════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(9, 5.5))
df_box = df.dropna(subset=['Heart_Disease_Risk', 'Treatment_Cost'])
sns.boxplot(data=df_box, x='Heart_Disease_Risk', y='Treatment_Cost',
            order=RISK_ORDER, hue='Heart_Disease_Risk', palette=RISK_COLORS,
            legend=False, ax=ax, width=0.6, fliersize=2)
ax.set_title('Treatment Cost Rises Steeply with Risk Tier')
ax.set_xlabel('Heart Disease Risk')
ax.set_ylabel('Treatment Cost (£)')
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, p: f'£{x/1000:.0f}k'))
medians = df_box.groupby('Heart_Disease_Risk')['Treatment_Cost'].median()
for i, risk in enumerate(RISK_ORDER):
    ax.text(i, medians[risk] + 1500, f'£{medians[risk]:,.0f}',
            ha='center', fontweight='bold', fontsize=10, color='#1F3864')
plt.tight_layout()
plt.savefig('fig3_cost_by_risk.png', bbox_inches='tight', dpi=150)
plt.close()

# ════════════════════════════════════════════════════════
# FIGURE 4: Age Distribution by Risk Group
# ════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(9, 5.5))
df_age = df.dropna(subset=['Heart_Disease_Risk'])
for risk in RISK_ORDER:
    subset = df_age[df_age['Heart_Disease_Risk'] == risk]
    sns.kdeplot(subset['Age'], fill=True, alpha=0.4, label=risk,
                color=RISK_COLORS[risk], ax=ax, linewidth=2)
ax.set_title('Older Patients Cluster in the High-Risk Group')
ax.set_xlabel('Age')
ax.set_ylabel('Density')
ax.legend(title='Risk Level')
plt.tight_layout()
plt.savefig('fig4_age_by_risk.png', bbox_inches='tight', dpi=150)
plt.close()

# ════════════════════════════════════════════════════════
# FIGURE 5: Smoking & Diabetes Compound Effect on Cost
# ════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(9, 5.5))
df_sd = df.dropna(subset=['Smoking_Status', 'Diabetes_Diagnosis', 'Treatment_Cost'])
pivot = df_sd.groupby(['Smoking_Status', 'Diabetes_Diagnosis'])['Treatment_Cost'].mean().unstack()
pivot = pivot.reindex(['Never', 'Former', 'Current'])
pivot.plot(kind='bar', ax=ax, color=['#A9CCE3', '#C0392B'], edgecolor='white', width=0.7)
ax.set_title('Smoking + Diabetes Compound: Each Adds to Treatment Cost')
ax.set_xlabel('Smoking Status')
ax.set_ylabel('Average Treatment Cost (£)')
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, p: f'£{x/1000:.0f}k'))
ax.legend(title='Diabetes', labels=['No Diabetes', 'Has Diabetes'])
plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig('fig5_smoking_diabetes_cost.png', bbox_inches='tight', dpi=150)
plt.close()

print("\nAll five figures saved successfully.")