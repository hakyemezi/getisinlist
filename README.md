# Takasbank VB ISIN browser

A small Streamlit tool for reading Takasbank's **VB** ISIN list. The search filters **VIS futures contracts**; this is not a complete fund-to-ISIN mapping service.

## Run

Use Python 3.11 or newer:

```sh
python -m pip install -r requirements.txt
streamlit run getisinlist.py
```

The source is cached for one hour. **Refresh source** clears this cache. All discovered pages must load successfully; a missing table, schema change or failed request produces an error instead of silently returning a partial list. A single page without pagination is supported. Search treats punctuation literally.

The scraper depends on the provider's HTML. Test fixtures check parsing and failure handling; they do not prove that the live source is available.

## Tests

```sh
python -m pip install pytest
python -m pytest -q tests
```

A GitHub Actions example is provided at `docs/ci-tests.example.yml`. It is not active: enabling it requires copying it to `.github/workflows/tests.yml` with credentials that can manage workflows. Local tests use the commands above.
