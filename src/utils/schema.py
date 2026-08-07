import json
from pathlib import Path

def validate_output(payload: dict) -> list[str]:
    schema_path = Path(__file__).resolve().parents[2] / "data" / "output_schema.json"
    try:
        from jsonschema import Draft202012Validator
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        return [f"schema: {error.message}" for error in Draft202012Validator(schema).iter_errors(payload)]
    except ImportError:
        required = {"classification", "answer", "sources", "confidence", "requires_human", "reason"}
        return [f"schema missing: {key}" for key in sorted(required - payload.keys())]
