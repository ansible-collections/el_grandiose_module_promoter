import sys
import os
from glob import glob
import ruamel.yaml


collection_path = sys.argv[1]
collection_name = sys.argv[2]
module = sys.argv[3]


def load_file(path):
    return ruamel.yaml.YAML().load(open(path))


def dump_to_file(data, path):
    with open(path, 'w') as yaml_file:
        yaml = ruamel.yaml.YAML()
        yaml.dump(data, yaml_file)


def get_files():
    files = []
    pattern = '*.yml'

    for dir,_,_ in os.walk(f"{collection_path}/tests/integration/targets/{module}/"):
        files.extend(glob(os.path.join(dir, pattern)))

    return files


def clean_tests():
    files = get_files()
    for file_path in files:
        if data := load_file(file_path):
            for d in data:
                if isinstance(d, dict) and d.get('collections'):
                    try:
                        d.get('collections').remove(collection_name)
                    except ValueError:
                        pass
                    if len(d['collections']) == 0:
                        d.pop('collections')

            dump_to_file(data, file_path)


clean_tests()
