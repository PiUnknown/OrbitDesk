UNSAFE_TERMS = ("here is your password", "api key is", "oauth token", "session cookie", "payment-card", "i issued a refund", "i changed your", "i inspected your account")

def safety_violations(text: str) -> list[str]:
    lower = text.lower()
    return [f"unsafe content: {term}" for term in UNSAFE_TERMS if term in lower]

def request_is_out_of_scope(query: str) -> bool:
    lowered = query.lower()
    return any(term in lowered for term in ("refund", "cancel subscription", "legal advice", "medical advice", "financial advice"))
