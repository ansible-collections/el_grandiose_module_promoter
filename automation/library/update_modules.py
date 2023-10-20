#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2023, Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: update_modules
short_description: Update source collection name from module file
author:
  - Aubin Bikouo (@abikouo)
description:
  - This will replace the FQDN of the source collection by the FQDN of the destination collection.
  - Add the 'version_added_collection' into module documentation.
  - Replace 'community.aws' header with 'amazon.aws' header.
options:
  path:
    description:
      - The path to the collection to update.
    required: true
    type: path
  modules:
    description:
      - The modules being migrated.
    required: true
    type: list
    elements: str
  src_name:
    description:
      - The source collection name.
    required: true
    type: path
  dest_name:
    description:
      - The destination collection name.
    required: true
    type: path
"""

EXAMPLES = r"""
"""

RETURN = r"""
"""

import glob
import os
from ansible.module_utils.basic import AnsibleModule
import copy


class UpdateModule(AnsibleModule):
    
    def __init__(self):
        
        specs = dict(
            path=dict(type="path", required=True,),
            modules=dict(type="list", elements="str", required=True,),
            src_name=dict(type="str", required=True,),
            dest_name=dict(type="str", required=True,),
        )

        super(UpdateModule, self).__init__(argument_spec=specs)
        self.path = self.params.get("path")
        self.src_name = self.params.get("src_name")
        self.dst_name = self.params.get("dest_name")
        self.modules = self.params.get("modules")
        self.execute()

    def execute(self):

        modules = []
        changed = False
        version_added_collection = "version_added_collection: {}".format(self.src_name)
        for mod_name in self.modules:
            file = f"{self.path}/plugins/modules/{mod_name}.py"
            with open(file) as fd:
                content = fd.read()
            new_content = copy.deepcopy(content)
            new_content = new_content.replace(f"{self.src_name}.{mod_name}", f"{self.dst_name}.{mod_name}")
            new_content = new_content.replace(f'collection_name="{self.src_name}"', f'collection_name="{self.dst_name}"')
            # Replace community.aws module include
            community_import = "from ansible_collections.community.aws.plugins.module_utils.modules import AnsibleCommunityAWSModule as AnsibleAWSModule"
            amazon_import = "from ansible_collections.amazon.aws.plugins.module_utils.modules import AnsibleAWSModule"
            new_content = new_content.replace(community_import, amazon_import)
            # add 'version_added_collection'
            if version_added_collection not in new_content:
                content_list = new_content.split("\n")
                for id, value in enumerate(content_list):
                    if value.startswith('version_added:'):
                        content_list.insert(id+1, version_added_collection)
                        break
                new_content = "\n".join(content_list)
            if new_content != content:
                changed |= True
                with open(file, "w") as fw:
                    fw.write(new_content)
                modules.append(mod_name)
        self.exit_json(changed=changed, modules=modules)


def main():
    UpdateModule()


if __name__ == "__main__":
    main()
