
# import os
# import json
# import glob
# import pandas as pd
# from datasets import Dataset, DatasetDict

# # =========================
# # CONFIG
# # =========================
# INPUT_DIR = "freebsd_output_code_only"   # your jsonl folder
# OUTPUT_DIR = "hf_dataset"                # temp folder
# REPO_ID = "TheFinAI/freebsd-cvs-archive"

# SHARD_SIZE = 100_000  # rows per parquet (tune if needed)

# # =========================
# # STEP 1: LOAD JSONL
# # =========================
# print("Loading JSONL files...")

# all_files = sorted(glob.glob(os.path.join(INPUT_DIR, "*.jsonl")))

# rows = []
# for f in all_files:
#     with open(f, "r") as fin:
#         for line in fin:
#             try:
#                 rows.append(json.loads(line))
#             except:
#                 continue

# print(f"Total rows: {len(rows)}")

# df = pd.DataFrame(rows)

# # Optional: enforce schema
# df = df[["Source", "Date", "Text", "Token_count"]]

# # =========================
# # STEP 2: CREATE HF DATASET
# # =========================
# dataset = Dataset.from_pandas(df)

# # =========================
# # STEP 3: SAVE AS PARQUET SHARDS
# # =========================
# print("Saving as parquet shards...")

# data_path = os.path.join(OUTPUT_DIR, "data")
# os.makedirs(data_path, exist_ok=True)

# dataset.to_parquet(
#     os.path.join(data_path, "train.parquet"),
#     batch_size=SHARD_SIZE
# )

# # =========================
# # STEP 4: DATASET DICT (important for HF)
# # =========================
# dataset_dict = DatasetDict({
#     "train": dataset
# })

# # =========================
# # STEP 5: PUSH TO HUB (XET backend)
# # =========================
# print("Uploading to Hugging Face...")

# dataset_dict.push_to_hub(
#     REPO_ID,
#     private=True  # change if needed
# )

# print("Done!")



# import time
# import os
# from huggingface_hub import HfApi

# api = HfApi()
# REPO = "TheFinAI/freebsd-cvs-archive"

# files = sorted(os.listdir("freebsd_output_ready_for_HF"))

# for f in files:
#     path = os.path.join("freebsd_output_ready_for_HF", f)

#     try:
#         print(f"Uploading {f}")
#         api.upload_file(
#             path_or_fileobj=path,
#             path_in_repo=f,
#             repo_id=REPO,
#             repo_type="dataset"
#         )
#         time.sleep(1)  # 🔥 key: slow down

#     except Exception as e:
#         print(f"Retry {f}")
#         time.sleep(10)

from huggingface_hub import HfApi
# from huggingface_hub import create_repo

# create_repo(
#     repo_id="TheFinAI/freebsd-cvs-archive",
#     repo_type="dataset",
#     private=False,   # 🔥 THIS makes it public
#     exist_ok=True,
# )

api = HfApi()

api.upload_large_folder(
    folder_path="freebsd_cvs_archive_dataset",
    repo_id="TheFinAI/freebsd-cvs-archive",
    repo_type="dataset",
)

print("🚀 Upload complete")




# from huggingface_hub import upload_folder
# import os
# import shutil

# REPO_ID = "TheFinAI/freebsd-cvs-archive"
# DATA_DIR = "freebsd_output_code_only"
# TMP_DIR = "hf_upload_tmp"

# # -----------------------------
# # Step 1: clean + filter files
# # -----------------------------
# if os.path.exists(TMP_DIR):
#     shutil.rmtree(TMP_DIR)

# os.makedirs(TMP_DIR, exist_ok=True)

# def is_valid_file(path):
#     if ".ipynb_checkpoints" in path:
#         return False
#     if path.startswith("."):
#         return False
#     return path.endswith(".jsonl")

# for root, _, files in os.walk(DATA_DIR):
#     for f in files:
#         full_path = os.path.join(root, f)

#         if not is_valid_file(full_path):
#             continue

#         rel_path = os.path.relpath(full_path, DATA_DIR)
#         dest_path = os.path.join(TMP_DIR, "data", rel_path)

#         os.makedirs(os.path.dirname(dest_path), exist_ok=True)
#         shutil.copy2(full_path, dest_path)

# print("✅ Files prepared for upload")

# # -----------------------------
# # Step 2: upload (CORRECT WAY)
# # -----------------------------
# upload_folder(
#     folder_path=TMP_DIR,
#     repo_id=REPO_ID,
#     repo_type="dataset",
# )

# print("🚀 Upload complete!")