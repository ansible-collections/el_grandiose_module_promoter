import os
import json
import requests
import ruamel.yaml


def load_file(file):
    with open(file, 'r') as _f:
        yaml = ruamel.yaml.YAML()
        yaml.preserve_quotes = True
        return yaml.load(_f.read())


def dump_to_file(data, path):
    with open(path, 'w') as yaml_file:
        yaml = ruamel.yaml.YAML()
        yaml.preserve_quotes = True
        yaml.indent(mapping=2, sequence=4, offset=2)
        yaml.explicit_start = True
        yaml.dump(data, yaml_file)


def list_pull_request(owner_name, repo_name, git_token, pr_title):
    req_url = ''

    git_pulls_api = "https://api.github.com/repos/{0}/{1}/pulls".format(
        owner_name,
        repo_name,
    )
    headers = {
        "Authorization": "token {0}".format(git_token),
        "Content-Type": "application/json"
    }

    for _i in range(30):
        response = requests.get(
            git_pulls_api,
            headers=headers
        )
        if response.status_code == 200:
            for req in response.json():
                if pr_title in req['title']:
                    req_url = req['url']
                    return req_url
    return req_url
       

def create_pull_request(owner_name, repo_name, description, pr_title, branch, base_branch):
    username = os.getenv('USERNAME')
    git_token = os.getenv('GITHUB_TOKEN')
    head_branch = f"{username}:{branch}"

    """Creates the pull request for the head_branch against the base_branch"""
    git_pulls_api = "https://api.github.com/repos/{0}/{1}/pulls".format(
        owner_name,
        repo_name
    )
    headers = {
        "Authorization": "token {0}".format(git_token),
        "Content-Type": "application/json"
    }
    payload = {
        "title": pr_title,
        "body": description,
        "head": head_branch,
        "base": base_branch,
    }

    response = requests.post(
        git_pulls_api,
        headers=headers,
        data=json.dumps(payload)
    )
        
    if response.status_code == 422:
        # PR already exists
        url = list_pull_request(owner_name, repo_name, git_token, pr_title)
        if url:
            response = requests.patch(
                url,
                headers=headers,
                data=json.dumps(payload)) 
            if response.ok:
                print(f"PR successfully patched in {repo_name}!")
                return response.json()['url']
            elif not response.ok:
                print("Request Failed: {0}".format(response.text))
                return ''
    elif not response.ok:
        print("Request Failed: {0}".format(response.text))
        return ''
    else:
        print(f"PR successfully created on {repo_name}!")
        return response.json()['url']
