#!/usr/bin/env bash
set -euo pipefail
cd src
go work init ./protocol  ./client ./server
go work use  ./protocol  ./client ./server
echo "go.work ready"
