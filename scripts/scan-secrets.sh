#!/usr/bin/env bash
set -euo pipefail

root_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$root_dir"

failed=0
scan() {
  local label="$1"
  local pattern="$2"
  local matches
  matches="$(rg -l --hidden --glob '!.git/**' --glob '!scripts/scan-secrets.sh' "$pattern" . || true)"
  if [[ -n "$matches" ]]; then
    printf 'Potential %s found in:\n%s\n' "$label" "$matches" >&2
    failed=1
  fi
}

scan "64-character credential" '[A-Fa-f0-9]{64}'
scan "OilPriceAPI token" '(oilpriceapi_|opa_)[A-Za-z0-9_-]{20,}'
scan "assigned API credential" '(api[_ -]?key|token)[[:space:]]*[:=][[:space:]]*"?[A-Za-z0-9_-]{32,}'

if [[ "$failed" -ne 0 ]]; then
  exit 1
fi

echo "secret scan passed"
