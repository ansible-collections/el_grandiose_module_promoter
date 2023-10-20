#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2023, Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: create_pr
short_description: Create pull request on Github repository
author:
  - Aubin Bikouo (@abikouo)
description:
  - Create pull request using input parameters
options:
  repository:
    description:
      - The base repository for the pull request to create.
    required: true
    type: dict
    suboptions:
        name:
            description:
            - The repository name
            required: true
        base_branch:
            description:
            - The pull request base branch.
            required: false
            default: 'main'
        head_branch:
            description:
            - The pull request head branch
            required: false
  fork:
    description:
      - The fork repository from which the pull request should be created.
    required: false
    type: dict
    suboptions:
        owner:
            description:
            - The owner of the fork repository
            required: true
        branch:
            description:
            - The fork branch used as pull request head branch.
            required: true
  body:
    description:
      - The pull request body.
    required: true
  title:
    description:
      - The pull request title.
    required: true
  token:
    description:
      - The Github token used to create pull request.
    required: true
    no_log: true
"""

EXAMPLES = r"""
"""

RETURN = r"""
"""

from github import Github
from github import GithubException
from ansible.module_utils.basic import AnsibleModule


class CreatePR(AnsibleModule):
    
    def __init__(self):

        argument_specs = dict(
            repository=dict(
                type="dict",
                required=True,
                options=dict(
                    name=dict(required=True),
                    base_branch=dict(required=False, default='main'),
                    head_branch=dict(),
                ),
            ),
            fork=dict(
                type="dict",
                required=False,
                options=dict(
                    owner=dict(required=True),
                    branch=dict(required=True),
                ),
            ),
            title=dict(required=True),
            body=dict(required=True),
            token=dict(required=True, no_log=True),
        )

        super(CreatePR, self).__init__(argument_spec=argument_specs)
        self.execute()

    def execute(self):

        try:
            self.client = Github(self.params.get("token"))
            repo = self.client.get_repo(self.params.get("repository").get("name"))
            fork = self.params.get("fork")
            head_br = self.params.get("repository").get("head_branch")
            base_br = self.params.get("repository").get("base_branch")

            if not fork and not head_br:
                self.fail_json(msg="at least one of 'repository.head_branch' or 'fork' parameters should be specified")

            params = {
                "title": self.params.get("title"),
                "body": self.params.get("body"),
                "base": base_br,
            }

            if head_br:
                params["head"] = head_br
            else:
                params["head"] = '{}:{}'.format(self.params.get("fork").get("owner"), self.params.get("fork").get("branch"))

            pr = repo.create_pull(**params)
            self.exit_json(changed=True, url=pr.html_url, id=pr.id, commits=pr.commits, changed_files=pr.changed_files)

        except GithubException as err:
            if err.status == 422 and "A pull request already exists" in str(err):
                self.exit_json(changed=False, msg=err.data.get("errors")[0]["message"])
            self.fail_json(msg="Failed to create pull request due to: %s" % str(err.data.get("errors")))

        except Exception as e:
            self.fail_json(msg="An error occurred while regenerating collection", exception=e)



def main():
    CreatePR()

if __name__ == "__main__":
    main()