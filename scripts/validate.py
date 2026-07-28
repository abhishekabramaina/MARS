#!/usr/bin/env python3
"""
MARS Pydantic Validation CLI Tool
Validates JSON data files against Pydantic models / JSON schemas.
Designed for Coordinator validation-retry loops.
"""

import sys
import json
import os
from pathlib import Path
from typing import Any, Dict

from pydantic import ValidationError
from models import MODEL_MAP


def format_pydantic_errors(error: ValidationError) -> list[str]:
    """Formats Pydantic ValidationError into clear field-path error lines."""
    formatted_errors = []
    for err in error.errors():
        loc_str = "$." + ".".join([str(p) for p in err["loc"]])
        msg = err["msg"]
        err_type = err["type"]
        formatted_errors.append(f"[{loc_str}] {msg} (error_type={err_type})")
    return formatted_errors


def main():
    if len(sys.argv) < 3:
        print("Usage: python scripts/validate.py <data_file.json> <schema_file_or_model_name>")
        print("Supported model names: search, analysis, report")
        sys.exit(1)

    data_path = sys.argv[1]
    schema_arg = sys.argv[2]

    # Resolve schema/model key
    schema_filename = Path(schema_arg).name.lower()
    adapter = MODEL_MAP.get(schema_filename) or MODEL_MAP.get(schema_arg.lower())

    # Read target JSON data file
    if not os.path.exists(data_path):
        print(f"Error: Data file not found: {data_path}")
        sys.exit(1)

    try:
        with open(data_path, "r", encoding="utf-8") as f:
            raw_data = f.read()
            data = json.loads(raw_data)
    except json.JSONDecodeError as e:
        print(f"JSON Parsing Error in {data_path}: {e}")
        sys.exit(1)

    if adapter:
        try:
            adapter.validate_python(data)
            print("SUCCESS: JSON is valid against schema.")
            sys.exit(0)
        except ValidationError as e:
            errors = format_pydantic_errors(e)
            print(f"VALIDATION FAILED ({len(errors)} error(s) found):")
            for err in errors:
                print(f"  - {err}")
            sys.exit(1)
    else:
        print(f"Error: Unknown schema target '{schema_arg}'. Supported targets: {list(MODEL_MAP.keys())}")
        sys.exit(1)


if __name__ == "__main__":
    main()
