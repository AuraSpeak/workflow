#!/usr/bin/env bash
# Create go.work and inject local replace directives into each go.mod.
# Run from workflow repo root.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT/src"
rm -f go.work go.work.sum
go work init $(tr ' ' '\n' < "$ROOT/scripts/modules" | sed 's/^/.\//' | paste -sd' ')
"$ROOT/scripts/inject-go-replace.sh"
echo "go.work ready"
