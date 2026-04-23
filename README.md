# Electrolyte-Scientist: Automated Expert for Electrolyte MD Simulations

Electrolyte-Scientist is an advanced toolset designed for the high-throughput discovery and characterization of battery electrolytes. It automates the entire pipeline from formulation processing to multi-GPU molecular dynamics (MD) execution and structural analysis using the ByteFF force field and OpenMM.

## 🚀 Core Features

- **Automated Formulation Processing**: Converts raw text/JSON recipes into MD-ready systems.
- **Smart Charge Balancing**: Automatically detects ions from SMILES and enforces system neutrality.
- **Multi-GPU Orchestration**: Intelligently distributes tasks across up to 8 GPUs with a single command.
- **Parameter Bypassing**: Efficiently reuses existing force field parameters from a shared library to avoid redundant model inference.
- **Advanced Analysis**: Built-in support for RDF, Coordination Number (CN), and transport property calculations (Viscosity, Conductivity, MSD).

## 📂 Project Structure

```text
electrolyte-scientist/
├── SKILL.md            # Skill definition for Gemini CLI integration
├── README.md           # This documentation
├── scripts/            # Core execution scripts
│   ├── setup_md_runs.py      # System builder & topology generator
│   ├── smart_launcher.py     # Multi-GPU batch task runner
│   ├── protocol.py           # Custom MD workflow with 11->14 dimension patch
│   ├── run_md_separate.py    # Per-task execution entry point
│   ├── run_rdf_analysis.py   # Structural coordination analysis
│   └── calc_msd.py           # Diffusion coefficient calculations
└── assets/             # Templates and static metadata
```

## 🛠️ Usage Guide

### 1. Prepare Your Library
Edit `electrolytes_library.json` to include your SMILES metadata and formulations.

### 2. Generate Simulation Directories
Run the setup script to create structured task folders and link parameters from your `shared_params` library:
```bash
python3 scripts/setup_md_runs.py
```

### 3. Launch Batch Simulations
Distribute your tasks (e.g., tasks indexed 25 to 34) across all available GPUs (0-7):
```bash
python3 scripts/smart_launcher.py 25 34
```

### 4. Monitor Progress
Check logs in real-time for any task:
```bash
tail -f run_25_*/md.log
```

## 🔧 Environment Requirements

- **Python**: 3.11+ (Conda environment `bff` recommended)
- **OpenMM**: 8.0+
- **ByteFF**: Core force field library
- **CUDA**: 12.0+

## 📄 Standardized Reporting
All results are generated in an **HKRI-SciComp** compatible format, facilitating integration into machine learning datasets for future electrolyte inverse design.

---
Developed by the Electrolyte Discovery Team.
