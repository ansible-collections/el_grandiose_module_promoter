#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2023, Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: update_tests
short_description: Update collection reference from integration tests
author:
  - Aubin Bikouo (@abikouo)
description:
  - This module remove the collections key word from integration tests.
options:
  collection_path:
    description:
      - The path to the collection.
    required: true
    type: path
  collection_name:
    description:
      - The collection name.
    required: true
    type: str
  targets:
    description:
      - The test target name.
    required: true
    type: list
    elements: str
"""

EXAMPLES = r"""
"""

RETURN = r"""
"""

import os
import glob

import ruamel.yaml

from ansible.module_utils.basic import AnsibleModule


def load_file(file):
    with open(file, 'r') as _f:
        return ruamel.yaml.round_trip_load(_f.read(), preserve_quotes=True)


def dump_to_file(data, path):
    with open(path, 'w') as yaml_file:
        yaml = ruamel.yaml.YAML()
        yaml.preserve_quotes = True
        yaml.indent(mapping=2, sequence=4, offset=2)
        yaml.explicit_start = True
        yaml.dump(data, yaml_file)


class UpdateIntegrationTests(AnsibleModule):

    def __init__(self):
        
        specs = dict(
            collection_path=dict(type="path", required=True,),
            targets=dict(type="list", elements="str", required=True,),
            collection_name=dict(type="str", required=True,),
        )

        super(UpdateIntegrationTests, self).__init__(argument_spec=specs)
        self.collection_name = self.params.get("collection_name")
        self.collection_path = self.params.get("collection_path")
        self.targets = self.params.get("targets")
        self.execute()

    def update_target(self, target):
        files = []
        pattern = '*.yml'

        test_path = f"{self.collection_path}/tests/integration/targets/{target}/"
        if os.path.exists(test_path) and os.path.isdir(test_path):
            for dir,_,_ in os.walk(test_path):
                files.extend(glob.glob(os.path.join(dir, pattern)))

        changed = False
        for file_path in files:
            if data := load_file(file_path):
                updated = False
                for d in data:
                    if isinstance(d, dict) and d.get('collections'):
                        try:
                            d.get('collections').remove(self.collection_name)
                            updated = True
                        except ValueError:
                            pass
                        if len(d['collections']) == 0:
                            d.pop('collections')
                            updated = True
                if updated:
                    dump_to_file(data, file_path)
                changed |= updated

        return changed

    def execute(self):
        changed, updated_targets = False, []
        for target in self.targets:
            changed |= self.update_target(target)
            updated_targets.append(target)

        self.exit_json(changed=changed, updated_targets=updated_targets)


def main():
    UpdateIntegrationTests()


if __name__ == "__main__":
    main()
