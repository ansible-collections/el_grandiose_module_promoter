import sys
import os
from glob import glob
import ruamel.yaml


collection_path = sys.argv[1]
collection_name = 'amazon.aws'
module = sys.argv[2]


def load_file(path):
    data = ruamel.yaml.load(open(path), Loader=ruamel.yaml.RoundTripLoader)

    return data


def dump_to_file(data, path):
    with open(path, 'w') as yaml_file:
        ruamel.yaml.dump(data, yaml_file, Dumper=ruamel.yaml.RoundTripDumper)


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