#!/usr/bin/env bash
# Idempotently inject local replace directives into each go.mod for local development.
# Run from workflow repo root. Strips existing replace blocks first, then appends new ones.
# These must be stripped before push; see scripts/strip-go-replace.sh and pre-push hook.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT/src"

# Strip any existing replace blocks so we can re-inject (idempotent)
"$ROOT/scripts/strip-go-replace.sh"

# Inject replace directives so modules resolve to ../ within src/
printf '\nreplace github.com/auraspeak/protocol => ../protocol\n' >> network/go.mod
printf '\nreplace (\n\tgithub.com/auraspeak/network => ../network\n\tgithub.com/auraspeak/protocol => ../protocol\n)\n' >> client/go.mod
printf '\nreplace (\n\tgithub.com/auraspeak/network => ../network\n\tgithub.com/auraspeak/protocol => ../protocol\n)\n' >> server/go.mod
printf '\nreplace github.com/auraspeak/server => ../server\nreplace github.com/auraspeak/client => ../client\nreplace github.com/auraspeak/protocol => ../protocol\n' >> debug-ui/go.mod

echo "Replace directives injected into go.mod files"
