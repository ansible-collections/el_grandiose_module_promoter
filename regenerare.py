import sys
import os
import subprocess
import ruamel.yaml


community_path = sys.argv[1]
amazon_path = sys.argv[2]
module = sys.argv[3]


def load_file(path):
    if 'community' in path:
        try: 
            os.mkdir(f"{community_path}/meta") 
        except OSError as error: 
            print(error)
        subprocess.call(f"git -C {community_path} cat-file --textconv 'origin/main:meta/runtime.yml' > {community_path}/meta/runtime.yml", shell=True)

    data = ruamel.yaml.load(open(f"{path}/meta/runtime.yml"), Loader=ruamel.yaml.RoundTripLoader)

    return data 


def dump_to_file(data, path):
    with open(path, 'w') as yaml_file:
        ruamel.yaml.dump(data, yaml_file, Dumper=ruamel.yaml.RoundTripDumper)


def update_actions_group(data, to_be_migrated):
    to_be_updated = []
    current = data['action_groups']['aws']
    to_be_updated = [x for x in current if x not in to_be_migrated]
    data['action_groups']['aws'] = to_be_updated

    return data


def update_plugin_routing(data, to_be_migrated):
    for name in to_be_migrated:
        if name in data['plugin_routing']['modules']:
            data['plugin_routing']['modules'].pop(name)
        else:
            data['plugin_routing']['modules'][name] = {"redirect": f"amazon.aws.{name}"}

    return data


def add_changelog(to_be_migrated):
    changelog_to = {}
    changelog_from = {}
    changelog_to['major_changes'] = []
    changelog_from['breaking_changes'] = []

    try: 
        os.makedirs(f"{community_path}/changelogs/fragments") 
    except OSError as error: 
        print(error)

    for module_name in to_be_migrated:
        _module_name = module_name
        if '_facts' in module_name:
            module_name = module_name.replace("_facts", "_info")
        msg = f"""{_module_name} - The module has been migrated from the ``community.aws`` collection. Playbooks using the Fully Qualified Collection Name for this module should be updated to use ``amazon.aws.{module_name}``."""
        changelog_to['major_changes'].append(msg)
        changelog_from['breaking_changes'].append(msg)

    dump_to_file(changelog_to, f"{amazon_path}/changelogs/fragments/migrate_{module}.yml")
    dump_to_file(changelog_from, f"{community_path}/changelogs/fragments/migrate_{module}.yml")


def ensure_and_dump_meta(data, path):
    dump_to_file(data, f"{path}/meta/runtime.yml")
    os.system(f"sed -i '' '/^ *$/d' {path}/meta/runtime.yml")
    os.system(f"sed -i '' $'1s/^/---\\\n/' {path}/meta/runtime.yml")


def regenerate():
    action_groups_to_be_added = []
    plugin_routing_to_be_added = {}
    com_data = load_file(community_path)
    am_data = load_file(amazon_path)

    for module_name in com_data['action_groups']['aws']:
        if module in module_name:
            action_groups_to_be_added.append(module_name)
    
    for key, value in com_data['plugin_routing']['modules'].items():
        if module in value.get('redirect'):
            plugin_routing_to_be_added[key] = com_data['plugin_routing']['modules'][key]
            com_data['plugin_routing']['modules'].pop(key) 

    if action_groups_to_be_added:
        am_data['action_groups']['aws'].extend(action_groups_to_be_added)
        com_data = update_actions_group(com_data, action_groups_to_be_added)
    
    if plugin_routing_to_be_added:
        am_data['plugin_routing']['modules'].update(plugin_routing_to_be_added)

    com_data = update_plugin_routing(com_data, action_groups_to_be_added)
    
    ensure_and_dump_meta(com_data, community_path)
    ensure_and_dump_meta(am_data, amazon_path)

    add_changelog(action_groups_to_be_added)


regenerate()