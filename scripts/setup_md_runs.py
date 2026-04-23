import json
import os
import sys

SHARED_PARAMS_ROOT = "/home/jmchen/project/polff/example/4_MD_simulations/2_Li_Metal/shared_params"

def get_atom_count(smiles):
    counts = {
        '[Na+]': 1, 'F[P-](F)(F)(F)(F)F': 7, '[F]S(=O)(=O)[N-]S(=O)(=O)[F]': 9,
        'COCCOC': 16, 'COCCOCCOC': 25, 'COCCOCCOCCOC': 34, 'COCCOCCOCCOCCOC': 43, 'CC1COC(=O)O1': 14
    }
    return counts.get(smiles, 15)

def force_link_params(comp_name, target_dir):
    """Deep search for files in SHARED_PARAMS_ROOT."""
    required_exts = ['.itp', '.atp', '.gro', '.json', '_nb_params.json']
    
    # Pre-map common variations
    ext_map = {ext: ext for ext in required_exts}
    
    # Gather all files in shared_params once for efficient searching
    if not hasattr(force_link_params, "_all_files"):
        force_link_params._all_files = []
        for root, dirs, files in os.walk(SHARED_PARAMS_ROOT):
            for f in files:
                force_link_params._all_files.append(os.path.join(root, f))

    for ext in required_exts:
        target_name = f"{comp_name}{ext}"
        dst_path = os.path.join(target_dir, target_name)
        
        # Try finding the best match
        found_src = None
        for src in force_link_params._all_files:
            fname = os.path.basename(src)
            # Case 1: Exact match (e.g. NA.itp)
            if fname == target_name:
                found_src = src
                break
            # Case 2: Generic nb_params.json inside a folder named after the component
            if ext == '_nb_params.json' and fname == 'nb_params.json':
                parent_dir = os.path.basename(os.path.dirname(src))
                if parent_dir.upper() == comp_name.upper():
                    found_src = src
                    break
            # Case 3: Upper case match
            if fname.upper() == target_name.upper():
                found_src = src
                break

        if found_src:
            if os.path.lexists(dst_path): os.remove(dst_path)
            os.symlink(found_src, dst_path)
        else:
            print(f"  [CRITICAL] Missing {target_name} for {comp_name}")

def setup_na_runs():
    with open('electrolytes_library.json', 'r') as f:
        lib = json.load(f)
    
    # indices 25-34
    for i in range(25, len(lib['formulations'])):
        form = lib['formulations'][i]
        name = form['name'].replace(' ', '_')
        run_dir = f"run_{i:02d}_{name}"
        os.makedirs(run_dir, exist_ok=True)
        params_dir = os.path.join(run_dir, "params")
        os.makedirs(params_dir, exist_ok=True)
        
        print(f"Processing {run_dir}...")
        for comp in form['molar_ratio']:
            force_link_params(comp, params_dir)
            
        molar_ratio = form['molar_ratio']
        avg_atoms = sum(molar_ratio[c] * get_atom_count(lib['components_metadata']['smiles'][c]) for c in molar_ratio)
        total_mols = 10000 / avg_atoms
        counts = {c: int(round(total_mols * r)) for c, r in molar_ratio.items()}
        
        anions = [c for c in counts if '-' in lib['components_metadata']['smiles'][c]]
        cations = [c for c in counts if '+' in lib['components_metadata']['smiles'][c]]
        if cations and anions: counts[cations[0]] = sum(counts[a] for a in anions)
            
        ordered_counts = {}
        for c in sorted(counts):
            smi = lib['components_metadata']['smiles'][c]
            if '+' not in smi and '-' not in smi: ordered_counts[c] = counts[c]
        for c in sorted(cations): ordered_counts[c] = counts[c]
        for a in sorted(anions): ordered_counts[a] = counts[a]

        config = {
            "protocol": "Transport", "params_dir": "params",
            "output_dir": "transport_results", "working_dir": "transport_working_dir",
            "temperature": 298, "natoms": 10000,
            "components": ordered_counts,
            "smiles": {c: lib['components_metadata']['smiles'][c] for c in ordered_counts}
        }
        with open(os.path.join(run_dir, "config.json"), "w") as cf:
            json.dump(config, cf, indent=4)

if __name__ == "__main__":
    setup_na_runs()
