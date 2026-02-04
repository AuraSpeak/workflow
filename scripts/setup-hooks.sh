#!/usr/bin/env bash
# Install pre-push hook in workflow root and in each module repo under src/.
# Run from workflow root. Use: just install-hooks or just setup.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

install_hook() {
	local d="$1"
	[ -d "$d" ] || return 0
	cp "$ROOT/scripts/pre-push.stub" "$d/pre-push"
	chmod +x "$d/pre-push"
}

install_hook "$ROOT/.git/hooks"
for mod in $(cat "$ROOT/scripts/modules"); do
	[ -d "$ROOT/src/$mod/.git" ] && install_hook "$ROOT/src/$mod/.git/hooks"
done
echo "Pre-push hooks installed (root + src/*)."
