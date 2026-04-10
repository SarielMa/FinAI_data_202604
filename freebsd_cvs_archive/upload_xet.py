import os
from huggingface_hub import HfApi, create_repo

# =========================================================
# 🔥 FORCE XET (CRITICAL — must be BEFORE anything else)
# =========================================================
os.environ["HF_HUB_ENABLE_XET"] = "1"
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

# =========================================================
# ⚙️ CONFIG
# =========================================================
REPO_ID = "TheFinAI/freebsd-cvs-archive"   # change if needed
FOLDER_PATH = "freebsd_output_ready_for_HF"
REPO_TYPE = "dataset"

# =========================================================
# 🚀 INIT
# =========================================================
api = HfApi()

# =========================================================
# 🏗️ CREATE REPO (if not exists)
# =========================================================
print("📦 Creating repo if not exists...")
create_repo(
    repo_id=REPO_ID,
    repo_type=REPO_TYPE,
    exist_ok=True,
)

# =========================================================
# 🔍 CHECK FILES
# =========================================================
files = [f for f in os.listdir(FOLDER_PATH) if f.endswith(".jsonl")]
files.sort()

print(f"📁 Found {len(files)} files to upload")
print(f"📄 Example files: {files[:5]}")

# =========================================================
# 🚀 UPLOAD (XET BACKEND)
# =========================================================
print("\n🚀 Uploading with Xet backend...")

api.upload_folder(
    folder_path=FOLDER_PATH,
    repo_id=REPO_ID,
    repo_type=REPO_TYPE,

    # 🔥 IMPORTANT SETTINGS
    # multi_commits=True,      # avoid timeout for large uploads
    commit_message="Upload dataset using Xet backend",
)

print("\n✅ Upload completed successfully!")