import os
import glob
import json
import MDAnalysis as mda
import numpy as np
from scipy.stats import linregress
import warnings

try:
    import tidynamics
    HAS_TIDYNAMICS = True
except ImportError:
    HAS_TIDYNAMICS = False

warnings.filterwarnings('ignore')

def calculate_msd():
    results = {}
    for run_dir in sorted(glob.glob('run_*')):
        config_path = os.path.join(run_dir, 'config.json')
        if not os.path.exists(config_path): continue
        
        gro_path = os.path.join(run_dir, 'params/solvent_salt.gro')
        nvt_dcd = os.path.join(run_dir, 'transport_results/nvt.dcd')
        npt_dcd = os.path.join(run_dir, 'transport_results/npt.dcd')
        
        dcd_to_use = nvt_dcd if os.path.exists(nvt_dcd) else (npt_dcd if os.path.exists(npt_dcd) else None)
        if not dcd_to_use: continue
        
        try:
            u = mda.Universe(gro_path, dcd_to_use)
            # Skip unwrap if no fragment info
            cation = u.select_atoms("resname LI Li LIT NA Na NAT")
            anions = u.select_atoms("resname FSI PF6 BF4 TFSI")
            
            if len(cation) == 0 or len(anions) == 0: continue
            
            # Using MDAnalysis native MSD or simple displacement if tidynamics is missing
            from MDAnalysis.analysis import msd
            stride = max(1, len(u.trajectory) // 500)
            
            msd_cat = msd.EinsteinMSD(cation, msd_type='xyz', fft=HAS_TIDYNAMICS)
            msd_cat.run(step=stride)
            msd_an = msd.EinsteinMSD(anions, msd_type='xyz', fft=HAS_TIDYNAMICS)
            msd_an.run(step=stride)
            
            # Fit from 40% to 100%
            time_ps = np.arange(len(msd_cat.results.timeseries)) * stride
            start_fit = int(len(time_ps) * 0.4)
            
            d_cat = linregress(time_ps[start_fit:], msd_cat.results.timeseries[start_fit:])[0] / 6.0 * 1e-4
            d_an = linregress(time_ps[start_fit:], msd_an.results.timeseries[start_fit:])[0] / 6.0 * 1e-4
            
            results[run_dir] = {"D_Li": d_cat, "D_anion": d_an, "t_Li": d_cat/(d_cat+d_an) if (d_cat+d_an)>0 else 0}
            print(f"{run_dir}: t_Li = {results[run_dir]['t_Li']:.3f}")
        except Exception as e:
            print(f"Error on {run_dir}: {e}")

    with open('msd_results.json', 'w') as f:
        json.dump(results, f, indent=4)

if __name__ == "__main__":
    calculate_msd()
