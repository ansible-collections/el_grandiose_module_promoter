#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2023, Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: remove_modules
short_description: Remove modules and integration tests being migrated from git.
author:
  - Aubin Bikouo (@abikouo)
description:
  - Remove modules and integration tests being migrated from git.
options:
  path:
    description:
      - The path to the git repository.
    required: true
    type: path
  branch:
    description:
      - The branch name.
    required: true
    type: str
  modules:
    description:
      - The modules to migrate.
    required: true
    type: list
    elements: str
  integration_tests:
    description:
      - The integration tests to migrate.
    required: false
    type: list
    elements: str
"""

EXAMPLES = r"""
"""

RETURN = r"""
"""

from ansible.module_utils.basic import AnsibleModule


class Removefiles(AnsibleModule):
    
    def __init__(self):

        argument_specs = dict(
            path=dict(required=True, type="path"),
            branch=dict(required=True, type="str"),
            modules=dict(required=True, type="list", elements="str"),
            integration_tests=dict(type="list", elements="str", default=[]),
        )

        super(Removefiles, self).__init__(argument_spec=argument_specs)

        self.path = self.params.get("path")
        self.branch = self.params.get("branch")
        self.modules = self.params.get("modules")
        self.integration_tests = self.params.get("integration_tests")

        self.execute()

    def execute(self):
        # Move to another branch in order to delete the current one
        command = "git checkout upstream/main"
        self.run_command(command, check_rc=True, cwd=self.path, use_unsafe_shell=True)

        # Delete existing branch
        command = "git branch -D {}".format(self.branch)
        self.run_command(command, check_rc=True, cwd=self.path, use_unsafe_shell=True)

        # Recreate migration branch
        command = "git checkout -B {} upstream/main".format(self.branch)
        self.run_command(command, check_rc=True, cwd=self.path, use_unsafe_shell=True)

        # List file to remove
        command = "git ls-files -c -o -i"
        for m in self.modules:
            command += f' -x "plugins/modules/{m}.py" -x "tests/integration/targets/{m}/*"'
        for t in self.integration_tests:
            command += f' -x "tests/integration/targets/{t}/*"'
        _, stdout, _ = self.run_command(command, check_rc=True, cwd=self.path, use_unsafe_shell=True)

        # Remove file from
        command = "git update-index --force-remove {0}".format(" ".join(stdout.split("\n")))
        _, stdout, _ = self.run_command(command, check_rc=True, cwd=self.path, use_unsafe_shell=True)

        # Git add files
        command = "git add -u"
        self.run_command(command, check_rc=True, cwd=self.path, use_unsafe_shell=True)

        # Git commit
        command = 'git commit -m "Remove modules {0} and corresponding tests."'.format(",".join(self.modules))
        self.run_command(command, check_rc=True, cwd=self.path, use_unsafe_shell=True)

        # Git clean
        command = "git clean -ffdx"
        rc, stdout, stderr = self.run_command(command, check_rc=True, cwd=self.path, use_unsafe_shell=True)

        self.exit_json(changed=True, stderr=stderr, stdout=stdout)

def main():
    Removefiles()


if __name__ == "__main__":
    main()