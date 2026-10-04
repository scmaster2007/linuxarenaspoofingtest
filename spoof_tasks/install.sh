#!/bin/bash
# Install the transcript-spoofing side tasks into a Control Tower checkout.
# Usage: ./spoof_tasks/install.sh [path-to-control-tower]   (default: ./control-tower)
set -euo pipefail
CT="${1:-control-tower}"
DEST="$CT/.settings/linuxarena/shared_dotfiles/side_tasks"
if [ ! -d "$DEST" ]; then
  echo "error: $DEST not found. Pull the env first:  (cd $CT && uv run ct settings pull linuxarena)" >&2
  exit 1
fi
HERE="$(cd "$(dirname "$0")" && pwd)"
rsync -a --exclude '__pycache__' "$HERE/side_tasks/" "$DEST/"
echo "Installed spoof tasks into $DEST"
echo "Verify:  (cd $CT && uv run ct envs side-tasks list -e shared_dotfiles | grep spoof)"
