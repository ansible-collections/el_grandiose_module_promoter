import sys

from utils import create_pull_request

module = sys.argv[1]
branch = sys.argv[2]

repo_name = sys.argv[3]

description=f"""
Update {module}* doc links
"""
pr_title = f"Update documentation links for {module}*"

# Create PR inside source repo
_ = create_pull_request(
    "ansible-collections", # owner_name
    repo_name, # repo_name
    description, # description
    pr_title, # title
    branch, # head_branch
    "main", # base_branch
)
