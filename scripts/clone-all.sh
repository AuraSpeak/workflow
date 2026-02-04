#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ORG="https://github.com/AuraSpeak"
mkdir -p "$ROOT/src" && cd "$ROOT/src"
for r in $(cat "$ROOT/scripts/modules"); do
	[ -d "$r" ] || git clone "$ORG/$r.git"
done
