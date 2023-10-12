"""Find cross-split duplicates, shared groups, and token-overlap candidates."""
import argparse
import hashlib
import json
from pathlib import Path
import math
import re
import sys
import unicodedata


def normalize(text):
    return " ".join(unicodedata.normalize("NFKC", text).casefold().split())


def audit(records, near_threshold=0.8, minimum_tokens=3):
    if not isinstance(records, list) or len(records) > 1000:
        raise ValueError("records must be a list with at most 1000 rows")
    if type(near_threshold) not in (int, float) or not math.isfinite(near_threshold) or not 0 <= near_threshold <= 1:
        raise ValueError("near_threshold must be finite and in [0,1]")
    if type(minimum_tokens) is not int or minimum_tokens < 1:
        raise ValueError("minimum_tokens must be a positive integer")
    ids, exact, groups, normalized, tokens = {}, {}, {}, [], []
    for index, row in enumerate(records):
        if any(not isinstance(row.get(key), str) or not row[key].strip() for key in ("id", "text", "split")):
            raise ValueError("id, text, and split must be nonempty strings")
        if row["split"] not in ("train", "validation", "test"):
            raise ValueError("split must be train, validation, or test")
        if "group" in row and (not isinstance(row["group"], str) or not row["group"].strip()):
            raise ValueError("group must be a nonempty string when supplied")
        value = normalize(row["text"])
        normalized.append(value)
        tokens.append(set(re.findall(r"\w+", value)))
        ids.setdefault(row["id"], []).append(index)
        exact.setdefault(hashlib.sha256(value.encode("utf-8")).hexdigest(), []).append(index)
        if "group" in row:
            groups.setdefault(row["group"], []).append(index)

    def references(indices):
        return [{"row": index, "id": records[index]["id"], "split": records[index]["split"]} for index in indices]

    def cross_split(indices):
        return len({records[index]["split"] for index in indices}) > 1

    duplicates = [{"id": key, "records": references(value)} for key, value in ids.items() if len(value) > 1]
    exact_leaks = [{"normalized_sha256": key, "records": references(value)} for key, value in exact.items() if cross_split(value)]
    group_leaks = [{"group": key, "records": references(value)} for key, value in groups.items() if cross_split(value)]
    near = []
    for first, row in enumerate(records):
        for second in range(first + 1, len(records)):
            if row["split"] == records[second]["split"] or normalized[first] == normalized[second]:
                continue
            left, right = tokens[first], tokens[second]
            if min(len(left), len(right)) < minimum_tokens:
                continue
            similarity = len(left & right) / len(left | right)
            if similarity >= near_threshold:
                near.append({"records": references([first, second]), "token_jaccard": similarity})
    findings = {"duplicate_ids": duplicates, "exact_cross_split": exact_leaks,
                "shared_groups": group_leaks, "near_duplicate_candidates": near}
    return {"passed": not any(findings.values()), "records": len(records), "findings": findings}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True)
    args = parser.parse_args()
    try:
        input_path = Path(args.input)
        if not input_path.is_absolute():
            input_path = Path(__file__).resolve().parent / input_path
        with input_path.open(encoding="utf-8") as handle:
            data = json.load(handle)
        result = audit(data["records"], data.get("near_threshold", 0.8), data.get("minimum_tokens", 3))
        print(json.dumps(result, indent=2, allow_nan=False))
        return 0 if result["passed"] else 1
    except (ValueError, KeyError, TypeError, OSError) as error:
        print(f"Invalid split audit: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
