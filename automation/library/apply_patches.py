#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2023, Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: apply_patches
short_description: Apply git patch
author:
  - Aubin Bikouo (@abikouo)
description:
  - Apply git patch on repository.
options:
  path:
    description:
      - The path to the git repository.
    required: true
    type: path
  patches:
    description:
      - The list of patches to apply to the repository.
    required: true
    type: list
    elements: path
"""

EXAMPLES = r"""
"""

RETURN = r"""
"""
import re
import os
from ansible.module_utils.basic import AnsibleModule


class ApplyPatch(AnsibleModule):
    
    def __init__(self):

        argument_specs = dict(
            path=dict(required=True, type="path"),
            patches=dict(required=True, type="list", elements="path"),
        )

        super(ApplyPatch, self).__init__(argument_spec=argument_specs)
        self.patches = sorted(self.params.get("patches"))
        self.path = self.params.get("path")
        self.execute()

    def execute(self):

        for id, patch in enumerate(self.patches):
            rc, stdout, stderr = self.run_command(
                "git am {}".format(patch),
                check_rc=False,
                cwd=self.path,
                use_unsafe_shell=True
            )
            if rc != 0:
                err = "error while applying patch '{0}' ({1} out of {2})".format(patch, id, len(self.patches))
                self.fail_json(msg=err, rc=rc, stdout=stdout, stderr=stderr)
        self.exit_json(changed=True, msg="{} successfully applied".format(len(self.patches)))


def main():
    ApplyPatch()


if __name__ == "__main__":
    main()