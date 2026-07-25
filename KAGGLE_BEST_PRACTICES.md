# Kaggle Notebook Release Practices

Use this checklist for every OilPriceAPI notebook. The repository copy is the
reviewed source; Kaggle is a deployment target, not the place to edit the
notebook.

## 1. Generate deterministic notebooks

Author reviewed cells in `scripts/generate_notebooks.py` and shared validation
logic in `scripts/notebook_support.py`. Then regenerate:

```bash
python3 scripts/generate_notebooks.py
```

Notebook `source` arrays must preserve line breaks on every line except the
last. Do not hand-edit notebook JSON. The generator keeps cell IDs stable,
clears execution counts and outputs, and embeds the exact reviewed support
module.

## 2. Keep credentials out of content

- Attach `OILPRICEAPI_KEY` through **Kaggle > Add-ons > Secrets**.
- Use a dedicated non-customer test key for release verification.
- Never paste a key into a notebook, output cell, metadata file, URL, log, or
  screenshot.
- Do not add a fallback credential. A missing secret must fail with the
  documented `MISSING_SECRET` recovery action.
- Run the tracked-content secret scan before every upload.

Repository notebooks deliberately contain no stored output. A public Kaggle
execution may display API values only when it also displays the notebook
execution time and the API timestamp/source context.

## 3. Validate before upload

From a clean checkout with the pinned notebook dependencies installed:

```bash
python3 -m pip install "oilpriceapi[pandas]==1.11.0" matplotlib seaborn
./scripts/validate_before_upload.sh
```

The command:

1. regenerates both notebooks and rejects source drift;
2. validates notebook JSON and Python syntax;
3. scans tracked content for credential patterns;
4. executes the exact committed cells against deterministic,
   production-shaped fixtures;
5. verifies missing/invalid key, locked dataset, 429, timeout, empty response,
   malformed response, timestamp, unit, and freshness behavior; and
6. builds isolated Kaggle CLI upload directories under `dist/kaggle`.

Do not upload if the command changes a tracked notebook or any check fails.
The fixture run does not replace the final Kaggle execution with an attached
non-customer secret.

## 4. Package and publish

`scripts/package_kaggle.py` creates one upload directory per public kernel with
the reviewed notebook and `kernel-metadata.json`.

```bash
./scripts/validate_before_upload.sh
kaggle kernels push -p dist/kaggle/oilpriceapi-wti-vs-brent
kaggle kernels push -p dist/kaggle/oil-price-technical-analysis
```

Monitor each kernel until it reaches a terminal state:

```bash
kaggle kernels status kwaldman/oilpriceapi-wti-vs-brent
kaggle kernels status kwaldman/oil-price-technical-analysis
```

If a run fails, download the output/logs, fix the reviewed source, regenerate,
and repeat the full validation. Do not patch only the Kaggle copy.

## 5. Review the public result

Before recording a release receipt, confirm:

- the attached secret is enabled and no secret value is visible;
- the first latest-price and history requests succeed;
- every analytical output names the symbol, currency, unit, source, API
  timestamp, requested range, and method;
- missing/invalid credentials and quota/access failures give a working next
  action;
- the output is described as the result of that dated execution, not a
  permanently current price;
- runtime stays within the Kaggle limit and requests remain bounded; and
- notebook metadata, title, links, and package version match the reviewed
  repository revision.

Save the Kaggle version URL, terminal status, execution timestamp, and source
commit in the release issue. Public republishing is a deployment and requires
the deployment authorization applicable to that session.

## 6. Distribution and SEO

Write for the developer question the notebook actually answers. Use precise
titles and an educational introduction, link to the current API reference and
product-facts contract, and make the notebook independently useful. Do not
manufacture backlinks, promise trading outcomes, repeat mutable plan/catalog
counts, or describe every source as real-time.
