from huggingface_hub import create_repo

# from huggingface_hub import create_repo

create_repo(
    repo_id="TheFinAI/hacker-news",
    repo_type="dataset",
    private=False,   # 🔥 THIS makes it public
    exist_ok=True,
)