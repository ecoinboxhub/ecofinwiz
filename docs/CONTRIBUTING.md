# EcoFinwize — Contributing Guidelines

> **Companion to**: AGENTS.md (Engineering Constitution)
> **Purpose**: Coding standards, Git workflow, testing expectations, and review guidelines for all AI coding agents and human contributors.

---

## 1. Before You Code

Per AGENTS.md Section 19, before writing any code, explain:

1. **Why** this feature exists — which user problem it solves
2. **Which assistant** it strengthens — Kemi, Chidi, or both
3. **How** it aligns with the fellowship objectives (SDGs)
4. **How** it performs with poor connectivity (offline-first)
5. **How** it minimizes bandwidth (low-bandwidth engineering)
6. **How** it protects against AI hallucinations (RAG + guardrails)
7. **Why** it belongs in the MVP scope (passes the decision filter)

Only after answering these should implementation begin.

---

## 2. Coding Standards

### 2.1 General

- Write **modular code** — one file = one responsibility
- Use **dependency injection** for services
- Follow the **repository pattern** for data access
- Maintain **service layer separation** — business logic never in routers or UI
- Use **typed interfaces** — Python type hints, TypeScript types, Dart types
- Write **self-documenting code** — clear names, minimal comments

### 2.2 Python (Backend — FastAPI)

```python
# ✅ Good
class BudgetService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_budgets(self, user_id: UUID) -> list[Budget]:
        result = await self.db.execute(
            select(Budget).where(Budget.user_id == user_id)
        )
        return result.scalars().all()

# ❌ Bad — no type hints, no service layer
def get_budgets(user_id):
    return db.query(Budget).filter_by(user_id=user_id).all()
```

**Conventions:**
- Use `async def` for all route handlers and service methods
- Type hint all function parameters and return values
- Use Pydantic v2 models for request/response schemas
- Use SQLAlchemy 2.0 `select()` style (not legacy `Query` API)
- Error handling via `AppException` subclasses, not bare HTTPExceptions

### 2.3 TypeScript (Frontend — React)

```typescript
// ✅ Good
interface BudgetResponse {
  id: string;
  name: string;
  monthly_limit: number;
  spent: number;
  remaining: number;
}

// ❌ Bad — any types, no interface
const getBudgets = async (): Promise<any> => { ... }
```

**Conventions:**
- Use TypeScript strict mode
- Prefer interfaces over types for object shapes
- Use React Functional Components with hooks (no class components)
- Use `import.meta.env.VITE_*` for environment variables
- Format with Prettier (default config)

### 2.4 Dart (Mobile — Flutter)

```dart
// ✅ Good
class BudgetService {
  final ApiService _api;

  BudgetService(this._api);

  Future<List<Budget>> getBudgets() async {
    final response = await _api.get('/finance/budgets');
    return (response as List).map((j) => Budget.fromJson(j)).toList();
  }
}

// ❌ Bad — no type safety, logic in UI
```

**Conventions:**
- Use Provider for state management
- Prefer `final` over `var`
- Use named constructors for JSON deserialization
- Keep widgets stateless where possible
- Use `const` constructors for performance

---

## 3. Architecture Rules

### 3.1 Module Boundaries

```
┌─────────────────────────────────────────────┐
│              Router (endpoints)              │
│  → validates input                          │
│  → calls service                            │
│  → returns response                         │
├─────────────────────────────────────────────┤
│              Service (business logic)        │
│  → orchestrates operations                  │
│  → calls repository / external APIs         │
│  → raises AppException on errors            │
├─────────────────────────────────────────────┤
│              Repository / ORM (data access)  │
│  → SQLAlchemy queries                       │
│  → returns model instances                  │
└─────────────────────────────────────────────┘
```

### 3.2 Dependency Direction

```
Router → Service → Repository (DB)
                → External API Service
                
Service → Service (cross-module only via dependency injection)
Repository → Repository (never directly from router)
```

**Rules:**
- Routers never call repositories directly
- Services never import routers
- Cross-module calls go through service classes, not direct DB access
- External services (email, payment, SMS) are injected, never imported statically

---

## 4. Git Workflow

### 4.1 Branch Naming

```
feature/kemi-budget-conversation
fix/transaction-category-bug
docs/update-api-endpoints
chore/dependency-upgrade
```

### 4.2 Commit Messages

```
type(scope): short description

- Use imperative mood: "Add" not "Added"
- Max 50 chars for first line
- Max 72 chars for body

Examples:
feat(kemi): add budget coaching conversation flow
fix(finance): correct transaction date filtering
docs(api): update budget endpoint examples
chore(deps): upgrade fastapi to 0.115.0
```

### 4.3 Pull Request Checklist

Before submitting:
- [ ] Passes MVP Decision Filter (AGENTS.md §8)
- [ ] Strengthens Kemi or Chidi
- [ ] Includes tests (unit or smoke)
- [ ] Handles offline behavior gracefully
- [ ] Minimizes bandwidth/data usage
- [ ] Includes RAG/citations if financial advice
- [ ] Passes lint/type-check (ruff, tsc, dart analyze)
- [ ] Updates documentation if API changes
- [ ] No secrets or credentials in code

---

## 5. Testing Expectations

### 5.1 Backend Testing

| Test Type | Tool | Coverage Target | When |
|-----------|------|----------------|------|
| Smoke tests | pytest + httpx | All routes respond | Every PR |
| Unit tests | pytest + unittest.mock | Service layer logic | When adding new services |
| Integration | pytest + test containers | DB + external API | Before release |

**Running tests:**
```bash
# All smoke tests (mocked DB, no Docker needed)
pytest tests/test_local.py -v

# Health check
pytest tests/test_health.py -v

# Specific module
pytest tests/test_local.py -k "TestFinanceRoutes"
```

### 5.2 Frontend Testing

| Test Type | Tool | Coverage Target | When |
|-----------|------|----------------|------|
| Build check | tsc + vite | 0 errors | Every commit |
| Unit tests | vitest (future) | Critical components | TBD |

### 5.3 Mobile Testing

| Test Type | Tool | Coverage Target | When |
|-----------|------|----------------|------|
| Static analysis | dart analyze | 0 warnings | Every commit |
| Build check | flutter build apk | Compiles | Every PR |

---

## 6. Code Review Guidelines

### Review Against AGENTS Principles

| Principle | Review Question |
|-----------|----------------|
| Conversation First | Can this be done through Kemi or Chidi? |
| Voice First | Does this work with voice input/output? |
| Offline First | What happens without internet? |
| Africa First | Does this work on low-end devices? |
| Accessibility | Is the simplest path the default? |
| AI Safety | Does every financial claim have a source? |
| MVP Scope | Does this belong in the fellowship MVP? |

### Review Checklist

- [ ] Code follows module boundaries (router → service → repository)
- [ ] Type hints present on all functions
- [ ] No duplicate logic
- [ ] Error handling via AppException (not bare 500s)
- [ ] Async/await used correctly (no blocking calls)
- [ ] No hardcoded secrets, URLs, or API keys
- [ ] Offline behavior considered (graceful degradation)
- [ ] Bandwidth usage minimized (no unnecessary API calls)
- [ ] AI safety: RAG citations included where relevant
- [ ] Tests added or existing tests pass

---

## 7. Documentation Standards

### 7.1 What to Document

| Artifact | Location | Format |
|----------|----------|--------|
| API endpoints | FastAPI auto-docs | OpenAPI/Swagger |
| Module architecture | `docs/ARCHITECTURE.md` | Markdown |
| Product requirements | `docs/PRODUCT_PRD.md` | Markdown |
| AI safety rules | `docs/AI_GUARDRAILS.md` | Markdown |
| Engineering principles | `docs/AGENTS.md` | Markdown |
| Environment variables | `.env.example` | Key=value |
| Service contracts | In-code docstrings | Python docstrings |

### 7.2 Docstring Format

```python
async def create_budget(user_id: UUID, data: dict) -> Budget:
    """Create a new budget for a user.

    Args:
        user_id: The UUID of the user creating the budget.
        data: Budget creation payload (name, monthly_limit, category, etc.).

    Returns:
        The created Budget model instance.

    Raises:
        ConflictException: If a budget with the same name exists.
    """
```

---

## 8. Environment & Secrets

- All secrets go in `.env` — never in code
- `.env.example` documents every variable with a placeholder value
- Never commit `.env` to version control
- API keys use descriptive env var names (e.g., `OPENROUTER_API_KEY`)

---

## 9. External Service Integration Rules

Every external service integration must:

1. **Have an `is_configured` property** — check before calling
2. **Implement graceful degradation** — fallback chain if primary fails
3. **Log at the appropriate level** — `warning` for fallback, `error` for failure
4. **Use httpx async client** — never use synchronous requests
5. **Set timeouts** — no infinite waits
6. **Error boundaries** — never crash the app if external API is down

```python
@property
def is_configured(self) -> bool:
    return bool(self.api_key)

async def send(self, ...) -> Result:
    if not self.is_configured:
        return Result(success=False, error="Not configured")
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            ...
    except Exception as e:
        logger.error("Service error: %s", e)
        return Result(success=False, error=str(e))
```

---

## 10. Definition of Done

Per AGENTS.md Section 20, a feature is complete only when:

- [ ] Solves a real user problem
- [ ] Fits the MVP scope
- [ ] Supports conversational interaction (Kemi or Chidi)
- [ ] Is documented
- [ ] Includes tests where practical
- [ ] Handles errors gracefully
- [ ] Considers offline behavior
- [ ] Minimizes data usage
- [ ] Meets accessibility expectations
- [ ] Maintains AI safety requirements
- [ ] Advances measurable social impact

---

## 11. Communication

- **Design decisions** should reference AGENTS.md principles
- **Technical debates** resolved by the MVP Decision Filter (§8)
- **Scope creep** flagged and escalated; use AGENTS.md §7 (Scope Management)
- **All code is AI-assisted** — treat AI agents as contributors requiring review
