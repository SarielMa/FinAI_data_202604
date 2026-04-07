#!/bin/bash
#SBATCH --job-name=downloading
#SBATCH --mail-type=ALL
#SBATCH --time=01-00:00:00
#SBATCH --nodes=1
#SBATCH --mem=256G
#SBATCH --partition=day
#SBATCH --output=%j_cpu.txt
#SBATCH --mail-user=linhai.ma@yale.edu

set -euo pipefail

# ---- CUDA toolkit for DeepSpeed ops ----
module purge
module load StdEnv || true
module load CUDA/12.6.0

export CUDA_HOME=$(dirname $(dirname $(which nvcc)))
export PATH=$CUDA_HOME/bin:$PATH
export LD_LIBRARY_PATH=$CUDA_HOME/lib64:$LD_LIBRARY_PATH

# Triton cache off NFS (recommended)
export TRITON_CACHE_DIR=/tmp/$USER/triton_cache
mkdir -p "$TRITON_CACHE_DIR"

# ---- Conda (robust) ----
module load miniconda
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate finben_vllm3

# Debug
which nvcc
nvcc --version
which python
python -c "import torch; print('torch cuda:', torch.version.cuda); print('gpus:', torch.cuda.device_count())"
nvidia-smi

cd /home/lm2445/scratch_pi_sjf37/lm2445/FinAI_data_202604/hacker_news
python down_load_to_jsonl_chunks.py
