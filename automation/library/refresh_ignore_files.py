#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2023, Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: refresh_ignore_files
short_description: Refresh ignore files, from source collection to destination
author:
  - Aubin Bikouo (@abikouo)
description:
  - Move references for modules being migrated from source to destination collection
options:
  modules:
    description:
      - The name of the modules being migrated.
    required: true
    type: list
    elements: str
  integration_tests:
    description:
      - The integration tests targets being migrated.
    required: false
    type: list
    elements: str
  src:
    description:
      - The path to the source collection.
    required: true
    type: path
  dest:
    description:
      - The path to the destination collection.
    required: true
    type: path
"""

EXAMPLES = r"""
"""

RETURN = r"""
"""

import glob
import os
from pathlib import Path

from ansible.module_utils.basic import AnsibleModule


class RefreshIgnoreFiles(AnsibleModule):

    def __init__(self):
        
        specs = dict(
            modules=dict(type="list", elements="str", required=True),
            integration_tests=dict(type="list", elements="str", default=[]),
            src=dict(type="str", required=True,),
            dest=dict(type="str", required=True,),
        )

        super(RefreshIgnoreFiles, self).__init__(argument_spec=specs)
        self.execute()

    def refresh_ignore_file(self, ignore_file):
        to_be_removed = []
        src_ignore_file = os.path.join(self.params.get("src"), ignore_file)
        with open(src_ignore_file) as fd:
            ignore_content = fd.read().split("\n")
        _ignore_content = ignore_content.copy()
        _ignore_content = list(filter(None, ignore_content))

        for line in ignore_content:
            if any(line.startswith(x) for x in self.starts):
                to_be_removed.append(line)
                _ignore_content.remove(line)

        changed = False
        if to_be_removed:
            changed = True
            with open(src_ignore_file, "w") as fw:
                fw.write("\n".join(_ignore_content).lstrip("\n"))
            dest = self.params.get("dest")
            dest_ignore_dir = Path(dest) / "tests" / "sanity"
            dest_ignore_dir.mkdir(parents=True, exist_ok=True)
            dest_ignore_file = os.path.join(dest, ignore_file)
            with open(dest_ignore_file) as fd:
                current_content = fd.read().split("\n")
            current_content = list(filter(None, current_content))
            current_content.extend(to_be_removed)
            with open(dest_ignore_file) as fw:
                fw.write("\n".join(current_content).lstrip("\n"))

        return changed


    def execute(self):
        src = self.params.get("src")
        dest = self.params.get("dest")
        src_sanity = os.path.join(src, "tests/sanity")
        dst_sanity = os.path.join(dest, "tests/sanity")

        self.starts = [f"plugins/modules/{m}.py" for m in self.params.get("modules")]
        self.starts += [f"tests/integration/targets/{test}/" for test in self.params.get("integration_tests")]

        changed = False
        src_files, dest_files, versions = [], [], []
        if os.path.exists(src_sanity) and os.path.isdir(dst_sanity):
            for file in glob.glob(f"{src_sanity}/ignore-*.txt"):
                ignore_file = os.path.relpath(file, start=src)
                result = self.refresh_ignore_file(ignore_file)
                versions.append(os.path.basename(ignore_file).replace("ignore-", "").replace(".txt", ""))
                if result:
                    src_files.append(ignore_file)
                    dest_files.append(ignore_file)
                changed |= result

        self.exit_json(changed=changed, src_files=src_files, dest_files=dest_files, versions=versions)


def main():
    RefreshIgnoreFiles()


if __name__ == "__main__":
    main()
