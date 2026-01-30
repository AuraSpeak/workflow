#!/usr/bin/env bash
set -euo pipefail
ORG="https://github.com/AuraSpeak"
mkdir -p src && cd src
for r in protocol client server debug-ui network; do
  [ -d "$r" ] || git clone "$ORG/$r.git"
done
