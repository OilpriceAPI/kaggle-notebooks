#!/usr/bin/env python3
"""Build Kaggle CLI upload directories without committing generated copies."""

from __future__ import annotations

import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist" / "kaggle"
PACKAGES = {
    "oilpriceapi-wti-vs-brent": {
        "notebook": "01_wti_brent_spread_analysis.ipynb",
        "title": "WTI and Brent Spread Analysis with Source Context",
    },
    "oil-price-technical-analysis": {
        "notebook": "02_oil_price_technical_analysis.ipynb",
        "title": "API-Timestamped Brent Technical Indicators",
    },
}


def main() -> None:
    if DIST.exists():
        shutil.rmtree(DIST)
    for slug, package in PACKAGES.items():
        destination = DIST / slug
        destination.mkdir(parents=True)
        notebook = package["notebook"]
        shutil.copy2(ROOT / notebook, destination / notebook)
        metadata = {
            "id": f"kwaldman/{slug}",
            "title": package["title"],
            "code_file": notebook,
            "language": "python",
            "kernel_type": "notebook",
            "is_private": False,
            "enable_gpu": False,
            "enable_internet": True,
            "dataset_sources": [],
            "competition_sources": [],
            "kernel_sources": [],
        }
        (destination / "kernel-metadata.json").write_text(
            json.dumps(metadata, indent=2, sort_keys=True) + "\n"
        )
        print(f"packaged {metadata['id']}")


if __name__ == "__main__":
    main()
