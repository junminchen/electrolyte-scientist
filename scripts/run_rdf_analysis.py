import os
import glob
import json
import MDAnalysis as mda
import numpy as np
import pandas as pd
from scipy.signal import find_peaks, savgol_filter
from scipy.integrate import simpson
import seaborn as sns
import matplotlib.pyplot as plt

def _find_first_shell_from_rdf(bins, rdf, smooth=True, savgol_window=11, savgol_poly=2, prominence_frac=0.02):
    r = np.asarray(bins)
    g = np.asarray(rdf)
    if smooth and len(g) >= 5:
        win = int(savgol_window)
        if win % 2 == 0: win -= 1
        if win < 3: win = 3
        if win > len(g): win = len(g) if len(g) % 2 == 1 else len(g) - 1
        try:
            g_s = savgol_filter(g, win, savgol_poly)
        except Exception:
            g_s = g
    else:
        g_s = g

    peaks_max, _ = find_peaks(g_s)
    peaks_min, _ = find_peaks(-g_s, prominence=max(g_s) * prominence_frac if max(g_s) > 0 else 0.0)

    if peaks_max.size == 0:
        idx_min = int(peaks_min[0]) if peaks_min.size > 0 else len(r) - 1
    else:
        first_peak_idx = int(peaks_max[0])
        mins_after = peaks_min[peaks_min > first_peak_idx]
        idx_min = int(mins_after[0]) if mins_after.size > 0 else len(r) - 1

    return float(r[idx_min]), int(idx_min)

def get_rdf(u, resnames, names, cation='LI', start=1500, figname=None):
    if len(u.trajectory) == 0: return {}
    sns.set_style("whitegrid")
    sns.set_context("paper", font_scale=1.05)
    palette = sns.color_palette("tab10")
    results = {}
    g_cation = u.select_atoms(f'resname {cation}')
    if len(g_cation) == 0:
        for alt in ['Li', 'li', 'LI', 'LIT']:
            g_cation = u.select_atoms(f'resname {alt}')
            if len(g_cation) > 0: 
                cation = alt
                break
    
    if len(g_cation) == 0: return {}

    box_volume = float(np.prod(u.dimensions[:3]))
    
    fig, ax = plt.subplots(figsize=(6.0, 4.0), dpi=150)
    ax2 = ax.twinx()
    
    handles = []
    handle_labels = []

    for i, resname in enumerate(resnames):
        atom_sel = f"resname {resname} and (type O or type F or type N or name O* or name F* or name N*)"
        g_res = u.select_atoms(atom_sel)
        if len(g_res.atoms) == 0: continue
            
        from MDAnalysis.analysis.rdf import InterRDF
        RDF = InterRDF(g_cation, g_res, nbins=100, range=(0, 10.0))
        RDF.run(start=start)

        bins = np.asarray(RDF.results.bins)
        rdf_vals = np.asarray(RDF.results.rdf)
        rho = float(len(g_res.atoms)) / box_volume if box_volume > 0 else 0.0
        
        cn = [0.0]
        for j in range(1, len(rdf_vals)):
            cn_val = simpson(y=4.0 * np.pi * bins[:j]**2 * rdf_vals[:j] * rho, x=bins[:j])
            cn.append(float(cn_val))

        rmin, idx_min = _find_first_shell_from_rdf(bins, rdf_vals)
        cn_first_shell = float(cn[idx_min])
        
        label = f'{cation}-{resname}'
        results[label] = {'rmin': rmin, 'CN_first_shell': cn_first_shell}
        
        col = palette[i % len(palette)]
        rdf_label = f'{label} (CN={cn_first_shell:.2f})'
        ax_line, = ax.plot(bins, rdf_vals, color=col, linewidth=1.5, label=rdf_label)
        ax2.plot(bins, cn, color=col, linestyle='--', linewidth=1.0, alpha=0.7)
        handles.append(ax_line)
        handle_labels.append(rdf_label)

    ax.legend(handles=handles, labels=handle_labels, loc='upper right', fontsize=8)
    ax.set_xlabel(r"Radius ($\AA$)")
    ax.set_ylabel(r"g(r)")
    ax2.set_ylabel("CN")
    ax.set_xlim(0, 8)
    if figname: plt.savefig(figname, bbox_inches='tight')
    plt.close(fig)
    return results

summary_data = []

for run_dir in sorted(glob.glob('run_*')):
    config_path = os.path.join(run_dir, 'config.json')
    if not os.path.exists(config_path): continue
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    components = config.get('components', {})
    resnames = [k for k in components.keys() if k not in ['LI', 'Li', 'LIT']]
    
    gro_path = os.path.join(run_dir, 'params/solvent_salt.gro')
    nvt_dcd_path = os.path.join(run_dir, 'transport_results/nvt.dcd')
    npt_dcd_path = os.path.join(run_dir, 'transport_results/npt.dcd')
    
    dcd_to_use = None
    start_frame = 1500 
    
    if os.path.exists(nvt_dcd_path):
        try:
            mda.Universe(gro_path, nvt_dcd_path)
            dcd_to_use = nvt_dcd_path
        except:
            print(f"NVT DCD corrupted for {run_dir}, trying NPT fallback...")
            
    if dcd_to_use is None and os.path.exists(npt_dcd_path):
        try:
            u_test = mda.Universe(gro_path, npt_dcd_path)
            dcd_to_use = npt_dcd_path
            start_frame = max(0, len(u_test.trajectory) - 1000)
            print(f"Using NPT DCD (frames {start_frame} to end) for {run_dir}")
        except:
             print(f"Both NVT and NPT DCD corrupted for {run_dir}")

    if dcd_to_use and os.path.exists(gro_path):
        try:
            print(f"Analyzing {run_dir} using {os.path.basename(dcd_to_use)}...")
            u = mda.Universe(gro_path, dcd_to_use)
            rdf_results = get_rdf(u, resnames, ["O F N"]*len(resnames), cation='LI', start=start_frame, figname=os.path.join(run_dir, 'rdf.png'))
            
            npt_csv_path = os.path.join(run_dir, 'transport_results/npt_state.csv')
            avg_density = np.nan
            if os.path.exists(npt_csv_path):
                df_npt = pd.read_csv(npt_csv_path)
                df_npt.columns = [c.lstrip('#').strip('"') for c in df_npt.columns]
                avg_density = df_npt.tail(1000)['Density (g/mL)'].mean()

            summary_data.append({
                'Run': run_dir,
                'Density': avg_density,
                'CN_Results': rdf_results,
                'Source': os.path.basename(dcd_to_use)
            })
        except Exception as e:
            print(f"Error analyzing {run_dir}: {e}")

with open('final_summary.json', 'w') as f:
    json.dump(summary_data, f, indent=4)

print("Analysis complete.")
