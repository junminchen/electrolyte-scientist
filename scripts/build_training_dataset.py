import os
import json
import pandas as pd
import numpy as np
import glob

# 1. Load component counts from config.json files
# 2. Load results from final_summary.json and msd_results.json
# 3. Create a unified tabular dataset

with open('final_summary.json', 'r') as f:
    struct_data = {item['Run']: item for item in json.load(f)}

with open('msd_results.json', 'r') as f:
    msd_data = json.load(f)

all_rows = []
all_components = set()

for run_dir in sorted(glob.glob('run_*')):
    config_path = os.path.join(run_dir, 'config.json')
    if not os.path.exists(config_path):
        continue
        
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    comp_counts = config.get('components', {})
    total_mols = sum(comp_counts.values())
    
    # Calculate molar fractions
    molar_fractions = {k: v/total_mols for k, v in comp_counts.items()}
    all_components.update(molar_fractions.keys())
    
    row = {
        'run_id': run_dir,
        **molar_fractions
    }
    
    # Add Structural results
    if run_dir in struct_data:
        row['density_g_mL'] = struct_data[run_dir].get('Density', np.nan)
        cn_res = struct_data[run_dir].get('CN_Results', {})
        for label, val in cn_res.items():
            # label is like "LI-DME", we want "CN_DME"
            ligand = label.split('-')[-1]
            row[f'CN_{ligand}'] = val.get('CN_first_shell', 0)
            
    # Add Transport results
    if run_dir in msd_data:
        row['D_Li_10-7'] = msd_data[run_dir]['D_Li'] * 1e7
        row['D_anion_10-7'] = msd_data[run_dir]['D_anion'] * 1e7
        row['t_Li'] = msd_data[run_dir]['t_Li']
        
    all_rows.append(row)

# Convert to DataFrame
df = pd.DataFrame(all_rows)

# Fill NaN components with 0 (if a molecule is not in a run, its molar fraction is 0)
# We only want to fill the chemical component columns
comp_cols = list(all_components)
df[comp_cols] = df[comp_cols].fillna(0)

# Reorder columns: ID first, then components, then properties
property_cols = ['density_g_mL', 'D_Li_10-7', 'D_anion_10-7', 't_Li']
# Also include CN columns
cn_cols = [c for c in df.columns if c.startswith('CN_')]
final_cols = ['run_id'] + sorted(comp_cols) + property_cols + sorted(cn_cols)

df = df[final_cols]

# Save to CSV
df.to_csv('results/electrolyte_ml_dataset.csv', index=False)

print(f"Dataset built with {len(df)} samples and {len(df.columns)} features.")
print("\nFirst 5 rows summary:")
print(df.head().to_markdown(index=False))
