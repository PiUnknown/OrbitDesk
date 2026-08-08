import os
import time

class LocalLLM:
    """Local Hugging Face causal-LM adapter; never makes a network request at runtime."""
    # The 0.5B instruct model is practical on CPU-only laptops; override this env var for 3B/GPU runs.
    model_name = os.getenv("ORBITDESK_LLM_MODEL", "Qwen/Qwen2.5-0.5B-Instruct")
    revision = os.getenv("ORBITDESK_LLM_REVISION", "main")

    def __init__(self) -> None:
        self.pipeline = None; self.load_seconds = 0.0; self.load_error: str | None = None
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
                # device=None is essential for models dispatched by Accelerate across CPU/disk.
                self.pipeline = pipeline("text-generation", model=model, tokenizer=tokenizer, device=None)
            except Exception as exc:
                self.pipeline = None
                self.load_error = f"{type(exc).__name__}: {exc}"
            self.load_seconds = time.perf_counter() - started

    def _prompt(self, query: str, evidence: list[dict], reason: str | None) -> str:
        snippets = "\n".join(f"[{item['source_id']}] {item['text'][:320]}" for item in evidence[:2])
        return f"OrbitDesk support. Use only evidence. Give a concise answer in two sentences. Cite [source_id]. No account actions or secrets.\nQuestion: {query}\nEvidence:\n{snippets}\nAnswer:"

    def generate(self, query: str, evidence: list[dict], revision_reason: str | None = None) -> str:
        if not evidence: return "I do not have enough OrbitDesk documentation to answer this safely."
        if self.pipeline is not None:
            result = self.pipeline(self._prompt(query, evidence, revision_reason), max_new_tokens=32, do_sample=False, return_full_text=False)
            return result[0]["generated_text"].strip()
        if os.getenv("ORBITDESK_TEMPLATE_MODE", "0") != "1":
            raise RuntimeError("Local generation model could not initialize: " + (self.load_error or "model cache unavailable") + ". Download/cache the configured model, or enable ORBITDESK_TEMPLATE_MODE=1 for tests only.")
        # Explicit deterministic test fallback; it is never the normal runtime path.
        citations = " ".join(f"[{item['source_id']}]" for item in evidence)
        return "Based on the supplied OrbitDesk evidence: " + " ".join(item["text"] for item in evidence) + " " + citations
