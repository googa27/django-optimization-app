# Architecture — django-optimization-app

<!-- PORTFOLIO-CONSTITUTION:START -->
## Portfolio architecture baseline

Source of truth: `docs/ARCHITECTURE.yaml`. Tracking: [Project #24](https://github.com/users/googa27/projects/24), [django-optimization-app issue](https://github.com/googa27/django-optimization-app/issues/1). Profile: `application`; status: legacy/demo Django application, not production; enforcement: `Blocking`.

### Research-backed defaults

| Decision | Evidence | Repository application |
|---|---|---|
| Agent context | [Hermes context files](https://hermes-agent.nousresearch.com/docs/user-guide/features/context-files), [AGENTS.md](https://agents.md/) | Root `AGENTS.md`; progressive detail stays in linked docs. |
| AI tool escalation | [MCP tools specification](https://modelcontextprotocol.io/specification/2025-06-18/server/tools) | Stable CLI/contracts and skills first; plugin/MCP only after measured need and least-privilege review. |
| Python source layout | [PyPA src layout](https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/) | Declared Python roots: `none yet`. |
| Test layout | [pytest good practices](https://docs.pytest.org/en/stable/explanation/goodpractices.html) | Unit/integration/e2e/architecture boundaries are explicit. |
| Module budget | [Pylint too-many-lines rationale](https://pylint.readthedocs.io/en/latest/user_guide/messages/convention/too-many-lines.html) plus AI review locality | 500 physical lines is stricter than Pylint's broad default; existing excess is a no-growth ratchet. |
| Evolution | [Evolutionary architecture](https://evolutionaryarchitecture.com/precis.html) | Architecture characteristics have executable fitness functions and incremental exceptions. |
| Data layers | [Medallion architecture](https://learn.microsoft.com/en-us/azure/databricks/lakehouse/medallion) | Applied only where data is consumed; simple repos record an explicit non-use decision. |
| Python protocols | [Python data model](https://docs.python.org/3/reference/datamodel.html), [NumPy dispatch](https://numpy.org/doc/stable/user/basics.dispatch.html) | Dunders express true protocols/laws; named methods own policy and effects. |

### Maintained-library decision table

| Capability | Selected route | Alternatives | Boundary / custom-code rule |
|---|---|---|---|
| Linear programming optimization | PuLP 3.2.1 | CVXPY; SciPy `linprog`; Google OR-Tools; custom LP solver | `optimizador/services.py` owns PuLP use behind typed DTOs; views and result formatting do not construct solver models. Custom code is limited to validation/composition/adapters. |
| Architecture contract bootstrap | Python standard-library JSON parser over the JSON subset of YAML 1.2 | Hand-written YAML parser; mandatory platform service | Repo-local dependency-free structural gate; richer maintained tools remain repo-specific. |
| Import/dependency rules | Existing repo lint/import tools where configured; declarative YAML boundary is authoritative | Custom import framework | Keep custom AST checks narrow; use maintained Import Linter/Tach/Ruff/deptry when warranted. |
| AI interaction | AGENTS + deterministic CLI/contracts + capability discovery + skills | MCP/plugin in every repo | Escalate only after measured interoperability/lifecycle need. |

### Two-user design

- AI: AGENTS + deterministic Django management commands, the architecture checker, the pytest architecture suite, and capability notes; no MCP by default.
- Human/notebook: Typed optimization service API usable outside views and from notebooks; model value objects may use repr/eq/hash only when lawful.
- Planned Python protocols: Immutable optimization inputs/results may use __repr__/value equality after typed domain extraction.; Solver execution, database access, and web effects remain named methods.
- Core posture: No core coupling unless a general FPF optimization contract becomes a real consumer need.
- Data posture: Bounded CSV upload -> DataLoader validation -> typed ProductionParameters -> pure PuLP optimization service -> typed OptimizationSolution -> ResultsHandler presentation. Views coordinate only; no uploaded-file persistence is introduced.

### Modernization boundary

Django settings now read deployment-sensitive values from environment variables, default `DEBUG` to false, and set explicit upload size limits. Upload forms enforce `.csv`, content-type, and size boundaries before pandas parsing. Runtime web and CLI flows explicitly adapt the validated CSV row into typed `ProductionParameters`, solve through PuLP behind `ProductionOptimizationService`, and pass a typed `OptimizationSolution` to results formatting. The maintained solver choice is PuLP for this small linear-programming app; custom solver implementation is rejected.

### Extension and exception discipline

Probable extensions must cross named ports/capability registries rather than adding sibling modules indefinitely. Every exception is exact, risk-bearing, no-growth, and has a refactoring trigger. Generated/vendor/migration/resource paths are declared explicitly; they do not silently weaken runtime rules.
<!-- PORTFOLIO-CONSTITUTION:END -->
