import os
import sys
import subprocess
import time
import shutil
import json

# Force find byteff2
sys.path.append("/home/jmchen/project/polff")

from byteff2.toolkit.protocol import TransportProtocol as BaseTransportProtocol

class TransportProtocol(BaseTransportProtocol):
    def __init__(self, config):
        # Pass the config to parent constructor
        super().__init__(config)
        # Ensure working dirs exist
        os.makedirs(self.params_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.working_dir, exist_ok=True)

    def generate_ff_params(self, smiles_dict):
        """Force skip FF generation if ITP files are already in params/."""
        all_exist = True
        for comp in smiles_dict.keys():
            itp_path = os.path.join(self.params_dir, f"{comp}.itp")
            if not os.path.exists(itp_path):
                all_exist = False
                break
        
        if all_exist:
            print(f"[{time.ctime()}] INFO All parameters found in {self.params_dir}. Bypassing model generation.")
            # Return something compatible
            return smiles_dict
            
        # Only call parent if parameters are missing (will likely fail in this env)
        return super().generate_ff_params(smiles_dict)

    def build_system(self, total_atoms, components_ratio, working_dir, build_gas=False):
        """Ensure GMX can be found in the PATH."""
        os.environ["PATH"] = f"/home/jmchen/miniconda3/envs/bff/bin:{os.environ.get('PATH', '')}"
        return super().build_system(total_atoms, components_ratio, working_dir, build_gas)

    # Note: run_protocol and post_process are fully inherited from BaseTransportProtocol
