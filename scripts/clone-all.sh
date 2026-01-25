#!/usr/bin/env bash
set -euo pipefail
ORG="https://github.com/aura-speak"
mkdir -p src && cd src
for r in protocol router client server debug-ui; do
  [ -d "$r" ] || git clone "$ORG/$r.git"
done
