# Ansible Collection modules migration tool to move between two Collections inside the ansible-collections GitHub Org

## Requirements

- Create a GitHub personal access token to use in place of a password with the API.
- Collections forks exist in the user namespace.


## Using Github action

From the [repository](https://github.com/ansible-collections/el_grandiose_module_promoter)

- Click on ![action](https://github.com/ansible-collections/el_grandiose_module_promoter/blob/main/images/action.jpg?raw=true)

- Choose the action named ``migrate_modules``

- Click on ![run workflow](https://github.com/ansible-collections/el_grandiose_module_promoter/blob/main/images/run_workflow.jpg?raw=true)

- Fill the form the required parameters and click on ![run workflow](https://github.com/ansible-collections/el_grandiose_module_promoter/blob/main/images/execute_workflow.jpg.jpg?raw=true)

## Usage (on your local computer)

- clone the collection containing the modules to migrate (``community.aws``)
```bash
git clone https://github.com/{username}/community.aws path_to_clone_community_aws
```

- clone the collection where the modules will be migrated (``amazon.aws``)
```bash
git clone https://github.com/{username}/amazon.aws path_to_clone_amazon_aws
```

- Set environment variables for Github token and username
```bash
export GH_TOKEN=abcdefgh....
export GH_USERNAME=username
```

- Run the automation playbook as described [here](https://github.com/ansible-collections/el_grandiose_module_promoter/blob/main/automation/README.md)


## License

GPLv3 or greater.
