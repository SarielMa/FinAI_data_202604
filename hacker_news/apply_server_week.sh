#!/bin/bash
#SBATCH --job-name=wkdownloading
#SBATCH --mail-type=ALL
#SBATCH --time=02-00:00:00
#SBATCH --nodes=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --partition=week
#SBATCH --output=%j_cpu.txt
#SBATCH --mail-user=linhai.ma@yale.edu

# ---- Conda (robust) ----
module load miniconda
conda activate finben_vllm3

# Debug
which nvcc
nvcc --version
which python
python -c "import torch; print('torch cuda:', torch.version.cuda); print('gpus:', torch.cuda.device_count())"
nvidia-smi

cd /home/lm2445/scratch_pi_sjf37/lm2445/FinAI_data_202604/hacker_news
python down_load_to_jsonl_chunks.py
