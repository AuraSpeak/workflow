#!/usr/bin/env bash
# Remove replace directives from go.mod under src/ (for clean state before push).
# Run from workflow repo root. Usage: strip-go-replace.sh [module]
# With no args: strip all src/*/go.mod. With module (e.g. client): strip only src/<module>/go.mod.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT/src"

strip_one() {
	local f="$1"
	[ -f "$f" ] || return 0
	awk '
		/^replace [^[:space:]]+ => .+$/ { next }
		/^replace[[:space:]]*\([[:space:]]*$/ { in_replace=1; next }
		in_replace {
			if (/^[[:space:]]*\)[[:space:]]*$/) in_replace=0
			next
		}
		{ print }
	' "$f" > "$f.tmp" && mv "$f.tmp" "$f"
}

if [ -n "${1:-}" ]; then
	strip_one "$1/go.mod"
	echo "Stripped replace directives from $1/go.mod"
else
	for m in $(cat "$ROOT/scripts/modules"); do
		strip_one "$m/go.mod"
	done
	echo "Stripped replace directives from go.mod files"
fi
