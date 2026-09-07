"""
Safety guardrails for AI conversations.

Includes PII filtering, harmful content detection, and financial advice
compliance checks. Input is sanitized before LLM, output is checked after.
"""

import re
from typing import Optional


PII_PATTERNS = {
    "email": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
    "phone": re.compile(r"\b(\+?\d{1,3}[-.\s]?)?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,4}\b"),
    "bv_nin": re.compile(r"\b(\d{11}|\d{10})\b"),
    "account_number": re.compile(r"\b\d{10}\b"),
    "credit_card": re.compile(r"\b(?:\d[ -]*?){13,19}\b"),
}

OUTPUT_PHONE_PATTERN = re.compile(
    r"(?:\+?\d{1,3}[-.\s]?)\(?\d{2,4}\)?[-.\s]?\d{3,4}[-.\s]?\d{3,4}"
    r"|(?:0[789]0|081|090|091)\d{8}"
    r"|(?:\+234|234)\d{10}",
)


FINANCIAL_RED_FLAGS = [
    r"\b(get rich|guaranteed|risk.?free|no risk|sure thing)\b",
    r"\b(illegal|scam|fraud|money.?laundering|tax.?evasion)\b",
    r"\b(invest all your money|sell everything|put your life savings)\b",
    r"\b(pump|dump|insider trading|pump and dump)\b",
    r"\b(loophole|hidden secret|insider secret)\b",
]


class GuardrailResult:
    def __init__(self, passed: bool, sanitized_text: Optional[str] = None, reason: Optional[str] = None):
        self.passed = passed
        self.sanitized_text = sanitized_text
        self.reason = reason


def sanitize_input(text: str) -> tuple[str, list[str]]:
    warnings = []
    for name, pattern in PII_PATTERNS.items():
        matches = pattern.findall(text)
        if matches:
            text = pattern.sub(f"[{name.upper()}_REDACTED]", text)
            warnings.append(f"{name} detected and redacted ({len(matches)} instance(s))")
    return text, warnings


def check_financial_red_flags(text: str) -> list[str]:
    flags = []
    for pattern in FINANCIAL_RED_FLAGS:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            flags.extend(matches)
    return flags


def check_output_safety(text: str) -> GuardrailResult:
    flags = check_financial_red_flags(text)
    if flags:
        return GuardrailResult(
            passed=False,
            sanitized_text=text,
            reason=f"Output contains flagged financial terms: {', '.join(set(flags))}. "
                   f"Response blocked by safety guardrails.",
        )

    pii_warnings = []
    for name, pattern in PII_PATTERNS.items():
        if name == "bv_nin" or name == "account_number":
            continue
        if name == "phone":
            if OUTPUT_PHONE_PATTERN.search(text):
                pii_warnings.append(name)
            continue
        if pattern.search(text):
            pii_warnings.append(name)

    if pii_warnings:
        return GuardrailResult(
            passed=False,
            sanitized_text=text,
            reason=f"Output may contain PII ({', '.join(pii_warnings)}). Response blocked.",
        )

    return GuardrailResult(passed=True, sanitized_text=text)


def check_input_safety(text: str) -> GuardrailResult:
    sanitized, warnings = sanitize_input(text)

    if warnings:
        return GuardrailResult(
            passed=True,
            sanitized_text=sanitized,
            reason=f"Sensitive data redacted: {'; '.join(warnings)}",
        )

    return GuardrailResult(passed=True, sanitized_text=sanitized)
