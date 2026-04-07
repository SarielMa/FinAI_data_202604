import requests
import json
import os
import glob
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import tiktoken

BASE = "https://hacker-news.firebaseio.com/v0"
CHUNK_SIZE = 50000
MAX_WORKERS = 50
BATCH_SIZE = 1000

# -----------------------------
# Output folder
# -----------------------------
OUTPUT_DIR = "hn_data"
os.makedirs(OUTPUT_DIR, exist_ok=True)

CHECKPOINT_FILE = os.path.join(OUTPUT_DIR, "checkpoint.json")

# -----------------------------
# Tokenizer
# -----------------------------
enc = tiktoken.get_encoding("cl100k_base")

def count_tokens(text):
    return len(enc.encode(text))

# -----------------------------
# Resume
# -----------------------------
if os.path.exists(CHECKPOINT_FILE):
    with open(CHECKPOINT_FILE, "r") as f:
        checkpoint = json.load(f)
        start_id = checkpoint.get("last_id", 1)
else:
    start_id = 1

existing_files = sorted(glob.glob(os.path.join(OUTPUT_DIR, "hn_part_*.jsonl")))
file_idx = len(existing_files)

print(f"Resuming from ID: {start_id}, file_idx: {file_idx}")

# -----------------------------
# Fetch
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
# Processing logic
# -----------------------------
def process_item(item):
    if not item:
        return None

    if item.get("deleted") or item.get("dead"):
        return None

    text = ""

    if item.get("type") == "story":
        title = item.get("title", "")
        body = item.get("text", "")
        text = f"{title} {body}".strip()

    elif item.get("type") == "comment":
        text = item.get("text", "")

    else:
        return None

    if not text:
        return None

    try:
        year = datetime.utcfromtimestamp(item["time"]).year
    except:
        return None

    if year < 2000:
        return None

    import re
    text = re.sub("<.*?>", "", text).strip()

    if not text:
        return None

    return {
        "source": "hackernews",
        "date": year,
        "text": text,
        "token_count": count_tokens(text)
    }

# -----------------------------
# Main
# -----------------------------
max_id = requests.get(f"{BASE}/maxitem.json").json()

current_chunk = []

for start in tqdm(range(start_id, max_id, BATCH_SIZE)):
    ids = range(start, start + BATCH_SIZE)
    results = fetch_batch(ids)

    for item in results:
        processed = process_item(item)
        if processed:
            current_chunk.append(processed)

    # save chunk
    if len(current_chunk) >= CHUNK_SIZE:
        tmp_file = os.path.join(OUTPUT_DIR, f"hn_part_{file_idx:04d}.jsonl.tmp")
        final_file = os.path.join(OUTPUT_DIR, f"hn_part_{file_idx:04d}.jsonl")

        with open(tmp_file, "w") as f:
            for row in current_chunk:
                f.write(json.dumps(row) + "\n")

        os.rename(tmp_file, final_file)

        current_chunk = []
        file_idx += 1

    # checkpoint
    checkpoint = {
        "last_id": start + BATCH_SIZE,
        "file_idx": file_idx
    }
    with open(CHECKPOINT_FILE, "w") as f:
        json.dump(checkpoint, f)

# save remaining
if current_chunk:
    tmp_file = os.path.join(OUTPUT_DIR, f"hn_part_{file_idx:04d}.jsonl.tmp")
    final_file = os.path.join(OUTPUT_DIR, f"hn_part_{file_idx:04d}.jsonl")

    with open(tmp_file, "w") as f:
        for row in current_chunk:
            f.write(json.dumps(row) + "\n")

    os.rename(tmp_file, final_file)

print("Done!")