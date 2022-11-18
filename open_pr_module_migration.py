import sys

from utils import create_pull_request


module = sys.argv[1]
branch = sys.argv[2]

src_repo_name = sys.argv[3]
dest_repo_name = sys.argv[4]

pr_title=f'DNM Migrate {module}* modules and tests'

am_description=f"""
Migrate {module}* modules and tests
"""

# Create PR inside dest_repo_name
req_url = create_pull_request(
    "ansible-collections", # owner_name
    dest_repo_name, # repo_name
    am_description, # description
    pr_title,
    branch, # head_branch
    "main", # base_branch
)

url = ''
if req_url:
    url = f"https://github.com/ansible-collections/{dest_repo_name}/pull/{req_url.split('/')[-1]}"

com_description=f"""
Depends-On: {url}

Remove {module}* modules and tests
These modules have been migrated to `{dest_repo_name}`
Update runtime.yml with redirects to that collection
Update ignore files
"""

# Create PR inside src_repo_name
_ = create_pull_request(
    "ansible-collections", # owner_name
    src_repo_name, # repo_name
    com_description, # description
    pr_title,
    branch, # head_branch
    "main", # base_branch
)
