#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2023, Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: identify_collection
short_description: Read collection information from galaxy.yml file.
author:
  - Aubin Bikouo (@abikouo)
description:
  - The module reads the namespace and name of the collection from galaxy.yml file.
options:
  path:
    description:
      - The path to the collection.
    required: true
    type: path
"""

EXAMPLES = r"""
- name: Identify collection from specified path
  identify_collection:
    path: ~/.ansible/collections/ansible_collections/amazon/aws
"""

RETURN = r"""
namespace:
    description: The collection namespace.
    type: str
    returned: always
name:
    description: The collection name.
    type: str
    returned: always
"""

import traceback
import os

try:
    import yaml

    IMP_YAML = True
    IMP_YAML_ERR = None
except ImportError:
    IMP_YAML_ERR = traceback.format_exc()
    IMP_YAML = False

from ansible.module_utils.basic import AnsibleModule, missing_required_lib


class IdentifyCollection(AnsibleModule):
    
    def __init__(self):
        
        specs = dict(
            path=dict(type="str", required=True,),
        )
        super(IdentifyCollection, self).__init__(argument_spec=specs)
        self.execute()

    def execute(self):
        
        galaxy_path = os.path.expanduser(os.path.join(self.params.get("path"), "galaxy.yml"))
        if not os.path.exists(galaxy_path):
            self.fail_json(msg="The following file '{0}' does exist.".format(galaxy_path))

        if not IMP_YAML:
          self.fail_json(msg=missing_required_lib("yaml"), exception=IMP_YAML_ERR)        

        with open(galaxy_path) as fd:
            data = yaml.safe_load(fd.read())
            self.exit_json(name=data.get("name"), namespace=data.get("namespace"))


def main():
    IdentifyCollection()


if __name__ == "__main__":
    main()
