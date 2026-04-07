import os
import re
import json
import tiktoken
from tqdm import tqdm

# -----------------------------
# Config
# -----------------------------
ROOT_DIR = "/nfs/roberts/scratch/pi_sjf37/lm2445/FinAI_data_202604/freebsd_cvs_archive/ncvs"
OUTPUT_DIR = "./freebsd_output"
SOURCE_NAME = "freebsd_cvs_archive"

MAX_SAMPLES_PER_FILE = 10000  # adjust if needed

os.makedirs(OUTPUT_DIR, exist_ok=True)

enc = tiktoken.get_encoding("cl100k_base")

def count_tokens(text):
    return len(enc.encode(text))


# -----------------------------
# Parse @...@ block (handles @@)
# -----------------------------
def parse_cvs_text_block(s, start_idx):
    i = start_idx
    out = []

    while i < len(s):
        if s[i] == "@":
            if i + 1 < len(s) and s[i + 1] == "@":
                out.append("@")
                i += 2
            else:
                return "".join(out)
        else:
            out.append(s[i])
            i += 1

    return None


# -----------------------------
# Process ONE file
# -----------------------------
def process_file(path):
    samples = []

    try:
        with open(path, "r", errors="ignore") as f:
            content = f.read()
    except:
        return samples

    # --- Step 1: revision → year ---
    rev2year = {}
    meta_matches = re.finditer(
        r"\n(\d+\.\d+(?:\.\d+)*)\n"
        r"date\s+(\d{4})",
        content
    )

    for m in meta_matches:
        rev = m.group(1)
        year = int(m.group(2))
        rev2year[rev] = year

    # --- Step 2: extract text ---
    pattern = re.finditer(
        r"\n(\d+\.\d+(?:\.\d+)*)\nlog\n@",
        content
    )

    for m in pattern:
        rev = m.group(1)
        start = m.end()

        log = parse_cvs_text_block(content, start)
        if log is None:
            continue

        text_pos = content.find("\ntext\n@", start)
        if text_pos == -1:
            continue

        text_start = text_pos + len("\ntext\n@")
        text = parse_cvs_text_block(content, text_start)

        if not text:
            continue

        text = text.strip()

        # optional filtering
        if len(text) < 10:
            continue

        year = rev2year.get(rev)
        if year is None:
            continue

        samples.append({
            "Source": SOURCE_NAME,
            "Date": year,
            "Text": text,
            "Token_count": count_tokens(text),
            # "File": path   # optional but VERY useful later
        })

    return samples


# -----------------------------
# Collect all .v files
# -----------------------------
v_files = []

for root, _, files in os.walk(ROOT_DIR):
    for f in files:
        if f.endswith(",v"):
            v_files.append(os.path.join(root, f))

print("Total .v files found:", len(v_files))


# -----------------------------
# Process ALL files (split output)
# -----------------------------
file_idx = 0
sample_count = 0
total_samples = 0

def open_new_file(idx):
    return open(
        os.path.join(OUTPUT_DIR, f"freebsd_part_{idx:04d}.jsonl"),
        "w",
        encoding="utf-8"
    )

out_f = open_new_file(file_idx)

for path in tqdm(v_files):
    samples = process_file(path)

    for s in samples:
        # rotate file
        if sample_count >= MAX_SAMPLES_PER_FILE:
            out_f.close()
            file_idx += 1
            sample_count = 0
            out_f = open_new_file(file_idx)

        out_f.write(json.dumps(s, ensure_ascii=False) + "\n")

        sample_count += 1
        total_samples += 1

out_f.close()

# -----------------------------
# Final stats
# -----------------------------
print("\nDone!")
print("Total samples:", total_samples)
print("Total output files:", file_idx + 1)
print("Output dir:", OUTPUT_DIR)