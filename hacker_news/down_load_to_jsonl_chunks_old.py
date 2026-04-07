import requests
import json
import os
import glob
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor

BASE = "https://hacker-news.firebaseio.com/v0"
CHUNK_SIZE = 50000
MAX_WORKERS = 50
BATCH_SIZE = 1000
CHECKPOINT_FILE = "checkpoint.json"

# -----------------------------
# Resume: load checkpoint
# -----------------------------
if os.path.exists(CHECKPOINT_FILE):
    with open(CHECKPOINT_FILE, "r") as f:
        checkpoint = json.load(f)
        start_id = checkpoint.get("last_id", 1)
else:
    start_id = 1

# Recover file_idx from existing files
existing_files = sorted(glob.glob("hn_part_*.jsonl"))
file_idx = len(existing_files)

print(f"Resuming from ID: {start_id}, file_idx: {file_idx}")

# -----------------------------
# Fetch functions
# -----------------------------
def fetch_item(i, retries=2):
    for _ in range(retries):
        try:
            r = requests.get(f"{BASE}/item/{i}.json", timeout=5)
            if r.status_code == 200:
                return r.json()
        except:
            continue
    return None

def fetch_batch(ids):
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        return list(executor.map(fetch_item, ids))

# -----------------------------
# Get max id
# -----------------------------
max_id = requests.get(f"{BASE}/maxitem.json").json()
print (f"max id is {max_id}" )

current_chunk = []

# -----------------------------
# Main loop
# -----------------------------
for start in tqdm(range(start_id, max_id, BATCH_SIZE)):
    ids = range(start, start + BATCH_SIZE)
    results = fetch_batch(ids)

    for item in results:
        if item:
            current_chunk.append(item)

    # Save chunk
    if len(current_chunk) >= CHUNK_SIZE:
        tmp_file = f"hn_part_{file_idx:04d}.jsonl.tmp"
        final_file = f"hn_part_{file_idx:04d}.jsonl"

        with open(tmp_file, "w") as f:
            for row in current_chunk:
                f.write(json.dumps(row) + "\n")

        os.rename(tmp_file, final_file)

        current_chunk = []
        file_idx += 1

    # Save checkpoint after every batch
    checkpoint = {
        "last_id": start + BATCH_SIZE,
        "file_idx": file_idx
    }
    with open(CHECKPOINT_FILE, "w") as f:
        json.dump(checkpoint, f)

# -----------------------------
# Save remaining
# -----------------------------
if current_chunk:
    tmp_file = f"hn_part_{file_idx:04d}.jsonl.tmp"
    final_file = f"hn_part_{file_idx:04d}.jsonl"

    with open(tmp_file, "w") as f:
        for row in current_chunk:
            f.write(json.dumps(row) + "\n")

    os.rename(tmp_file, final_file)

print("Done!")