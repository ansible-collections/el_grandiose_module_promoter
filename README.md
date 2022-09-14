# AWS modules migration script from community.aws to amazon.aws

## Usage
Create a GitHub personal access token to use in place of a password with the API and set it within the username inside run.sh. In addition, please specify the name of the AWS module you want to migrate and the collections paths.
```bash
export GITHUB_TOKEN="Token ..."
export USERNAME="GitHub username"
module_to_migrate="Module name"
c_a_path="community.aws collection path"
a_a_path="amazon.aws collection path"
```

Finally, run the script.
```bash
$ ./run.sh
```

## License

GPLv3 or greater.
