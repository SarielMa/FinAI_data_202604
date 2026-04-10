from huggingface_hub import create_repo

create_repo(
    repo_id="TheFinAI/freebsd-cvs-archive",
    repo_type="dataset",
    exist_ok=True
)