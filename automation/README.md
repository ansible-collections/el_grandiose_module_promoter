# A playbook to migrate modules from community to amazon upstream collection

## Requirements

- Forks for upstream collections exist in the user namespace
- A Github personal access token with permission to create pull requests.

## Playbook variables

- ``migration_src_path``: The path the source collection (path to clone of community.aws). **Required**
- ``migration_dst_path``: The path the destination collection (path to clone of amazon.aws). **Required**
- ``migration_src_repo_name``: The name of the source collection (community.aws). **Required**
- ``migration_dst_repo_name``: The name of the destination collection (amazon.aws). **Required**
- ``migration_modules``: The list of modules to migrate. **Required**
- ``migration_tests``: The list of integration tests to migrate. **Optional**
- ``migration_branch``: The branch name to use for migration. **Optional**

``GH_TOKEN`` environment variable should be defined with the personal access token.
``GH_USERNAME`` environment variable should be defined with the Github username.

## Usage

With the following variable file ``vars.yaml``

```yaml
---
migration_src_path: /path/to/community.aws
migration_dst_path: /path/to/amazon.aws
migration_src_repo_name: 'community.aws'
migration_dst_repo_name: 'amazon.aws'
migration_modules:
    - acm_certificate
    - iam_role_info
migration_tests:
    - iam_role_validate
    - acm_certificate_rule
```

Run the following command:

```bash
ansible-playbook migrate.yaml -e "@./vars.yaml" -v
```

## License

GPLv3 or greater.
