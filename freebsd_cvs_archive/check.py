from huggingface_hub import HfApi

api = HfApi()

api.upload_file(
    path_or_fileobj="test.txt",
    path_in_repo="test.txt",
    repo_id="TheFinAI/freebsd-cvs-archive",
    repo_type="dataset",
)