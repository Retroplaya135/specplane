# Contributing

Changes should concern schemas, contract templates, validators, traceability, or generators. Add a focused test for changes to validation or generated output.

After installing the dependencies described in the README, run:

```bash
python -m unittest discover -s tests -v
python scripts/validate_contracts.py
```

Declare scaffold paths in the file manifest and include traceability markers. Preserve the scaffold generator's write-once behavior. Use synthetic requirements in tests, and keep application business logic out of generated placeholders.
