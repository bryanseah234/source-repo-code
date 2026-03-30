---
description: Standard process for creating, reviewing, and merging Pull Requests
---

// standard-pr-process

## Context
This workflow guides the AI and the user through the standard process of finalizing a feature and preparing it for merge into the main branch.

## Steps

### 1. Pre-commit Checks
1. Ensure all code changes are saved.
2. Run any available local linters or formatters (e.g., `npm run lint`, `flake8`, `black`, `prettier`).
3. Run the local test suite (e.g., `npm test`, `pytest`) to ensure no existing functionality is broken.

### 2. Commit Changes
1. Stage the changes: `git add .` (or add specific files).
2. Create a commit message following the Conventional Commits specification (see `git-best-practices.md`).
   - Example: `git commit -m "feat(auth): implement JWT token validation"`

### 3. Push and PR Creation
1. Push the branch to the remote repository: `git push origin HEAD`
2. Generate a PR description. The description should include:
   - **What**: Summary of the changes.
   - **Why**: The problem being solved or the feature being added.
   - **How to test**: Steps for the reviewer to verify the changes locally.
3. Open the Pull Request via the GitHub UI or CLI (`gh pr create`).

### 4. CI/CD and Review
1. Wait for GitHub Actions (CI) to pass. If TruffleHog or other checks fail, investigate and fix the issues.
2. Request a review from team members (if applicable).

### 5. Merge
1. Once approved and CI is green, use the "Squash and Merge" strategy to merge the PR into `main`.
2. Delete the remote feature branch.