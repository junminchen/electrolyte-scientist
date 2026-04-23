---
name: electrolyte-scientist
description: Automated expert for electrolyte MD simulation, structural analysis, and property prediction. Use when provided with chemical formulations or SMILES to run OpenMM simulations and generate HKRI-SciComp standardized reports.
---

# Electrolyte-Scientist Skill

This skill transforms Gemini CLI into an expert computational chemist for electrolyte discovery.

## 1. Environment Setup
Always ensure the runtime environment is correctly linked:
- **LD_LIBRARY_PATH**: Must include `/home/jmchen/miniconda3/envs/bff/openmm/lib`.
- **Python Path**: Use `/home/jmchen/miniconda3/envs/bff/bin/python`.
- **Dependencies**: Requires `MDAnalysis`, `tidynamics`, `seaborn`, `velocityverletplugin`.

## 2. Core Workflow

### A. Initialization
- Maintain `electrolytes_library.json` as the source of truth for SMILES and recipes.
- Execute `python3 scripts/setup_md_runs.py` to:
    - Auto-detect ions and balance charges.
    - Fetch parameters from `shared_params` via smart symlinking.
    - Target 10,000 atoms per system.

### B. Simulation Execution
- **Multi-GPU Orchestration**: Use `python3 scripts/smart_launcher.py <start> <end>` to distribute tasks across GPUs 0-7.
- **Optimized Protocol**: Uses the custom `protocol.py` that bypasses model inference if local parameters exist, preventing dimension mismatch errors.
- **Workflow**: NPT (Density) -> NVT (Production) -> Transport (Properties).

### C. Automated Analysis
- **Structure**: Calculate RDF and Coordination Numbers (CN).
- **Transport**: Calculate $D_{Li}$, $D_{anion}$, and Transference Number $t_{Li^+}$.
- **Fallback**: If NVT trajectory is corrupted, automatically use the last 1000 frames of NPT.

## 3. Reporting Standards
All outputs must include the **HKRI-SciComp** header.
The report must summarize:
1. Physical properties (Density, Diffusion, $t_{Li^+}$).
2. Coordination fingerprints (which solvent/anion dominates Li+ shell).
3. Mechanistic trends (AGG vs CIP vs SSIP).

## 4. Dataset Integration
Append every new result to `results/electrolyte_ml_dataset.csv` to improve the surrogate model for future inverse design.
