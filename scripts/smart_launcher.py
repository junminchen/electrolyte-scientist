import os
import subprocess
import sys

def launch_tasks(start_idx, end_idx, gpus=[0,1,2,3,4,5,6,7]):
    python_exec = "/home/jmchen/miniconda3/envs/bff/bin/python"
    openmm_lib = "/home/jmchen/miniconda3/envs/bff/lib"
    
    # Get list of run directories
    all_dirs = sorted([d for d in os.listdir('.') if d.startswith('run_') and os.path.isdir(d)])
    
    count = 0
    for run_dir in all_dirs:
        # Extract index from 'run_XX_...'
        try:
            idx = int(run_dir.split('_')[1])
        except:
            continue
            
        if start_idx <= idx <= end_idx:
            gpu_id = gpus[count % len(gpus)]
            print(f"Starting {run_dir} on GPU {gpu_id}...")
            
            # Build the command
            cmd = f"cd {run_dir} && export LD_LIBRARY_PATH={openmm_lib}:$LD_LIBRARY_PATH && "
            cmd += f"nohup env CUDA_VISIBLE_DEVICES={gpu_id} {python_exec} ../../run_md_separate.py --config config.json > md.log 2>&1 &"
            
            subprocess.run(cmd, shell=True, executable='/bin/bash')
            count += 1

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 smart_launcher.py <start_idx> <end_idx>")
        print("Example: python3 smart_launcher.py 25 34")
    else:
        launch_tasks(int(sys.argv[1]), int(sys.argv[2]))
