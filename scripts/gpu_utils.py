import subprocess
import os

def get_free_gpus():
    """
    Query nvidia-smi for free GPUs based on memory usage.
    Returns a list of GPU indices sorted by available memory (most free first).
    """
    try:
        # Query index, used memory, and total memory
        cmd = "nvidia-smi --query-gpu=index,memory.used,memory.total --format=csv,noheader,nounits"
        output = subprocess.check_output(cmd, shell=True).decode('utf-8').strip()
        
        gpu_stats = []
        for line in output.split('\n'):
            idx, used, total = map(int, line.split(','))
            # Calculate free memory percentage or just use absolute used memory
            gpu_stats.append({
                'index': idx,
                'used': used,
                'total': total,
                'free': total - used
            })
        
        # Sort by free memory descending (most free first)
        # We can also filter by a threshold (e.g., only GPUs with < 1000MiB used)
        sorted_gpus = sorted(gpu_stats, key=lambda x: x['used'])
        return [gpu['index'] for gpu in sorted_gpus]
    except Exception as e:
        print(f"Error querying NVIDIA SMI: {e}")
        return []

if __name__ == "__main__":
    free_gpus = get_free_gpus()
    print(f"Detected free GPUs (sorted by usage): {free_gpus}")
