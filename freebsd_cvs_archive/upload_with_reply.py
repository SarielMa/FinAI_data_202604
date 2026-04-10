import os
import time
from huggingface_hub import HfApi

REPO = "TheFinAI/freebsd-cvs-archive"
DATA_DIR = "freebsd_output_ready_for_HF"

api = HfApi()

# get already uploaded files
existing = set(api.list_repo_files(REPO, repo_type="dataset"))

files = sorted(os.listdir(DATA_DIR))

for f in files:
    if f in existing:
        print(f"⏭ Skip {f}")
        continue

    path = os.path.join(DATA_DIR, f)

    success = False
    retries = 0

    while not success and retries < 5:
        try:
            print(f"Uploading {f} (try {retries+1})")

            api.upload_file(
                path_or_fileobj=path,
                path_in_repo=f,
                repo_id=REPO,
                repo_type="dataset"
            )

            print(f"✅ Done {f}")
            success = True

            time.sleep(1)  # slow down

        except Exception as e:
            print(f"❌ Failed {f}: {e}")
            retries += 1
            time.sleep(5 * retries)  # exponential backoff

    if not success:
        print(f"🚨 Gave up on {f}")