import sys

from utils import create_pull_request


module = sys.argv[1]
branch = sys.argv[2]

pr_title=f'DNM Migrate {module}* modules and tests'

am_description=f"""
Migrate {module}* modules and tests
"""

# Create PR inside amazon.aws
req_url = create_pull_request(
    "ansible-collections", # owner_name
    "amazon.aws", # repo_name
    am_description, # description
    pr_title,
    branch, # head_branch
    "main", # base_branch
)

url = ''
if req_url:
    url = f"https://github.com/ansible-collections/amazon.aws/pull/{req_url.split('/')[-1]}"

com_description=f"""
Depends-On: {url}

Remove {module}* modules and tests
These modules have been migrated to `amazon.aws`
Update runtime.yml with redirects to that collection
Update ignore files
"""

# Create PR inside community.aws
_ = create_pull_request(
    "ansible-collections", # owner_name
    "community.aws", # repo_name
    com_description, # description
    pr_title,
    branch, # head_branch
    "main", # base_branch
)
