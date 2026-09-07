# EcoFinwize — AI Guardrails & Safety

> **Companion to**: AGENTS.md (Engineering Constitution)
> **Purpose**: Detailed RAG policies, prompt engineering rules, hallucination prevention, citation requirements, and safety constraints for all AI-powered features.

---

## 1. Core Safety Principle

**Financial advice must never rely solely on LLM knowledge.** The LLM provides reasoning; the knowledge base provides facts. Every financial response must cite a verified source.

```
Required Pipeline:
  User Input → Guardrails → Embedding → Vector Search → Retrieved Context
  → Prompt Assembly → LLM → Output Guardrails → Cited Response → User
```

---

## 2. RAG Pipeline Requirements

### 2.1 Embedding

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| Model | OpenAI text-embedding-3-small | High quality, 384 dimensions, cost-effective |
| Fallback | Jina AI embeddings v2 | Open-source alternative |
| Last resort | sentence-transformers (local) | No API key required |
| Batch size | 20 texts per request | Balances throughput and latency |
| Chunk size | 512 tokens | Optimal for semantic search |

### 2.2 Vector Search

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| Vector store | Pinecone (serverless) | Scalable, managed |
| Index | finwize-knowledge | Single index for all knowledge |
| Metric | cosine | Best for semantic similarity |
| Top-k | 5 chunks | Sufficient context without noise |
| Similarity threshold | 0.75 | Below this = no relevant context found |
| Fallback threshold | 0.60 | Lower threshold when primary returns nothing |

### 2.3 Knowledge Base Contents

**Allowed sources:**
- Curated financial education content
- Local tax laws and regulations (verified)
- Government financial literacy resources
- SME documentation and templates
- Business compliance documents
- Approved third-party educational content

**Prohibited sources:**
- Unverified web scrapes
- Social media content
- User-uploaded documents (must pass moderation first)
- LLM-generated "knowledge" without source verification

---

## 3. Prompt Engineering Rules

### 3.1 System Prompt Structure

Every conversation prompt must contain:

```
1. Persona definition (Kemi or Chidi personality)
2. Safety instructions (mandatory)
3. Citation requirements
4. Uncertainty handling
5. Context injection (user data)
6. Response format
```

### 3.2 Mandatory Safety Instructions

The following instructions must appear in every system prompt:

```
You are a financial assistant. You MUST follow these rules:

1. NEVER give financial advice without citing a source from the provided context.
2. If you don't know the answer, say "I don't have verified information about that."
3. NEVER invent tax rates, regulations, or legal requirements.
4. NEVER recommend specific stocks, crypto, or investment products.
5. ALWAYS include disclaimers when discussing financial risks.
6. If context is insufficient, ask clarifying questions before answering.
7. NEVER share personal user data between conversations.
8. If a user asks about self-harm or financial distress, provide supportive resources.
```

### 3.3 Response Format Rules

```
1. Begin with a direct answer to the user's question.
2. Follow with relevant context or explanation.
3. Cite sources using inline markers: [1], [2], etc.
4. List sources at the end of the response.
5. If uncertain, state: "I'm not entirely sure about this."
6. If no context found: "I don't have information about that in my knowledge base."
```

---

## 4. Hallucination Prevention

### 4.1 Pre-Generation Checks

| Check | Implementation | Action |
|-------|---------------|--------|
| PII redaction | Regex: email, phone, SSN, bank details before LLM call | Mask with [REDACTED] |
| Harmful intent detection | Keyword + pattern matching on input | Block and log |
| Context relevance | Check if retrieved chunks exist before prompting | If empty → inform user |
| Topic boundary check | Verify input is finance/business related | If out-of-scope → redirect |

### 4.2 Post-Generation Checks

| Check | Implementation | Action |
|-------|---------------|--------|
| Hallucination detection | Regex for fabricated stats, percentages, dates | Flag for review |
| Citation verification | Ensure every [N] marker has a corresponding source | Strip uncited claims |
| Output sanitization | Remove any PII that leaked through | Mask and log |
| Safety scan | Check for harmful, discriminatory, or offensive content | Block and log |
| Rate check | Verify numbers (percentages, amounts) match context | Flag discrepancies |

### 4.3 Handling Uncertainty

When the RAG pipeline returns no relevant context (similarity < 0.75):

```
Assistant: "I don't have verified information about that specific question.
Here's what I can tell you based on general knowledge: [general info with disclaimer].
Would you like me to find someone who can help, or would you like to ask about
something else I have information on?"
```

When context is partial:

```
Assistant: "Based on the information I have, [answer with sources].
However, I recommend consulting with a qualified financial advisor for
personalized advice on this matter."
```

---

## 5. Citation Requirements

### 5.1 Citation Format

Every financial response must include inline citations:

```
Based on the Central Bank of Nigeria guidelines [1], the current
monetary policy rate is 27.50%. This affects savings account
interest rates at commercial banks [2].

Sources:
[1] CBN Monetary Policy Committee Communiqué, March 2026
[2] Financial Literacy Guide for Nigerian Youth, Section 4.2
```

### 5.2 Citation Rules

- Every factual claim must have at least one source
- Sources must be listed at the end of the response
- Multiple claims from same source: reuse the same [N] marker
- If a source is generated or speculative, it must be labeled as such
- Personal user data (budget amounts, transaction history) is exempt from citation

### 5.3 Context Assembly for Citations

The context block injected into the LLM prompt must include:

```
=== RETRIEVED KNOWLEDGE ===
[1] Source: CBN MPC Communiqué, March 2026
Content: The MPC voted to hold MPR at 27.50%...

[2] Source: Financial Literacy Guide, Section 4.2
Content: Savings accounts in Nigeria typically earn 1-4% interest...
=== END RETRIEVED KNOWLEDGE ===
```

---

## 6. Safety Constraints

### 6.1 Absolute Prohibitions

The AI must **never**:

- Give specific stock/crypto buy/sell recommendations
- Quote tax rates or regulations without citing the exact source document
- Claim to be a licensed financial advisor
- Store or repeat personal financial information across user sessions
- Generate disclaimers that imply medical or legal advice
- Use fear-based language to pressure financial decisions
- Reference specific unverified investment opportunities

### 6.2 Required Disclaimers

**Financial advice response:**
> "This information is for educational purposes. Please consult a licensed financial advisor for personalized advice."

**Tax/regulatory response:**
> "Tax laws may change. Please verify with a tax professional or the relevant government authority."

**Investment discussion:**
> "All investments carry risk. Past performance does not guarantee future results."

### 6.3 Sensitive Topic Handling

| Topic | Behavior |
|-------|----------|
| Debt/loss/depression | Provide supportive resources, avoid judgment |
| Bankruptcy | General information only, recommend professional help |
| Loans/debt | Explain terms, warn about predatory lending |
| Cryptocurrency | General education only, no trading advice |
| Gambling | Block and flag, redirect to financial literacy |

---

## 7. Guardrails Architecture

```
                    ┌─────────────────────────┐
                    │    User Input            │
                    │    (text/voice)          │
                    └────────────┬────────────┘
                                 ▼
                    ┌─────────────────────────┐
                    │  Input Guardrails         │
                    │  ─────────────────────── │
                    │  • PII Redaction         │
                    │  • Harmful Intent Check  │
                    │  • Topic Boundary Check  │
                    │  • Rate Limit Check      │
                    └────────────┬────────────┘
                         PASS   │   BLOCK
                    ┌───────────▼───────────┐
                    │  RAG Pipeline          │
                    │  ──────────────────    │
                    │  • Embed Query         │
                    │  • Search Pinecone      │
                    │  • Retrieve Context     │
                    │  • Relevance Check      │
                    └───────────┬────────────┘
                                 ▼
                    ┌─────────────────────────┐
                    │  Prompt Assembly         │
                    │  ─────────────────────── │
                    │  • System Prompt         │
                    │  • Safety Instructions   │
                    │  • Retrieved Context     │
                    │  • User Data Context     │
                    │  • Conversation History  │
                    └────────────┬────────────┘
                                 ▼
                    ┌─────────────────────────┐
                    │  LLM (OpenRouter/Groq)   │
                    │  → Streaming Response    │
                    └────────────┬────────────┘
                                 ▼
                    ┌─────────────────────────┐
                    │  Output Guardrails       │
                    │  ─────────────────────── │
                    │  • Hallucination Check   │
                    │  • Citation Verification │
                    │  • Output Sanitization   │
                    │  • Safety Scan          │
                    └────────────┬────────────┘
                         PASS   │   BLOCK
                    ┌───────────▼───────────┐
                    │  User Response         │
                    │  (SSE streaming)       │
                    └───────────────────────┘
```

---

## 8. Monitoring & Feedback

| Mechanism | Purpose | Frequency |
|-----------|---------|-----------|
| User ratings (1-5 stars) | Direct quality feedback | Per response |
| Report inappropriate | Flag harmful/incorrect responses | Per response |
| Automated safety logs | All guardrail violations logged | Real-time |
| Human review queue | Responses rated < 3 stars or flagged | Daily |
| Hallucination audits | Random sample of 100 conversations/month | Monthly |
| RAG relevance tracking | % of queries with successful retrievals | Real-time |

---

## 9. Incident Response

| Severity | Definition | Response Time | Action |
|----------|-----------|---------------|--------|
| Critical | AI gives harmful financial advice | < 1 hour | Block model, rollback prompt, notify team |
| High | AI fabricates regulations/tax rates | < 4 hours | Add to prohibited patterns, audit affected users |
| Medium | AI cites incorrect sources | < 24 hours | Fix RAG pipeline, re-index affected documents |
| Low | AI gives unclear or unhelpful response | < 72 hours | Review and improve prompt |

---

## 10. Compliance & Ethics

| Standard | Requirement | Status |
|----------|-------------|--------|
| Nigeria Data Protection Act (2023) | User data consent, right to deletion | Implemented |
| GDPR (if EU users) | Data portability, breach notification | Partial |
| AI ethics | Transparency, fairness, accountability | Built into guardrails |
| Financial advisory regulation | Clear disclaimers, no unlicensed advice | In prompts |
| Content moderation | No hate speech, discrimination, or harmful content | Implemented |
