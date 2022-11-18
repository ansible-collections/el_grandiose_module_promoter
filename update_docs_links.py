import sys
from pathlib import Path
from ruamel.yaml import YAML

from utils import load_file


module = sys.argv[1]
path = sys.argv[2]
name = sys.argv[3]

dest_action_group = name.split('.')[0]

def update_doc_links():
    to_be_migrated = []
    com_data = load_file(f"{path}/meta/runtime.yml")

    for module_name in com_data['action_groups'][dest_action_group]:
        if module in module_name:
            to_be_migrated.append(module_name)

    docs_pr = load_file(f"{path}/.github/workflows/docs-pr.yml")

    for module_name in to_be_migrated:
        docs_pr['jobs']['validate-docs']['with']['provide-link-targets'] += f"ansible_collections.{name}.{module_name}_module\n"
        docs_pr['jobs']['build-docs']['with']['provide-link-targets'] += f"ansible_collections.{name}.{module_name}_module\n"

    yaml = YAML(typ='rt')
    yaml.width = 4096
    file_docs_pr = Path(f"{path}/.github/workflows/docs-pr.yml")
    yaml.dump(docs_pr, file_docs_pr)

    docs_push = load_file(f"{path}/.github/workflows/docs-push.yml")

    for module_name in to_be_migrated:
        docs_push['jobs']['build-docs']['with']['provide-link-targets'] += f"ansible_collections.{name}.{module_name}_module\n"

    yaml = YAML(typ='rt')
    yaml.width = 4096
    file_push_pr = Path(f"{path}/.github/workflows/docs-push.yml")
    yaml.dump(docs_push, file_push_pr) 


update_doc_links()
