import os
import json
import glob
import time
import math
import pandas as pd
from datasets import Dataset
from huggingface_hub import HfApi

# =========================
# CONFIG
# =========================
INPUT_DIR = "freebsd_output_code_only"
WORK_DIR = "hf_dataset"
DATA_DIR = os.path.join(WORK_DIR, "data")

REPO_ID = "TheFinAI/freebsd-cvs-archive"

SHARD_ROWS = 5000
SLEEP_TIME = 1

# 🔥 VERY IMPORTANT (speed + stability)
os.environ["HF_HUB_ENABLE_HF_TRANSFER"] = "1"

# =========================
# STEP 0: INIT REPO
# =========================
api = HfApi()

print("Checking / creating repo...")
api.create_repo(
    repo_id=REPO_ID,
    repo_type="dataset",
    exist_ok=True
)

# =========================
# STEP 1: STREAM + SHARD
# =========================
print("\nStreaming JSONL → Parquet shards...")

os.makedirs(DATA_DIR, exist_ok=True)

files = sorted(glob.glob(os.path.join(INPUT_DIR, "*.jsonl")))

buffer = []
shard_id = 0
total_rows = 0

def save_shard(buffer, shard_id):
    df = pd.DataFrame(buffer)

    # enforce schema
    df = df[["Source", "Date", "Text", "Token_count"]]

    dataset = Dataset.from_pandas(df)

    shard_file = os.path.join(
        DATA_DIR,
        f"train-{shard_id:05d}.parquet"
    )

    dataset.to_parquet(shard_file)

    size_mb = os.path.getsize(shard_file) / 1024 / 1024
    print(f"Saved {shard_file} ({size_mb:.2f} MB)")

for f in files:
    print(f"Reading {f}")

    with open(f, "r") as fin:
        for line in fin:
            try:
                obj = json.loads(line)
                buffer.append(obj)
                total_rows += 1
            except:
                continue

            if len(buffer) >= SHARD_ROWS:
                save_shard(buffer, shard_id)
                buffer = []
                shard_id += 1

# last shard
if buffer:
    save_shard(buffer, shard_id)
    shard_id += 1

print(f"\nTotal rows processed: {total_rows}")
print(f"Total shards: {shard_id}")

# =========================
# STEP 2: UPLOAD (RESUMABLE)
# =========================
print("\nUploading to Hugging Face...")

existing = set(api.list_repo_files(REPO_ID, repo_type="dataset"))

parquet_files = sorted(os.listdir(DATA_DIR))

for f in parquet_files:
    remote_path = f"data/{f}"

    if remote_path in existing:
        print(f"⏭ Skip {f}")
        continue

    local_path = os.path.join(DATA_DIR, f)

    for retry in range(5):
        try:
            print(f"Uploading {f} (try {retry+1})")

            api.upload_file(
                path_or_fileobj=local_path,
                path_in_repo=remote_path,
                repo_id=REPO_ID,
                repo_type="dataset",
            )

            print(f"✅ Done {f}")
            time.sleep(SLEEP_TIME)
            break

        except Exception as e:
            print(f"❌ Failed {f}: {e}")
            time.sleep(5 * (retry + 1))

    else:
        print(f"🚨 Gave up on {f}")

print("\nAll done!")