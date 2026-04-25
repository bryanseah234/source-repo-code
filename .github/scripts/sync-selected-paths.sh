#!/usr/bin/env bash
set -euo pipefail

git config --global user.email "actions@github.com"
git config --global user.name "GitHub Actions Sync"

OWNER="${GITHUB_REPOSITORY_OWNER}"
SOURCE_REPO_NAME="${GITHUB_REPOSITORY##*/}"
WORKDIR="$(pwd)"
SYNC_ROOT="$(mktemp -d)"
FAILED_REPOS=()
PUSH_FAILED_REPOS=()

# Dot files/folders that are NEVER deleted from target repos
EXEMPT_DOTS=(
  ".git" ".github" ".gitignore" ".gitattributes" ".gitmodules"
  ".editorconfig" ".nvmrc" ".node-version" ".python-version" ".tool-versions"
  ".prettierrc" ".prettierrc.js" ".prettierrc.cjs" ".prettierrc.json"
  ".prettierrc.yml" ".prettierrc.yaml" ".prettierignore"
  ".eslintrc" ".eslintrc.js" ".eslintrc.cjs" ".eslintrc.json"
  ".eslintrc.yml" ".eslintrc.yaml" ".eslintignore"
  ".stylelintrc" ".stylelintrc.js" ".stylelintrc.json" ".stylelintrc.yml"
  ".babelrc" ".babelrc.js" ".babelrc.cjs" ".babelrc.json"
  ".browserslistrc" ".dockerignore"
  ".npmrc" ".yarnrc" ".yarnrc.yml" ".pnpmfile.cjs"
  ".env.example" ".env.template" ".env.sample"
  ".sourcery.yml" ".deepsource.toml" ".htaccess"
)

GITIGNORE_MARKER="# AI / editor dot directories (managed via sourcerepo)"

retry() {
  local attempts=0
  local max_attempts=3
  until "$@"; do
    attempts=$((attempts + 1))
    if [ "$attempts" -ge "$max_attempts" ]; then
      return 1
    fi
    sleep $((2 ** attempts))
  done
}

copy_if_exists() {
  local src="$1"
  local dst="$2"
  local dst_dir
  dst_dir="$(dirname "$dst")"
  mkdir -p "$dst_dir"

  if [ -f "$src" ]; then
    cp -f "$src" "$dst"
    echo "Copied file $src -> $dst"
  elif [ -d "$src" ]; then
    rm -rf "$dst"
    cp -r "$src" "$dst"
    echo "Copied directory $src -> $dst"
  else
    echo "Source missing, skipping copy: $src"
  fi
}

force_stage_path() {
  local path="$1"
  if [ -e "$path" ]; then
    git add -f "$path"
  else
    git add -A "$path" 2>/dev/null || true
  fi
}

# Delete all dot items at repo root that are not on the exemption list
delete_unlisted_dot_items() {
  for item in .[!.]* ; do
    [ -e "$item" ] || continue
    local exempt=false
    for e in "${EXEMPT_DOTS[@]}"; do
      [[ "$item" == "$e" ]] && exempt=true && break
    done
    if [ "$exempt" = false ]; then
      rm -rf "$item"
      echo "Deleted dot item: $item"
    fi
  done
}

# Delete all *.code-workspace files recursively (skip .git/)
delete_code_workspace_files() {
  find . -path "./.git" -prune -o -name "*.code-workspace" -print -exec rm -f {} \;
}

# Inject .gitignore entries — idempotent, uses broad .* pattern with exemptions
inject_gitignore_entries() {
  if grep -qF "$GITIGNORE_MARKER" .gitignore 2>/dev/null; then
    return
  fi
  cat >> .gitignore << 'GITIGNORE_BLOCK'

# AI / editor dot directories (managed via sourcerepo)
.*
!.github/
!.gitignore
!.gitattributes
!.gitmodules
!.editorconfig
!.nvmrc
!.node-version
!.python-version
!.tool-versions
!.prettierrc*
!.eslintrc*
!.stylelintrc*
!.babelrc*
!.browserslistrc
!.dockerignore
!.npmrc
!.yarnrc
!.yarnrc.yml
!.env.example
!.env.template
!.env.sample
!.sourcery.yml
!.deepsource.toml
skills/
skills-lock.json
docs/
templates/
GITIGNORE_BLOCK
  echo "Updated .gitignore with dot directory exclusions"
}

REPOS_JSON="$(gh api --paginate "user/repos?per_page=100&affiliation=owner" | jq -s 'add')"
echo "Owner: $OWNER"
echo "Source repo: $SOURCE_REPO_NAME"
echo "Found repos: $(echo "$REPOS_JSON" | jq length)"

while read -r repo; do
  REPO_NAME="$(echo "$repo" | jq -r '.name')"
  ARCHIVED="$(echo "$repo" | jq -r '.archived')"
  DISABLED="$(echo "$repo" | jq -r '.disabled')"
  FORKED="$(echo "$repo" | jq -r '.fork')"
  DEFAULT_BRANCH="$(echo "$repo" | jq -r '.default_branch')"

  if [ "$ARCHIVED" = "true" ] || [ "$DISABLED" = "true" ] || [ "$FORKED" = "true" ]; then
    echo "Skipping repo: $REPO_NAME"
    continue
  fi

  if [ "$REPO_NAME" = "$SOURCE_REPO_NAME" ]; then
    echo "Skipping source repo: $REPO_NAME"
    continue
  fi

  TARGET_DIR="$SYNC_ROOT/$REPO_NAME"
  echo "Processing $REPO_NAME..."

  if ! retry gh repo clone "$OWNER/$REPO_NAME" "$TARGET_DIR" -- --depth 1; then
    echo "Failed to clone $OWNER/$REPO_NAME, skipping."
    FAILED_REPOS+=("$REPO_NAME")
    continue
  fi

  cd "$TARGET_DIR" || {
    FAILED_REPOS+=("$REPO_NAME")
    continue
  }

  # Copy skills content from sourcerepo
  while IFS='|' read -r src dst; do
    [ -z "$src" ] && continue
    copy_if_exists "$WORKDIR/$src" "$dst"
    force_stage_path "$dst"
  done <<< "$SYNC_ITEMS"

  # Clean up dot items and .code-workspace files
  delete_unlisted_dot_items
  delete_code_workspace_files

  # Remove AI tool / generated dirs from git tracking
  for item in skills skills-lock.json docs templates; do
    [ -e "$item" ] && rm -rf "$item" && echo "Removed: $item"
  done

  # Inject .gitignore entries (idempotent)
  inject_gitignore_entries

  git add -A

  if [ -n "$(git status --porcelain)" ]; then
    git commit -m "$COMMIT_MESSAGE"
    if retry git push origin HEAD:"$DEFAULT_BRANCH"; then
      echo "Pushed changes to $REPO_NAME"
    else
      SYNC_BRANCH="sync-${GITHUB_RUN_ID}-${GITHUB_RUN_ATTEMPT}"
      git checkout -b "$SYNC_BRANCH"
      if git push origin "$SYNC_BRANCH"; then
        gh pr create --repo "$OWNER/$REPO_NAME" --title "$PR_TITLE" --body "$PR_BODY" --base "$DEFAULT_BRANCH" --head "$SYNC_BRANCH" || true
        echo "Opened PR for $REPO_NAME"
      else
        echo "Push failed for $REPO_NAME"
        PUSH_FAILED_REPOS+=("$REPO_NAME")
      fi
    fi
  else
    echo "No changes needed in $REPO_NAME, skipping push."
  fi

  cd "$WORKDIR" || exit 1
  rm -rf "$TARGET_DIR"
done < <(echo "$REPOS_JSON" | jq -c '.[] | {name, archived, disabled, fork, default_branch}')

if [ "${#FAILED_REPOS[@]}" -gt 0 ]; then
  echo "Clone failures: ${FAILED_REPOS[*]}"
fi
if [ "${#PUSH_FAILED_REPOS[@]}" -gt 0 ]; then
  echo "Push failures: ${PUSH_FAILED_REPOS[*]}"
fi
