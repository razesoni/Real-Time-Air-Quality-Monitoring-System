# Air Quality Ingestion Prototype

A Python prototype that polls OpenAQ measurements and adapts them to a Pathway stream schema.

**Implemented:** OpenAQ client and ingestion pipeline. AQI calculation, retrieval-augmented Q&A, trend analysis and spike detection are not yet implemented.

## Run locally

From the repository root in a separate Python environment:

```bash
python -m pip install -r requirements.txt
python -m ingestion.pathway_pipeline
```

Before running, copy `.env.example` to `.env` and supply your own OpenAQ key. Inspect the configured location IDs in the pipeline.

## Runtime modes

Install Pathway separately in a supported environment to use its streaming engine. When the engine cannot be imported, the current compatibility fallback performs one poll and prints records. This fallback is not a real-time stream processor.

## Credential maintenance

A credential file was previously tracked. It has been removed from the current branch, but historical commits may still contain it. The owner must revoke/rotate the old key with OpenAQ. Do not reuse it. History cleanup is a separate coordinated operation.

## Next steps

Test ingestion against controlled fixtures, define pollutant units and AQI methodology, then implement and evaluate downstream features. No production deployment is claimed.
