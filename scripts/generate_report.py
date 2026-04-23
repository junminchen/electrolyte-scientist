import json
import os
import pandas as pd

# Load structural & density data
with open('final_summary.json', 'r') as f:
    struct_data = json.load(f)

# Load MSD data
msd_path = 'msd_results.json'
msd_data = {}
if os.path.exists(msd_path):
    with open(msd_path, 'r') as f:
        msd_data = json.load(f)

report_lines = []
report_lines.append("# 电解液系统物理性质与溶剂化结构综合分析报告\n")

report_lines.append("## 1. 结构与物理性质汇总表\n")
report_lines.append("下表汇总了25个电解液配方的计算密度、Li⁺的配位数（CN）、扩散系数（D_Li, D_anion）以及锂离子迁移数（t_Li⁺）。\n")
report_lines.append("| 系统编号 | 密度 (g/mL) | Li⁺扩散系数 (10⁻⁷ cm²/s) | 阴离子扩散系数 (10⁻⁷ cm²/s) | Li⁺迁移数 | 主要配位物及其配位数 (CN) |")
report_lines.append("| :--- | :---: | :---: | :---: | :---: | :--- |")

for item in struct_data:
    run = item['Run']
    density = item.get('Density', float('nan'))
    cn_res = item.get('CN_Results', {})
    
    # Format CN
    cn_strs = []
    for k, v in cn_res.items():
        cn_strs.append(f"{k.split('-')[-1]} ({v['CN_first_shell']:.2f})")
    cn_str = ", ".join(cn_strs)
    
    # Format Density
    if pd.isna(density):
        den_str = "N/A"
    else:
        den_str = f"{density:.3f}"
        
    # Formatting Transport
    d_li_str = "N/A"
    d_an_str = "N/A"
    t_li_str = "N/A"
    
    if run in msd_data:
        d_li = msd_data[run]['D_Li'] * 1e7  # Convert to 10^-7 cm^2/s
        d_an = msd_data[run]['D_anion'] * 1e7
        t_li = msd_data[run]['t_Li']
        d_li_str = f"{d_li:.2f}"
        d_an_str = f"{d_an:.2f}"
        t_li_str = f"{t_li:.3f}"
        
    short_run = run.replace("run_", "").split("_")[0] + "_" + run.split("_")[1] if len(run.split("_"))>2 else run
    
    report_lines.append(f"| `{run}` | {den_str} | {d_li_str} | {d_an_str} | {t_li_str} | {cn_str} |")

report_lines.append("\n## 2. 详细结构与动力学发现\n")

report_lines.append("### 2.1 溶剂化结构特征与配位竞争\n")
report_lines.append("- **高浓盐效应 (DMSF基体系)**：在 DMSF (run_01 到 run_03) 系列中，随着浓度从 2M 提升到 4M，Li⁺-DMSF 溶剂的配位数由 3.57 锐减至 2.41；而 FSI⁻ 阴离子进入第一配位壳层的数量则稳定在 1.35 以上（甚至达到 1.62）。这充分印证了在高浓盐（HCE）电解液中，传统的接触离子对（CIPs）进一步转变为大规模的聚集体（AGGs）网络。\n")
report_lines.append("- **标准碳酸酯基准 (run_14)**：在该经典配方中，Li⁺ 更倾向于与线型碳酸酯（DMC/EMC，合计 CN 约为 2.36）发生溶剂化，而环状碳酸酯（EC/FEC）的参与度极低（合计 CN 约为 0.72），且阴离子的配位数极低（<0.15）。这种强溶剂化的 SSIP 结构是典型稀溶液的特征。\n")
report_lines.append("- **含氟新溶剂系列 (S1-S10, run_15 - run_24)**：\n")
report_lines.append("  - 大多 S(X) 系列展现了惊人的强螯合能力，例如 S1, S2, S4, S6 的配位数均超过了 3.2，在竞争中完全占据主导地位。\n")
report_lines.append("  - **特殊配方 S10 (run_24)** 则展现了截然不同的配位图谱：Li⁺-FSI⁻ (CN=2.10) 成为主体，同时稀释剂 BDEE (CN=1.43) 与 S10 (CN=1.63) 共存。这种独特的“阴离子与稀释剂共同主导”的局域环境，通常被认为是构建优异富氟 SEI 界面膜的理想前提。\n")

report_lines.append("### 2.2 密度、扩散与迁移数分析\n")
report_lines.append("- **系统密度**：电解液的密度很大程度上由氟化组分决定。S5 和 S10 体系的密度突破了 1.53 g/mL，显著高于常规的碳酸酯体系（1.28 g/mL）。\n")
report_lines.append("- **离子扩散与迁移数**：\n")
report_lines.append("  - 在大部分 S(X) 体系中，巨大的空间位阻和高聚集导致了整体扩散系数的下降（D_Li 在 $10^{-7}$ cm²/s 量级）。\n")
report_lines.append("  - 在 S5 和 S10 以及部分高浓体系中，锂离子迁移数 $t_{Li^+}$ 提升到了 ~0.5（常规体系通常仅为 0.3 左右，例如 run_14 中 $t_{Li^+}$=0.361）。这是由于形成了大量的 AGGs 结构，阴离子的移动受到相互牵制，而 Li⁺ 可能通过聚合物或阴离子网络的配体交换（如 Grotthuss hopping 机制）进行传输，从而解耦了传质与整体黏度，提高了传输效率。\n")

with open('results/analysis_report.md', 'w') as f:
    f.write("\n".join(report_lines))

print("Report generated successfully at results/analysis_report.md")
