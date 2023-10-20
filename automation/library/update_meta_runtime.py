#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2023, Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: update_meta_runtime
short_description: Regenerate collection
author:
  - Aubin Bikouo (@abikouo)
description:
  - The module updates meta/runtime.yml and add changelog fragment.
options:
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

import os
from pathlib import Path
import copy

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


def ensure_and_dump_meta(data, path):
    dump_to_file(data, f"{path}/meta/runtime.yml")

    runtime_file = Path(f"{path}/meta/runtime.yml")
    no_empty_lines = [l for l in runtime_file.read_text().split("\n") if l != ""]
    content = '\n'.join(no_empty_lines)
    if not content.startswith("---\n"):
        content = f"---\n{content}"
    runtime_file.write_text(content)


class Regenerate(AnsibleModule):
    
    def __init__(self):
        
        specs = dict(
            src=dict(type="path", required=True,),
            dest=dict(type="path", required=True,),
            modules=dict(type="list", elements="str", required=True,),
            src_name=dict(type="str", required=True,),
            dest_name=dict(type="str", required=True,),
        )

        super(Regenerate, self).__init__(argument_spec=specs)
        self.dest_action_group = self.params.get("dest_name").split(".")[1]
        self.dest_path = self.params.get("dest")
        self.src_path = self.params.get("src")
        self.modules = self.params.get("modules")
        self.src_name = self.params.get("src_name")
        self.dest_name = self.params.get("dest_name")

        self.changelog_to = {}
        self.changelog_from = {}
        self.changelog_to['major_changes'] = []
        self.changelog_from['breaking_changes'] = []

        self.execute()

    def add_changelog(self, to_be_migrated):
        for module_name in to_be_migrated:
            _module_name = module_name
            if '_facts' in module_name:
                module_name = module_name.replace("_facts", "_info")
            msg = f"""{_module_name} - The module has been migrated from the ``{self.src_name}`` collection. Playbooks using the Fully Qualified Collection Name for this module should be updated to use ``{self.dest_name}.{module_name}``."""
            self.changelog_to['major_changes'].append(msg)
            self.changelog_from['breaking_changes'].append(msg)

        os.makedirs(f"{self.dest_path}/changelogs/fragments", exist_ok=True)
        changelog_file = ""
        for module in self.modules:
            changelog_file += "_" + module

        dest_changelog = f"{self.dest_path}/changelogs/fragments/migrate_{changelog_file}.yml"
        dump_to_file(self.changelog_to, dest_changelog)
        src_changelog = f"{self.src_path}/changelogs/fragments/migrate_{changelog_file}.yml"
        dump_to_file(self.changelog_from, src_changelog)
        return [dest_changelog, src_changelog]

    def execute(self):

        try:

            action_groups_to_be_added = []
            plugin_routing_to_be_added = {}
            com_data = load_file(f"{self.src_path}/meta/runtime.yml")
            _com_data_cpy = copy.deepcopy(com_data)
            am_data = load_file(f"{self.dest_path}/meta/runtime.yml")
            _am_data_cpy = copy.deepcopy(am_data)

            for module in self.modules:
              for module_name in com_data['action_groups'][self.dest_action_group]:
                  if module in module_name and module not in action_groups_to_be_added:
                      action_groups_to_be_added.append(module_name)

              for key, value in com_data['plugin_routing']['modules'].items():
                  if value.get('redirect').endswith(module):
                      li = copy.deepcopy(value)
                      li['redirect'] = li['redirect'].replace(self.src_name, self.dest_name)
                      plugin_routing_to_be_added[key] = li
                      _com_data_cpy['plugin_routing']['modules'].pop(key)

            if action_groups_to_be_added:
                _am_data_cpy['action_groups'][self.dest_action_group].extend(action_groups_to_be_added)
                _am_data_cpy['action_groups'][self.dest_action_group].sort()
                # Remove items to migrated
                _com_data_cpy['action_groups'][self.dest_action_group] = [x for x in _com_data_cpy['action_groups'][self.dest_action_group] if x not in action_groups_to_be_added]

            if plugin_routing_to_be_added:
                _am_data_cpy['plugin_routing']['modules'].update(plugin_routing_to_be_added)
                _am_data_cpy['plugin_routing']['modules'] = dict(sorted(_am_data_cpy['plugin_routing']['modules'].items()))

            # Update source plugin routing
            for module in action_groups_to_be_added:
                if module in com_data['plugin_routing']['modules']:
                    com_data['plugin_routing']['modules'].pop(module)
                else:
                    com_data['plugin_routing']['modules'][module] = {"redirect": f"{self.dest_name}.{module}"}
            _com_data_cpy['plugin_routing']['modules'] = com_data['plugin_routing']['modules']
            _com_data_cpy['plugin_routing']['modules'] = dict(sorted(_com_data_cpy['plugin_routing']['modules'].items()))

            ensure_and_dump_meta(_com_data_cpy, self.src_path)
            ensure_and_dump_meta(_am_data_cpy, self.dest_path)

            changelogs = self.add_changelog(action_groups_to_be_added)
            self.exit_json(changed=True, changelogs=changelogs)

        except Exception as e:
            self.fail_json(msg="An error occurred while regenerating collection", exception=e)


def main():
    Regenerate()


if __name__ == "__main__":
    main()
