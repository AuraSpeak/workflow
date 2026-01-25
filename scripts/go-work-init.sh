#!/usr/bin/env bash
set -euo pipefail
cd src
go work init ./protocol ./router ./client ./server
go work use  ./protocol ./router ./client ./server
echo "go.work ready"
