#!/usr/bin/env bash
set -euo pipefail

export GITHUB_TOKEN="Token ..."
export USERNAME="GitHub username"
module_to_migrate="module name"
src_collection_name="srcnamespace.name"
src_collection_path="community.aws collection path"
dest_collection_name="destnamespace.name"
dest_collection_path="amazon.aws collection path"

# quick sanity checks
if ! [ -d "${src_collection_path}" ]; then
    printf "ERROR: provided value for src_collection_path is not a directory: ${src_collection_path}\n"
fi
if ! [ -d "${dest_collection_path}" ]; then
    printf "ERROR: provided value for dest_collection_path is not a directory: ${dest_collection_path}\n"
fi
if [ -z ${src_collection_name%.*} ]; then
    printf "ERROR: Collection namespace not found in provided value for src_collection_name: ${src_collection_name}\n"
fi
if [ -z ${dest_collection_name%.*} ]; then
    printf "ERROR: Collection namespace not found in provided value for dest_collection_name: ${dest_collection_name}\n"
fi

main_folder_scripts=$(pwd)

cd ${src_collection_path}

git checkout origin/main

git checkout -B promote_$module_to_migrate origin/main

# --topo-order to be consistent with git filter-branch behavior
git log --pretty=tformat:%H --topo-order > /tmp/change_sha1.txt

# add an URL pointing on the original commit in the commit message
FILTER_BRANCH_SQUELCH_WARNING=1 git filter-branch -f --msg-filter "python3 $main_folder_scripts/rewrite.py $src_collection_name"

# remove all the files, except the modules we want to keep
FILTER_BRANCH_SQUELCH_WARNING=1 git filter-branch -f --prune-empty --index-filter 'git ls-tree -r --name-only --full-tree $GIT_COMMIT | \
   grep -v "^plugins/modules/'$module_to_migrate'*" | \
   grep -v "^tests/integration/targets/'$module_to_migrate'*" | \
   xargs git rm --cached --ignore-unmatch -r -f' -- HEAD

# generate the patch files
git format-patch -10000 promote_$module_to_migrate

# apply the patch files
cd ${dest_collection_path}
git am --abort || true
git checkout -B promote_$module_to_migrate origin/main
git am ${src_collection_path}/*.patch

cd ${src_collection_path}
git checkout origin/main
git branch -D promote_$module_to_migrate
git checkout -B promote_$module_to_migrate origin/main

git ls-files -c -o -i -x "*${module_to_migrate}*" | git update-index --force-remove --stdin
git add -u
git commit -m "Remove modules"
git clean -ffdx

${main_folder_scripts}/refresh_ignore_files $module_to_migrate ${src_collection_path} ${dest_collection_path}
echo `git add tests/sanity/*.txt && git commit -m "Update ignore files"`

python3 $main_folder_scripts/regenerare.py ${src_collection_path} ${dest_collection_path} $module_to_migrate ${src_collection_name} ${src_collection_name}

cd ${dest_collection_path}
echo `git add meta/runtime* && git commit -m "Update runtime"`

sed -i "s/$src_collection_name.$module_to_migrate/$dest_collection_name.$module_to_migrate/g" plugins/modules/$module_to_migrate*
sed -i "s/collection_name='$src_collection_name'/collection_name='$dest_collection_name'/g" plugins/modules/$module_to_migrate*
git add plugins/modules/$module_to_migrate*
git commit -m "Update FQDN"

python $main_folder_scripts/clean_tests.py ${dest_collection_path} ${dest_collection_name} $module_to_migrate
echo `git add tests/integration/targets/$module_to_migrate/* && git commit -m "Remove collection reference inside the tests"`

git add changelogs/fragments/migrate_$module_to_migrate.yml
git commit -m "Add changelog fragment"

echo `git add tests/sanity/*.txt && git commit -m "Update ignore files"`

git push origin promote_$module_to_migrate --force

cd ${src_collection_path}
git add meta/runtime*
git commit -m "Update runtime"
git add changelogs/fragments/migrate_$module_to_migrate.yml
git commit -m "Add changelog fragment"
git push origin promote_$module_to_migrate --force

sleep 10
python $main_folder_scripts/open_pr_module_migration.py $module_to_migrate promote_$module_to_migrate ${src_collection_name} ${dest_collection_name}
