#!/bin/bash
# git_nuke.sh - The "Have you tried turning it off and on again?" for Git repositories.
# WARNING: This is destructive. It deletes all untracked files and resets to HEAD.

echo "☢️  INITIATING GIT NUKE PROTOCOL ☢️"
echo "This will:"
echo "  1. Reset all tracked files to match HEAD (hard reset)"
echo "  2. DELETE all untracked files and directories (clean -fdx)"
echo "  3. Re-make the repo pristine"
echo ""
read -p "Are you sure? (y/N) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 1
fi

echo "step 1/2: Resetting..."
git reset --hard HEAD

echo "step 2/2: Cleaning..."
git clean -fdx

echo "✨ Pristine. Your repo is now exactly as it is on the remote (if you pulled)."
