import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler

# 1. Load the dataset we just built
df = pd.read_csv('results/electrolyte_ml_dataset.csv')

# 2. Select Features (Molar fractions of components) and Target (t_Li)
# We exclude ID and property/structure columns from features
target_col = 't_Li'
# Components are all columns between 'BDE' and 'TTE' (alphabetical in our previous script)
# Let's dynamically find them: they are the ones that sum up to ~1 or are identified as components
exclude_cols = ['run_id', 'density_g_mL', 'D_Li_10-7', 'D_anion_10-7', 't_Li']
cn_cols = [c for c in df.columns if c.startswith('CN_')]
feature_cols = [c for c in df.columns if c not in exclude_cols + cn_cols]

X = df[feature_cols]
y = df[target_col]

# Handle potential NaNs in target (though we should have values for all 25 now)
mask = ~y.isna()
X = X[mask]
y = y[mask]

# 3. Train a Random Forest Regressor
# Using a small number of estimators and shallow depth because of small N
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X, y)

# 4. Visualization
sns.set_style("whitegrid")
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

# Plot A: Feature Importance
importances = model.feature_importances_
indices = np.argsort(importances)[-10:]  # Top 10 contributors
ax1.barh(range(len(indices)), importances[indices], color='skyblue', align='center')
ax1.set_yticks(range(len(indices)))
ax1.set_yticklabels([feature_cols[i] for i in indices])
ax1.set_xlabel('Relative Importance Weight')
ax1.set_title('Which Components Drive t_Li+? (Top 10)', fontsize=12, fontweight='bold')

# Plot B: Parity Plot (Self-consistency check)
y_pred = model.predict(X)
ax2.scatter(y, y_pred, alpha=0.7, color='coral', edgecolors='w', s=80)
ax2.plot([y.min(), y.max()], [y.min(), y.max()], 'k--', lw=1)
ax2.set_xlabel('MD Simulated t_Li+')
ax2.set_ylabel('Model Predicted t_Li+')
ax2.set_title('Model Accuracy (Parity Plot)', fontsize=12, fontweight='bold')

# Add HKRI-SciComp brand
fig.text(0.5, 0.01, 'Department: HKRI-SciComp | Surrogate Model Demo', ha='center', fontsize=10, color='gray')

plt.tight_layout()
plt.savefig('results/surrogate_model_analysis.png', dpi=300)
print("Surrogate model analysis complete. Plot saved to results/surrogate_model_analysis.png")

# Output the weights for text summary
top_features = sorted(zip(importances, feature_cols), reverse=True)[:5]
print("\nTop 5 Influential Components for t_Li+:")
for imp, name in top_features:
    print(f"- {name}: {imp:.4f}")
