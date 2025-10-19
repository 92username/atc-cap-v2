#!/bin/bash
#
# Add & commit remote scripts to Git
#
# Convenience script to stage all scripts and commit them
#

cd "$(dirname "$0")/../"

echo "Adding scripts to Git..."
git add scripts/
git status

echo ""
echo "Ready to commit. Run:"
echo "  git commit -m 'Add remote script execution system'"
echo "  git push"
