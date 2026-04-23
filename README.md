# Electrolyte-Scientist: Automated Expert for Electrolyte MD Simulations

Electrolyte-Scientist is an automated workflow toolset for high-throughput discovery and characterization of battery electrolytes.

## ⚙️ Prerequisites & Dependencies

Before running the simulations, ensure your environment meets the following requirements:

### 🛠️ Environment Requirements
- **Conda Environment**: `bff` (recommended)
- **Python**: 3.11+
- **CUDA**: 12.0+
- **GROMACS**: Installed and accessible via `gmx` command.

### 📦 Key Python Packages
```bash
pip install openmm MDAnalysis tidynamics seaborn pandas
```
*Note: Requires the **ByteFF** force field library and **velocityverletplugin** for OpenMM.*

---

## 📍 Critical Path Configuration

This toolset relies on several absolute paths. **Before running, please verify the following in `scripts/`**:

1. **Parameter Library**: In `scripts/setup_md_runs.py`, set `SHARED_PARAMS_ROOT` to your shared parameter directory.
   ```python
   SHARED_PARAMS_ROOT = "/path/to/your/shared_params"
   ```
2. **Environment Paths**: In `scripts/smart_launcher.py`, verify the Python and OpenMM library paths:
   ```python
   PYTHON_EXEC = "/home/user/miniconda3/envs/bff/bin/python"
   OPENMM_LIB = "/home/user/miniconda3/envs/bff/lib"
   ```
3. **LD_LIBRARY_PATH**: Ensure your `LD_LIBRARY_PATH` includes the OpenMM and CUDA lib paths to avoid `ModuleNotFoundError` during background runs.

---

## 📥 Installation

### As a Standalone Toolset
```bash
git clone https://github.com/junminchen/electrolyte-scientist.git
cd electrolyte-scientist
```

### As a Gemini CLI Skill
To enable Gemini CLI to use this expert knowledge, add this directory to your skills search path or link it:
```bash
# In your .bashrc or .zshrc
export GEMINI_SKILLS_PATH="$GEMINI_SKILLS_PATH:/path/to/electrolyte-scientist"
```
Then in Gemini CLI: `activate_skill electrolyte-scientist`

---

## 🚀 Usage Workflow

### 1. Define Formulations
Update `electrolytes_library.json` with your SMILES strings and target molar ratios.

### 2. Prepare System & Links
Generate individual run directories and symlink parameters from the shared library:
```bash
python3 scripts/setup_md_runs.py
```

### 3. Launch Simulations
Batch launch tasks (e.g., indices 25-34) across all available GPUs (0-7):
```bash
python3 scripts/smart_launcher.py 25 34
```

### 4. Analysis
After completion, use the analysis scripts:
```bash
python3 scripts/run_rdf_analysis.py  # Coordination shell analysis
python3 scripts/calc_msd.py          # Diffusion coefficients
```

---
## 📄 Standardized Reporting
All outputs are generated in **HKRI-SciComp** format, ready for machine learning dataset integration.
