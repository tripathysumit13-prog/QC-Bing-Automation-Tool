# Bing Ads QC Automation Agent

This repository provides a minimum viable product (MVP) implementation of an AI-assisted quality-check (QC) service for Microsoft Advertising (Bing Ads) accounts, along with the supporting product requirements.

## Getting Started

1. Create a virtual environment and install dependencies:

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -e .[dev]
   ```

2. Run the sample QC workflow against the included demo snapshot:

   ```bash
   python -m qc_tool data/sample_account.json rules/default_rules.yaml --output sample_report.json
   ```

   The command prints a human-readable report and writes structured results to `sample_report.json`.

3. Execute the automated tests:

   ```bash
   python -m pytest
   ```

## Product Requirements

The complete product requirements document (PRD) describing goals, rule catalog, architecture, APIs, rollout, and more remains available at [`docs/PRD.md`](docs/PRD.md).

## Extending the MVP

* Add or customize rules by editing the YAML files in [`rules/`](rules).
* Provide real account snapshots that follow the schema demonstrated in [`data/sample_account.json`](data/sample_account.json).
* Build integrations with the Microsoft Ads API to replace the static snapshot loader in `qc_tool/loader.py`.
