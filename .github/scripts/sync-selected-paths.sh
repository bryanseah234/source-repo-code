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

  while IFS='|' read -r src dst; do
    [ -z "$src" ] && continue
    copy_if_exists "$WORKDIR/$src" "$dst"
  done <<< "$SYNC_ITEMS"

  ### Delete .agent/ directory (old setup)
  if [ -d ".agent" ]; then
    rm -rf .agent
    echo "Deleted .agent directory (old setup)"
  fi

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
