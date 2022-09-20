#!/usr/bin/env bash
set -euo pipefail

export GITHUB_TOKEN="Token ..."
export USERNAME="GitHub username"
module_to_migrate="module name"
c_a_path="community.aws collection path"
a_a_path="amazon.aws collection path"

main_folder_scripts=$(pwd)

cd ${a_a_path}
git clean -ffdx
git reset --hard
git am --abort || true

cd ${c_a_path}
git clean -ffdx
git reset --hard
git am --abort || true
git fetch --all
git checkout -B promote_$module_to_migrate origin/main

# --topo-order to be consistent with git filter-branch behavior
git log --pretty=tformat:%H --topo-order > /tmp/change_sha1.txt

# add an URL pointing on the original commit in the commit message
FILTER_BRANCH_SQUELCH_WARNING=1 git filter-branch -f --msg-filter "python3 $main_folder_scripts/rewrite.py"

# remove all the files, except the modules we want to keep
FILTER_BRANCH_SQUELCH_WARNING=1 git filter-branch -f --prune-empty --index-filter 'git ls-tree -r --name-only --full-tree $GIT_COMMIT | \
   grep -v "^plugins/modules/'$module_to_migrate'*" | \
   grep -v "^tests/integration/targets/'$module_to_migrate'*" | \
   xargs git rm --cached --ignore-unmatch -r -f' -- HEAD

# generate the patch files
git format-patch -10000 promote_$module_to_migrate

# apply the patch files
cd ${a_a_path}
git checkout -B promote_$module_to_migrate origin/main
git am ${c_a_path}/*.patch

cd ${c_a_path}
git checkout origin/main
git branch -D promote_$module_to_migrate
git checkout -B promote_$module_to_migrate origin/main

git ls-files -c -o -i -x "*${module_to_migrate}*" | git update-index --force-remove --stdin
git add -u
git commit -m "Remove modules"
git clean -ffdx

${main_folder_scripts}/refresh_ignore_files $module_to_migrate ${c_a_path} ${a_a_path}
echo `git add tests/sanity/*.txt && git commit -m "Update ignore files"`

python3 $main_folder_scripts/regenerare.py ${c_a_path} ${a_a_path} $module_to_migrate

cd ${a_a_path}
echo `git add meta/runtime* && git commit -m "Update runtime"`

sed -i '' "s/community.aws.$module_to_migrate/amazon.aws.$module_to_migrate/g" plugins/modules/$module_to_migrate*
sed -i '' "s/collection_name='community.aws'/collection_name='amazon.aws'/g" plugins/modules/$module_to_migrate*
git add plugins/modules/$module_to_migrate*
git commit -m "Update FQDN"

python $main_folder_scripts/clean_tests.py ${a_a_path} $module_to_migrate
echo `git add tests/integration/targets/$module_to_migrate/* && git commit -m "Remove collection reference inside the tests"`

git add changelogs/fragments/migrate_$module_to_migrate.yml
git commit -m "Add changelog fragment"

echo `git add tests/sanity/*.txt && git commit -m "Update ignore files"`

git push origin promote_$module_to_migrate --force

cd ${c_a_path}
git add meta/runtime*
git commit -m "Update runtime"
git add changelogs/fragments/migrate_$module_to_migrate.yml
git commit -m "Add changelog fragment"
git push origin promote_$module_to_migrate --force

sleep 10
python $main_folder_scripts/open_pr.py $module_to_migrate promote_$module_to_migrate
