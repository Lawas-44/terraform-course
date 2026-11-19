#!/usr/bin/env bash
# Borra todo lo creado para no pagar por ello.
set -euo pipefail
cd "$(dirname "$0")/.."
terraform -chdir=terraform destroy
