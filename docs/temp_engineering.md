# Engineering Standards Master Document

**Maintained by:** Mike Muryn
**Revision:** 3.5
**Last Updated:** November 27, 2025

---

> **Status in this repo:** Archived upstream “master” standards reference.
>
> For this codebase, the canonical, shortened standards are:
> - `docs/engineering.md` (core rules)
> - `docs/engineering-playbook.md` (examples/how-to)
> - `docs/code-review-checklist.md`
> - `docs/naming-conventions.md`
>
> Keep this file as a reference; prefer updating the canonical docs above.

## 📘 Table of Contents
- [Purpose & Scope](#purpose--scope)
- [Usage Across Repositories](#usage-across-repositories)
- [General Standards](#general-standards)
- [Naming & Style Rules](#naming--style-rules)
- [Documentation Standards](#documentation-standards)
- [Testing & CI/CD](#testing--cicd)
- [Security, Secrets & Dependency Hygiene](#security-secrets--dependency-hygiene)
- [Logging & Error Handling](#logging--error-handling)
- [Runtime Operations & Observability](#runtime-operations--observability)
- [Performance & Complexity](#performance--complexity)
- [Version Control & Code Review](#version-control--code-review)
- [Knowledge Transfer & Hand-off](#knowledge-transfer--hand-off)
- [Operational Enforcement Tools](#operational-enforcement-tools)
- [Appendix A – Software Craftsmanship Principles](#appendix-a--software-craftsmanship-principles)
- [Appendix B – Enforcement Checklist](#appendix-b--enforcement-checklist)

---

## ⚙️ General Standards
<details><summary>Expand</summary>

- Use a professional CI/CD structure with linting, typing, and tests.  
- Apply **semantic versioning** and **Conventional Commits** (`feat:`, `fix:`, `test:` etc.).  
- Organize all code under `/src` and mirror tests under `/tests`.  
- Use **Conda** for environment management (pip only if conda-forge unavailable).  
- Never hard-code credentials; use `.env` or secure OS keyrings.  
- Profile key paths using `cProfile` or `line_profiler`.  
- Functions should generally be **under 30 lines**.  
- Maintain cyclomatic complexity ≤ 10 (flag > 15 for review).  
- Detect headless or non-interactive environments across **GUIs, CLIs, cron jobs, notebooks, and services**, and provide safe fallbacks (log instead of failing).  
- All alerting or outbound systems (email, SMS, Slack) must implement a common `AlertSender` interface returning a structured `DeliveryResult` and logging all outcomes.  
- Fixing a bug requires changes to the underlying codebase – never comment out tests or functionality as a "fix."  

</details>

---

## ✏️ Naming & Style Rules
<details><summary>Expand</summary>

### Python Code Standards
- Follow **PEP 8**, enforced via `black`, `flake8`, and `mypy`.  
- All public functions include **type hints** (`mypy --strict`).  
- Boolean names should read like questions (`is_valid`, `should_alert`, `has_timeout`).  
- Prefer **descriptive** names over abbreviations (`current_price`, not `cp`).  

---

### Python Naming Conventions (PEP 8)

**Modules:** Short all-lowercase; underscores if needed for readability  
Example: `data_processor.py`

**Packages:** Short all-lowercase; avoid underscores  
Example: `analytics`

**Classes:** CapWords (CamelCase)  
Example: `DataProcessor`, `UserAccount`

**Functions & Methods:** snake_case  
Example: `calculate_sum()`, `load_user_data()`

**Variables:** snake_case  
Example: `total_count`, `user_id`

**Constants:** UPPERCASE_WITH_UNDERSCORES  
Example: `MAX_RETRIES`, `DEFAULT_TIMEOUT`

**Logger Names:** Module-qualified  
```python
logger = logging.getLogger(__name__)
```

---

### Non-Python File Naming Conventions

#### 📋 Documentation Files — SCREAMING_CASE
**Root-level documentation must be uppercase for visibility:**
```
README.md              ✅ Required
CHANGELOG.md           ✅ Required
CONTRIBUTING.md        ✅ Required
LICENSE                ✅ Required (no extension)
CODE_OF_CONDUCT.md     ✅ Optional
AUTHORS.md             ✅ Optional
SECURITY.md            ✅ Optional
ENGINEERING_STANDARDS_MASTER.md ✅ Project-specific
```

**Subdirectory documentation should be lowercase with hyphens:**
```
docs/
├── architecture.md
├── api-reference.md
├── deployment-guide.md
└── user-manual.md
```

#### ⚙️ Configuration Files — lowercase
```
.env                   ✅ Environment variables
.env.example           ✅ Template for .env
config.yaml            ✅ Application config
settings.yaml          ✅ User settings
pyproject.toml         ✅ Python project config
.gitignore             ✅ Git ignore rules
.gitattributes         ✅ Git attributes
.pre-commit-config.yaml ✅ Pre-commit hooks
.flake8                ✅ Flake8 configuration
.pylintrc              ✅ Pylint configuration
docker-compose.yml     ✅ Docker Compose
.dockerignore          ✅ Docker ignore rules
```

**Exceptions — Capitalized by convention:**
```
Dockerfile             ✅ Standard Docker convention
Dockerfile.dev         ✅ Environment-specific
Dockerfile.prod        ✅ Environment-specific
```

#### 🛠️ Build & Task Files — Capitalized (by convention)
```
Makefile               ✅ GNU Make standard
Jenkinsfile            ✅ Jenkins standard
Procfile               ✅ Heroku/process manager standard
```

**Modern alternatives use lowercase:**
```
justfile               ✅ just command runner
```

#### 📜 Shell Scripts — lowercase with hyphens
```bash
scripts/
├── setup.sh           ✅ Single word
├── deploy.sh          ✅ Single word
├── run-tests.sh       ✅ Multi-word: kebab-case
├── build-docker.sh    ✅ Multi-word: kebab-case
├── seed-database.sh   ✅ Multi-word: kebab-case
└── generate-docs.sh   ✅ Multi-word: kebab-case
```

**Avoid:**
```
❌ Setup.sh            (Don't capitalize)
❌ DEPLOY.sh           (Don't use all caps)
❌ run_tests.sh        (Don't use underscores)
```

#### 🏗️ Infrastructure as Code — lowercase
```
# Terraform
main.tf
variables.tf
outputs.tf
terraform.tfvars

# Kubernetes
deployment.yaml
service.yaml
ingress.yaml
configmap.yaml

# CloudFormation
stack.yaml
template.json

# Ansible
playbook.yml
inventory.ini
```

#### 📊 Data Files — lowercase with hyphens
```
data/
├── sample-data.csv
├── config.json
├── schema.sql
├── seed-data.yaml
└── test-fixtures.json
```

#### 🎯 CI/CD Workflows — lowercase with hyphens
```
.github/
└── workflows/
    ├── ci.yml
    ├── deploy-prod.yml
    ├── security-scan.yml
    └── dependency-update.yml

.gitlab-ci.yml
.travis.yml
```

---

### Naming Convention Rationale

**UPPERCASE documentation:** Historical Unix convention for high visibility in repo root; matches GitHub/GitLab expectations for special files.

**lowercase configs:** Tool expectations—most systems explicitly look for lowercase config files (`.gitignore`, `docker-compose.yml`).

**Hyphens in scripts:** Improved readability in shell context; standard practice in modern tooling (npm scripts, GitHub Actions).

**Consistency over perfection:** When ecosystem conventions exist (e.g., `Makefile`, `Dockerfile`), follow them even if they break general rules.

---

### Quick Reference Table

| File Type | Convention | Example |
|-----------|-----------|---------|
| Root docs | UPPERCASE.md | `README.md` |
| Subdirectory docs | lowercase-with-hyphens.md | `api-guide.md` |
| Configs | lowercase | `.env`, `config.yaml` |
| Docker | Capitalized | `Dockerfile` |
| Build tools | Capitalized | `Makefile` |
| Scripts | lowercase-with-hyphens.sh | `deploy.sh` |
| IaC | lowercase | `main.tf` |
| Data | lowercase-with-hyphens | `test-data.csv` |

---

### Additional Guidance
- Avoid confusing one-letter names (`l`, `O`, `I`).
- Multi-word non-Python files: prefer hyphens over underscores (`api-docs.md` not `api_docs.md`).
- Consistency within the project outweighs strict perfection.
- When in doubt, check similar files in major OSS projects (Django, FastAPI, Kubernetes).

---

### Data Operations Terminology

**Consistent terminology for data operations:**

- **`fetch`** – Get data from external APIs or remote sources
  - Example: `fetch_historical_data()`, `fetch_price_data()`
  - Use in: Method names, log messages when calling APIs
  - Context: "Fetching data from Schwab API"

- **`pull`** – Get data from local storage (database, cache, file system)
  - Example: `get_bars()` returns data from storage, log "Pulled 13 bars from storage"
  - Use in: Log messages, docstrings when retrieving from local storage
  - Context: "Pulled 13 bars for SPY from storage"

- **`store`** / **`save`** – Persist data to local storage
  - Example: `store_bars()`, `save_config()`
  - Use in: Method names for persistence operations
  - Context: "Stored 13 bars in cache"

- **`get`** – Generic retrieval (can be from storage or computed)
  - Example: `get_bars()`, `get_account()`
  - Use in: Method names when source is ambiguous or method handles both cases
  - Context: "Get bars from storage or compute if missing"

- **`update`** / **`sync`** – Refresh data by fetching missing pieces
  - Example: `update_incremental()`, `sync_data()`
  - Use in: Method names for incremental updates
  - Context: "Update cached data with missing ranges"

**Rationale:**
- "Fetch" clearly indicates external API calls (network I/O, rate limits, authentication)
- "Pull" clearly indicates local storage access (fast, no network, may be cached)
- This distinction helps with debugging, performance analysis, and understanding data flow
- Consistent terminology improves code readability and maintainability

**Examples:**
```python
# ✅ Good: Clear distinction
data = source.fetch_historical_data(...)  # From API
bars = storage.get_bars(...)              # From storage
logger.info("Pulled %d bars from storage", len(bars))

# ❌ Avoid: Ambiguous terminology
data = source.retrieve_historical_data(...)  # Unclear: API or storage?
bars = storage.retrieve_bars(...)           # Unclear: storage or API?
logger.info("Retrieved %d bars", len(bars))  # Unclear source
```

</details>

---

## 📝 Documentation Standards
<details><summary>Expand</summary>

- Prefer **Google-style** docstrings (NumPy OK for analytical code).  
- Validate completeness with `flake8-docstrings` or `pydocstyle`.  
- Generate docs automatically with `pdoc` in CI.  
- Avoid raw reStructuredText unless using Sphinx for API docs.

### Dates and Timestamps in Documentation

**Always use the current date when creating or updating documentation:**

- **Report dates:** Use the actual date when the document was created/updated (e.g., `2025-11-13`, not `2024-12-19` or `2025-01-15`)
- **"Last Updated" fields:** Update these when modifying documentation
- **Example dates in code samples:** Use realistic dates, but prefer recent past dates (e.g., `2024-01-01` for examples is fine)

**Important distinction - Documentation dates vs. Trading symbols:**

- **Documentation dates:** Use current/actual dates (report headers, "Last Updated", etc.)
- **Trading symbols:** Futures and options contracts use expiration dates in their symbols (e.g., `ESZ26` for Dec 2026 futures is valid to trade today - that's how futures markets work!)
- **Example symbols in docs:** When showing examples, use realistic contract symbols that would be tradeable (e.g., `ESZ26` is fine if Dec 2026 contracts are available)

**Common mistakes to avoid:**
- ❌ Using future dates that haven't occurred yet **in documentation metadata** (report dates, "Last Updated" fields)
- ❌ Using dates from months/years that don't match when you're actually working **on the documentation**
- ❌ Copying dates from other documents without updating them
- ❌ Using placeholder dates like `2024-01-01` in report headers

**Note:** These rules apply to **documentation dates**, not to trading contract expiration dates. Trading December 2026 futures contracts (`ESZ26`) today is perfectly normal and expected - futures contracts are designed to trade months or years before expiration.

**Best practices:**
- ✅ Check the current date before writing documentation
- ✅ Use `date +%Y-%m-%d` or system date when unsure
- ✅ Update "Last Updated" fields when modifying existing docs
- ✅ Use relative dates in examples (e.g., "last 30 days" instead of hardcoded dates)
- ✅ Use valid, tradeable contract symbols in examples (including future-dated contracts)

**Example:**
```python
def calculate_portfolio_value(
    positions: dict[str, float],
    prices: dict[str, float],
    currency: str = "USD"
) -> float:
    """Calculate total portfolio value in specified currency.

    Args:
        positions: Dictionary mapping ticker symbols to quantities held.
        prices: Dictionary mapping ticker symbols to current prices.
        currency: Target currency for valuation (default: USD).

    Returns:
        Total portfolio value in the specified currency.

    Raises:
        ValueError: If any ticker in positions is missing from prices.
        
    Example:
        >>> positions = {"AAPL": 10, "GOOGL": 5}
        >>> prices = {"AAPL": 150.0, "GOOGL": 2800.0}
        >>> calculate_portfolio_value(positions, prices)
        15500.0
    """
    # Implementation here
```

</details>

---

## 🧪 Testing & CI/CD
<details><summary>Expand</summary>

- **≥95% test coverage** measured via `pytest-cov`.  
- All tests must pass in CI before merge.  
- Use **fixtures** for shared test dependencies.  
- Mock external services (APIs, databases).  
- Run tests with `-vv` for verbose output in CI.  
- Include **integration tests** for critical paths.  
- Test edge cases: empty inputs, null values, boundary conditions.  
- Use **parametrize** for testing multiple inputs efficiently.

**CI Pipeline Must Include:**
1. Linting (`black --check`, `flake8`)
2. Type checking (`mypy --strict`)
3. Tests with coverage (`pytest --cov`)
4. Security scan (`pip-audit`, `bandit`)
5. Complexity check (`radon cc --min B`)
6. Documentation validation (`pydocstyle`)

</details>

---

## 🔒 Security, Secrets & Dependency Hygiene
<details><summary>Expand</summary>

- No secrets in source control; use `.env` and `.gitignore`.  
- Run `pip-audit` or `safety` weekly in CI.  
- Pin dependencies in `environment.yml`.  
- Secrets injected at runtime, never during import.  
- Centralize credential access in `secrets_manager.py`.  
- Mock secrets in tests; never use real credentials.  
- Enable **Dependabot** or scheduled jobs for routine dependency updates.  

</details>

---

## 🪵 Logging & Error Handling
<details><summary>Expand</summary>

- Use structured logging with context (`logger.info("msg", extra={...})`).  
- Log at appropriate levels: DEBUG, INFO, WARNING, ERROR, CRITICAL.  
- Never log sensitive data (passwords, API keys, PII).  
- Include correlation IDs for request tracing.  
- Catch specific exceptions, avoid bare `except:`.  
- Log exceptions with stack traces (`logger.exception("error")`).  
- Use `logging.getLogger(__name__)` for module-specific loggers.

### Defensive Programming & Safe Data Access

**Prevent IndexError and KeyError through validation:**

- **Always validate before accessing indices:**
  ```python
  # ✅ Good: Check bounds before access
  if len(items) > 0:
      value = items[0]
  else:
      value = default_value
  
  # ✅ Good: Check DataFrame/Series before .iloc access
  if not df.empty and len(df) > 0:
      last_value = df.iloc[-1]
  
  # ❌ Bad: Direct access without validation
  value = items[0]  # IndexError if empty
  last_value = df.iloc[-1]  # IndexError if empty
  ```

- **Use `.get()` for dictionary access with defaults:**
  ```python
  # ✅ Good: Safe dictionary access
  value = config.get("key", default_value)
  nested = settings.get("section", {}).get("key", "default")
  
  # ❌ Bad: Direct key access
  value = config["key"]  # KeyError if missing
  nested = settings["section"]["key"]  # KeyError if missing
  ```

- **Validate DataFrame/Series structure before access:**
  ```python
  # ✅ Good: Check columns and emptiness
  if not df.empty and "Close" in df.columns and len(df) > 0:
      price = df["Close"].iloc[-1]
  
  # ✅ Good: Check index before .loc access
  if timestamp in series.index:
      value = series.loc[timestamp]
  else:
      value = series.iloc[-1] if len(series) > 0 else default_value
  
  # ❌ Bad: Direct access without checks
  price = df["Close"].iloc[-1]  # IndexError or KeyError possible
  value = series.loc[timestamp]  # KeyError if timestamp missing
  ```

- **Validate list/array bounds before access:**
  ```python
  # ✅ Good: Check length before accessing specific indices
  if len(legs) >= 4:
      leg = legs[3]
  else:
      raise ValueError("Insufficient legs for strategy")
  
  # ✅ Good: Check tuple/list unpacking
  if len(row) >= 8:
      trade_id, symbol, entry_time = row[0], row[1], row[2]
  else:
      logger.warning(f"Incomplete row data: {row}, skipping")
      continue
  
  # ❌ Bad: Direct index access
  leg = legs[3]  # IndexError if len(legs) < 4
  trade_id = row[0]  # IndexError if row is shorter than expected
  ```

- **Prefer validation over exception handling when possible:**
  ```python
  # ✅ Good: Validate first, then access
  if key in dictionary:
      value = dictionary[key]
  
  # ⚠️ Acceptable: Try/except for expected cases
  try:
      value = dictionary[key]
  except KeyError:
      value = default_value
  
  # ❌ Bad: Relying on exceptions for control flow
  try:
      value = dictionary[key]
  except KeyError:
      pass  # Silent failure
  ```

**Rationale:**
- Prevents runtime crashes from IndexError/KeyError
- Makes code intent explicit (validation vs. error handling)
- Improves debuggability (failures happen at validation point)
- Reduces exception overhead in hot paths
- Makes edge cases visible in code review

</details>

---

## ⏱️ Runtime Operations & Observability
<details><summary>Expand</summary>

Every long-running process must provide:  
- Health checks or a callable status method.  
- Regular heartbeat logs (INFO).  
- Error-rate tracking or recent-failure counts.  

All alert logic must log:  
- Trigger condition  
- Data values causing trigger  
- Timestamp  
- Delivery result (success/fail + channel)  
- **Stable event ID** for end-to-end traceability.  

</details>

---

## 🚀 Performance & Complexity
<details><summary>Expand</summary>

- Prefer O(n log n) algorithms; avoid O(n²).  
- Profile performance bottlenecks.  
- Document assumptions in README.  
- Complexity > 15 requires explicit justification in PR.  
- Enforce `radon` / `flake8-complexity` thresholds in pre-commit and CI; any function > 15 lines requires a justification note in the PR.  

</details>

---

## 🧩 Version Control & Code Review
<details><summary>Expand</summary>

- Use **Conventional Commits**: `feat:`, `fix:`, `docs:`, `test:`, `refactor:`, `chore:`.  
- Keep commits atomic and focused.  
- Write descriptive PR descriptions with context.  
- Link PRs to issues/tickets.  
- Require at least one approval before merge.  
- Squash merge for feature branches.  
- Protect main branch with CI checks.

</details>

---

## 📄 Knowledge Transfer & Hand-off
<details><summary>Expand</summary>

- Maintain up-to-date README with setup instructions.  
- Document architectural decisions in ADRs (Architecture Decision Records).  
- Include runbook for operational procedures.  
- Create video walkthroughs for complex systems.  
- Schedule knowledge-sharing sessions before transitions.  

</details>

---

## 🧰 Operational Enforcement Tools
<details><summary>Expand</summary>

- **black** – Auto-formatting  
- **flake8** – Linting  
- **mypy** – Type checking  
- **pytest + pytest-cov** – Testing  
- **pydocstyle** – Doc validation  
- **pre-commit** – Hook enforcement  
- **pip-audit / safety** – Dependency security  
- **radon** – Complexity measurement  
- **bandit** – Security linting

**Pre-commit Configuration:**
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.12.1
    hooks:
      - id: black
  
  - repo: https://github.com/pycqa/flake8
    rev: 7.0.0
    hooks:
      - id: flake8
        args: [--max-line-length=88, --extend-ignore=E203]
  
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.8.0
    hooks:
      - id: mypy
        args: [--strict]
  
  - repo: local
    hooks:
      - id: check-standards-reference
        name: Check standards reference in new modules
        entry: python scripts/check_standards_reference.py
        language: python
        pass_filenames: true
      
      - id: check-complexity
        name: Check cyclomatic complexity
        entry: radon cc --min B --show-complexity
        language: system
        pass_filenames: true
```

</details>

---

## 📚 Appendix A – Software Craftsmanship Principles
<details><summary>Expand</summary>

1. **Code is read more than written** – Optimize for readability.
2. **Simple beats clever** – Prefer straightforward solutions.
3. **Explicit beats implicit** – Make intentions clear.
4. **Fail fast, fail loud** – Catch errors early with clear messages.
5. **Don't repeat yourself (DRY)** – Extract common logic.
6. **Separation of concerns** – Each module has one responsibility.
7. **Test behavior, not implementation** – Tests should survive refactoring.
8. **Documentation is code** – Keep docs in sync with implementation.
9. **Automate the boring stuff** – Use tools to enforce standards.
10. **Leave code better than you found it** – Boy Scout Rule.

</details>

---

## ✅ Appendix B – Enforcement Checklist
<details><summary>Expand</summary>

**Before Every Commit:**
- [ ] Code formatted with `black`
- [ ] Linting passes (`flake8`)
- [ ] Type checking passes (`mypy --strict`)
- [ ] All tests pass locally
- [ ] Coverage ≥95%
- [ ] Docstrings complete
- [ ] No secrets in code
- [ ] Complexity ≤10 (or justified if >15)

**Before Every PR:**
- [ ] Conventional commit messages
- [ ] PR description includes context
- [ ] Linked to relevant issues
- [ ] CI pipeline passes
- [ ] Security scan passes
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] Standards reference checked

**Before Every Release:**
- [ ] Version bumped (semantic versioning)
- [ ] CHANGELOG.md finalized
- [ ] Release notes written
- [ ] Tags created
- [ ] Dependencies audited
- [ ] Deployment tested in staging

</details>

---

> _End of ENGINEERING_STANDARDS_MASTER.md – Revision 3.4, November 26, 2025_
