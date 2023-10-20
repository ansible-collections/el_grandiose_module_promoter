#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2023, Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: create_patches
short_description: Create patches files for modules to be migrated
author:
  - Aubin Bikouo (@abikouo)
description:
  - Create patches files for modules and integration tests to be migrated.
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
  collection_name:
    description:
      - The collection name.
    required: true
    type: str
"""

EXAMPLES = r"""
"""

RETURN = r"""
"""

from ansible.module_utils.basic import AnsibleModule
import tempfile
import glob


class CreatePatches(AnsibleModule):
    
    def __init__(self):

        argument_specs = dict(
            path=dict(required=True, type="path"),
            branch=dict(required=True, type="str"),
            modules=dict(required=True, type="list", elements="str"),
            integration_tests=dict(type="list", elements="str", default=[]),
            collection_name=dict(required=True, type="str"),
        )

        super(CreatePatches, self).__init__(argument_spec=argument_specs)

        self.path = self.params.get("path")
        self.branch = self.params.get("branch")
        self.modules = self.params.get("modules")
        self.integration_tests = self.params.get("integration_tests")
        self.collection_name = self.params.get("collection_name")

        self.execute()

    def create_rewrite_script(self, commits):
        # create index file
        _, commit_path = tempfile.mkstemp(suffix=".txt")
        with open(commit_path, "w") as fw:
            fw.write(commits)

        # create rewrite file
        content = [
            "#!/usr/bin/env python3",
            "",
            "import os",
            "import sys",
            "import pathlib",
            "",
            "lines = sys.stdin.readlines()",
            "",
            "def pop_sha1():",
            "    sha1_file = pathlib.PosixPath('{0}')".format(commit_path),
            "    sha1_list = sha1_file.read_text().rstrip().split('\\n')",
            "    sha1_file.write_text('\\n'.join(sha1_list[:-1]))",
            "    return sha1_list[-1]",
            "",
            'sys.stdout.write("[promoted]")',
            "for l in lines:",
            "    sys.stdout.write(l)",
            "",
            "sha1 = pop_sha1()",
            f'print("\\n\\nThis commit was initially merged in https://github.com/ansible-collections/{self.collection_name}")',
            f'print("See: https://github.com/ansible-collections/{self.collection_name}/commit/" + sha1)',
        ]
        _, py_path = tempfile.mkstemp(suffix=".py")
        with open(py_path, "w") as fw:
            fw.write("\n".join(content))

        return commit_path, py_path

    def create_index_filter(self):

        f_modules = [f"plugins/modules/{x}.py" for x in self.modules]
        f_tests = [f"tests/integration/targets/{x}/" for x in self.modules + self.integration_tests]

        content = [
            "#!/usr/bin/env python3",
            "",
            "import sys",
            "",
            f"f_modules = {f_modules}",
            f"f_tests = {f_tests}",
            "",
            "for file in sys.stdin.readlines():",
            "   if any(file.startswith(x) for x in f_tests + f_modules):",
            "       continue",
            "   print(file)",
        ]

        _, path = tempfile.mkstemp(suffix=".py")
        with open(path, "w") as fw:
            fw.write("\n".join(content))

        return path

    def execute(self):
        # create migration branch with 'upstream/main' as base
        command = ["git", "checkout", "-B", self.branch, "upstream/main"]
        self.run_command(command, check_rc=True, cwd=self.path, use_unsafe_shell=True)

        # display log topology order
        command = ["git", "log", "--pretty=tformat:%H", "--topo-order"]
        _, stdout, _ = self.run_command(command, check_rc=True, cwd=self.path, use_unsafe_shell=True)
        commit_path, py_path = self.create_rewrite_script(stdout)

        # Rewrite commits
        command = ["git", "filter-branch", "-f", "--msg-filter", '"python3 {0}"'.format(py_path)]
        squelch_warn = {"FILTER_BRANCH_SQUELCH_WARNING": "1"}
        _, stdout, _ = self.run_command(" ".join(command), check_rc=True, cwd=self.path, use_unsafe_shell=True, environ_update=squelch_warn)

        self.add_cleanup_file(commit_path)
        self.add_cleanup_file(py_path)

        # Remove all the files, except the modules we want to keep
        filter_path = self.create_index_filter()
        command = [
            "git",
            "filter-branch",
            "-f",
            "--prune-empty",
            "--index-filter",
            "'git ls-tree -r --name-only --full-tree $GIT_COMMIT | python3 {0} | xargs git rm --cached --ignore-unmatch -r -f'".format(filter_path),
            "--",
            "HEAD",
        ]

        _, stdout, _ = self.run_command(" ".join(command), check_rc=True, cwd=self.path, use_unsafe_shell=True, environ_update=squelch_warn)
        self.add_cleanup_file(filter_path)

        # Generate the patch files
        command = "git format-patch -10000 " + self.branch
        self.run_command(command, check_rc=True, cwd=self.path, use_unsafe_shell=True, environ_update=squelch_warn)

        files = glob.glob("{0}/*.patch".format(self.path))

        self.exit_json(changed=True, files=files)


def main():
    CreatePatches()


if __name__ == "__main__":
    main()