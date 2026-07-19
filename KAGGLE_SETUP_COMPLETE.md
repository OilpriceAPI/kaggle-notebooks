# Kaggle Publication Checklist

This repository contains reference notebooks for OilPriceAPI analysis. Public
notebook metadata and stored outputs must remain reproducible, source-timestamped,
and free of credentials or account details.

## Before Publishing

1. Import the notebook from
   [OilpriceAPI/kaggle-notebooks](https://github.com/OilpriceAPI/kaggle-notebooks).
2. Add `OILPRICEAPI_KEY` through Kaggle Secrets. Never paste a key into a cell,
   output, URL, commit, screenshot, issue, or notebook metadata.
3. Enable internet access for package installation and API requests.
4. Run every cell from a clean kernel.
5. Confirm the notebook reports commodity code, currency, unit, source
   timestamp, requested date range, and any data limitations.
6. Confirm missing secret, authentication, entitlement, rate-limit, timeout,
   empty response, and malformed response paths give a working next action.
7. Clear mutable outputs before committing the repository copy. Public Kaggle
   outputs must identify their execution time and must not be described as
   current after that run.
8. Run the repository validation commands before publishing:

   ```bash
   ./scripts/scan-secrets.sh
   python3 -m pytest -q
   ```

## Product Claims

Use the reviewed contract for offer, catalog, freshness, entitlement, and
data-rights facts:

- [Product facts](https://api.oilpriceapi.com/product-facts.json)
- [Documentation](https://docs.oilpriceapi.com)
- [Pricing and current access](https://www.oilpriceapi.com/pricing)
- [Data usage policy](https://www.oilpriceapi.com/legal/data-usage)

Latest available values include source timestamps. Refresh cadence varies by
source, market hours, dataset, and plan. Do not describe notebook values as a
live executable quote or imply guaranteed freshness.

## Publication Receipt

After a successful Kaggle run, record the public notebook URL, repository
commit, package version, execution timestamp, and validation result in the
release notes and the tracking issue. Do not record the secret, account email,
customer identifiers, request limits, or raw account responses.
