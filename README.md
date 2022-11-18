# Ansible Collection modules migration script to move between two Collections

## Usage
Create a GitHub personal access token to use in place of a password with the API and set it within the username inside run.sh. In addition, please specify the name of the module you want to migrate and the collections paths.

The below paths should correlate to the location of these collections git clone locations on your computer.
```bash
export GITHUB_TOKEN="Token ..."
export USERNAME="GitHub username"
module_to_migrate="Module name"
src_collection_name="srcnamespace.name"
src_collection_path="source (original) collection path"
dest_collection_name="destnamespace.name"
dest_collection_path="destination collection path"
```

Finally, run the script.
```bash
$ ./run.sh
```

## License

GPLv3 or greater.
