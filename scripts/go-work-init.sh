#!/usr/bin/env bash
set -euo pipefail
cd src
rm -f go.work go.work.sum
go work init ./protocol ./client ./server ./debug-ui ./network
echo "go.work ready"
