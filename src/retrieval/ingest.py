import json
import re
from pathlib import Path

def _frontmatter(text: str) -> dict:
    match = re.match(r"^---\s*(.*?)\s*---", text, re.S)
    return {key.strip(): value.strip() for key, value in re.findall(r"^([\w_]+):\s*(.+)$", match.group(1), re.M)} if match else {}

def _chunks(text: str, size: int = 350) -> list[str]:
    words = text.split()
    return [" ".join(words[start:start + size]) for start in range(0, len(words), size)] or [text]

def load_documents(data_dir: Path) -> list[dict]:
    """Load current KB documents first and non-superseded historical cases second."""
    docs: list[dict] = []
    for path in sorted((data_dir / "knowledge_base").glob("*.md")):
        raw = path.read_text(encoding="utf-8"); metadata = _frontmatter(raw)
        for index, chunk in enumerate(_chunks(raw)):
            docs.append({"source_id": metadata.get("document_id", path.stem), "title": metadata.get("title", path.stem), "text": chunk, "document_type": "kb", "status": metadata.get("status", "current"), "chunk_id": f"{path.stem}:{index}"})
    payload = json.loads((data_dir / "resolved_cases.json").read_text(encoding="utf-8") or "{}")
    cases = payload.get("cases", payload if isinstance(payload, list) else [])
    for case in cases:
        if case.get("status") == "superseded":
            continue
        text = " ".join([case.get("title", ""), *case.get("symptoms", []), *case.get("resolution", []), case.get("important_limit", "")])
        for index, chunk in enumerate(_chunks(text)):
            docs.append({"source_id": case["case_id"], "title": case["title"], "text": chunk, "document_type": "case", "status": case.get("status", "resolved"), "chunk_id": f"{case['case_id']}:{index}", "source_documents": case.get("source_documents", [])})
    return docs
