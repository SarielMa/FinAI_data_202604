import json
import os

INPUT_DIR = "hn_data"
OUTPUT_DIR = "hn_data_capitalized"

os.makedirs(OUTPUT_DIR, exist_ok=True)

for file in os.listdir(INPUT_DIR):
    if not file.endswith(".jsonl"):
        continue

    in_path = os.path.join(INPUT_DIR, file)
    out_path = os.path.join(OUTPUT_DIR, file)

    with open(in_path, "r") as fin, open(out_path, "w") as fout:
        for line in fin:
            obj = json.loads(line)

            new_obj = {
                "Source": obj.get("source"),
                "Date": int(obj.get("date")),
                "Text": obj.get("text"),
                "Token_count": int(obj.get("token_count")),
            }

            fout.write(json.dumps(new_obj) + "\n")