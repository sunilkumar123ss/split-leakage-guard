# Dataset split leakage guard

Audit small text datasets for duplicate record IDs, normalized text shared across splits, shared speaker/customer/document groups, and token-Jaccard near-duplicate candidates. Fixture utterances and group IDs are synthetic.

~~~sh
python3 main.py --input example.json
python3 -m unittest -v
~~~

The supplied fixture intentionally contains leakage and exits 1. Exit 0 means no findings; exit 2 means invalid input. Text normalization uses Unicode NFKC, case folding, and collapsed whitespace. Near-duplicate candidates require a configurable minimum unique-token count and threshold. Exact duplicates within one split are not flagged unless IDs repeat.

Output references row IDs and hashes rather than reproducing text. Group identifiers still appear in output. Pairwise comparison is limited to 1000 records and is quadratic. Token overlap is a heuristic, not semantic similarity; findings require review and a clean report does not prove evaluation independence.

## Scope

This is an educational implementation with synthetic fixtures. Run the tests and inspect the documented limits before adapting it.

## Repository checks

```sh
python3 verify.py
```

This runs the isolated test suite, synthetic example, and CLI help. The included GitHub Actions workflow repeats these checks when the repository is published. No hosted CI result is claimed by the local verification report.
