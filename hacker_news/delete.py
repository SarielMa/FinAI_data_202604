# from huggingface_hub import HfApi

# REPO_ID = "TheFinAI/freebsd-cvs-archive"

# api = HfApi()

# # Step 1: list files
# files = api.list_repo_files(
#     repo_id=REPO_ID,
#     repo_type="dataset"
# )

# print("Files in repo:")
# for f in files:
#     print(f)

# # Step 2: filter JSONL files (optional)
# jsonl_files = [f for f in files if f.endswith(".jsonl")]

# print(f"\nDeleting {len(jsonl_files)} JSONL files...")

# # Step 3: delete
# api.delete_files(
#     repo_id=REPO_ID,
#     repo_type="dataset",
#     paths=jsonl_files
# )

# print("✅ Done.")

from huggingface_hub import delete_repo, create_repo

delete_repo("TheFinAI/freebsd-cvs-archive", repo_type="dataset")
create_repo("TheFinAI/freebsd-cvs-archive", repo_type="dataset")