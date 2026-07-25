#!/usr/bin/env bash
set -euo pipefail

repo_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_dir"

notebooks=(
  "01_wti_brent_spread_analysis.ipynb"
  "02_oil_price_technical_analysis.ipynb"
)

if ! python3 -c 'import matplotlib, numpy, oilpriceapi, pandas, seaborn' 2>/dev/null; then
  echo 'Missing notebook dependencies.' >&2
  echo 'Install: python3 -m pip install "oilpriceapi[pandas]==1.11.0" matplotlib seaborn' >&2
  exit 1
fi

python3 scripts/generate_notebooks.py
git diff --exit-code -- "${notebooks[@]}"

./scripts/scan-secrets.sh

for notebook in "${notebooks[@]}"; do
  python3 -m json.tool "$notebook" >/dev/null
done

python3 -m unittest discover -s tests -v
python3 scripts/package_kaggle.py

echo "Kaggle pre-upload validation passed."
