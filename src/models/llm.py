import os
import time

class LocalLLM:
    """Local Hugging Face causal-LM adapter; never makes a network request at runtime."""
    model_name = os.getenv("ORBITDESK_LLM_MODEL", "Qwen/Qwen2.5-3B-Instruct")
    revision = os.getenv("ORBITDESK_LLM_REVISION", "main")

    def __init__(self) -> None:
        self.pipeline = None; self.load_seconds = 0.0
        if os.getenv("ORBITDESK_TEMPLATE_MODE", "0") != "1":
            started = time.perf_counter()
            try:
                from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
                tokenizer = AutoTokenizer.from_pretrained(self.model_name, revision=self.revision, local_files_only=True)
                model = AutoModelForCausalLM.from_pretrained(
                    self.model_name,
                    revision=self.revision,
                    local_files_only=True,
                    device_map="auto",
                )
                self.pipeline = pipeline("text-generation", model=model, tokenizer=tokenizer)
            except Exception:
                self.pipeline = None
            self.load_seconds = time.perf_counter() - started

    def _prompt(self, query: str, evidence: list[dict], reason: str | None) -> str:
        snippets = "\n\n".join(f"[{item['source_id']}] {item['text']}" for item in evidence)
        return f"You are OrbitDesk Support. Answer ONLY with the evidence below. Do not invent steps, claim account access, request secrets, or perform actions. Cite every conclusion using [source_id]. If evidence is insufficient, say so.\nQuestion: {query}\nVerification feedback: {reason or 'none'}\nEvidence:\n{snippets}\nAnswer:"

    def generate(self, query: str, evidence: list[dict], revision_reason: str | None = None) -> str:
        if not evidence: return "I do not have enough OrbitDesk documentation to answer this safely."
        if self.pipeline is not None:
            result = self.pipeline(self._prompt(query, evidence, revision_reason), max_new_tokens=220, do_sample=False, return_full_text=False)
            return result[0]["generated_text"].strip()
        if os.getenv("ORBITDESK_TEMPLATE_MODE", "0") != "1":
            raise RuntimeError("Local generation model is unavailable. Download/cache the configured Hugging Face model, or enable ORBITDESK_TEMPLATE_MODE=1 for tests only.")
        # Explicit deterministic test fallback; it is never the normal runtime path.
        citations = " ".join(f"[{item['source_id']}]" for item in evidence)
        return "Based on the supplied OrbitDesk evidence: " + " ".join(item["text"] for item in evidence) + " " + citations
