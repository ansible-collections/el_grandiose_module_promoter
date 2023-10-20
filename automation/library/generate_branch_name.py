#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2023, Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: generate_branch_name
short_description: Generate branch name
author:
  - Aubin Bikouo (@abikouo)
description:
  - Generate branch name using random information.
options:
  prefix:
    description:
      - The branch prefix.
    required: false
    type: str
    default: 'promote'
"""

EXAMPLES = r"""
"""

RETURN = r"""
"""

from datetime import datetime
from os import getpid
from ansible.module_utils.basic import AnsibleModule


class GenerateBranchName(AnsibleModule):

    def __init__(self):
        
        specs = dict(
            prefix=dict(type="str", required=False, default="promote"),
        )

        super(GenerateBranchName, self).__init__(argument_spec=specs)
        self.execute()

    def execute(self):

        branch = "{0}_{1}_{2}".format(self.params.get("prefix"), datetime.now().strftime("%y%m%d%H%M"), getpid())
        self.exit_json(name=branch, changed=False)


def main():
    GenerateBranchName()


if __name__ == "__main__":
    main()
