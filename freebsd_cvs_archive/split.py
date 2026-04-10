import os

INPUT_DIR = "freebsd_output_code_only"
OUTPUT_DIR = "freebsd_output_ready_for_HF"
MAX_SIZE_MB = 8

os.makedirs(OUTPUT_DIR, exist_ok=True)

MAX_BYTES = MAX_SIZE_MB * 1024 * 1024

file_idx = 0

def open_new_file(idx):
    path = os.path.join(OUTPUT_DIR, f"part-{idx:06d}.jsonl")
    return open(path, "w", encoding="utf-8", newline="\n"), path

out_file, current_path = open_new_file(file_idx)

for fname in sorted(os.listdir(INPUT_DIR)):
    if not fname.endswith(".jsonl"):
        continue

    in_path = os.path.join(INPUT_DIR, fname)

    with open(in_path, "r", encoding="utf-8") as f:
        for line in f:
            encoded = line.encode("utf-8")
            line_bytes = len(encoded)

            # 🚨 Case 1: single line too large
            if line_bytes > MAX_BYTES:
                print(f"⚠️ Large sample ({line_bytes/1024/1024:.2f} MB), isolating")

                out_file.close()

                # write alone
                file_idx += 1
                temp, _ = open_new_file(file_idx)
                temp.write(line)
                temp.close()

                # reopen new shard
                file_idx += 1
                out_file, current_path = open_new_file(file_idx)
                continue

            # 🚨 Check real file size (NOT manual counter)
            out_file.flush()
            current_size = os.path.getsize(current_path)

            if current_size + line_bytes >= MAX_BYTES:
                out_file.close()
                file_idx += 1
                out_file, current_path = open_new_file(file_idx)

            out_file.write(line)

out_file.close()

print(f"✅ Done. Total shards: {file_idx + 1}")