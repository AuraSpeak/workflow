# Aura-Speak Workflow

Workflow scripts and conventions for Aura-Speak development.

---

## Overview

This repo holds scripts and rules to clone the Aura-Speak repositories and work on them locally in a Go workspace layout.

Everything is driven via **just** from the workflow root (see [justfile](justfile)).

### Just commands

| Command | Purpose |
|---------|---------|
| `just setup` | Clone all repos into `src/`, create `go.work`, inject replace directives, install pre-push hooks (root + each module), and copy the module justfile into each `src/<module>/`. |
| `just inject-replace` | Re-inject local replace directives into all `go.mod` files (e.g. after pull, when remote has no replace). |
| `just install-hooks` | Install pre-push hook in workflow root and in each `src/<module>/.git/hooks`. |
| `just copy-module-justfile` | Copy `scripts/justfile.module` into each `src/<module>/justfile`. |
| `just bootstrap` | Run `go generate` across all modules. |
| `just test-all` | Run tests across all modules. |
| `just act` | Run GitHub Actions locally (act) in each repo; logs in `act-logs/`. See `scripts/run_act.py`. |

### Scripts (used by just)

| Script | Purpose |
|--------|---------|
| `scripts/clone-all.sh` | Clones all repos (`protocol`, `client`, `server`, `debug-ui`, `network`) into `src/`. |
| `scripts/go-work-init.sh` | Creates `go.work` and calls `inject-go-replace.sh`. |
| `scripts/inject-go-replace.sh` | Idempotently injects local `replace` directives into each `go.mod` (strip then append). |
| `scripts/strip-go-replace.sh` | Removes `replace` directives from `src/*/go.mod` (or a single module if passed as argument). |
| `scripts/setup-hooks.sh` | Installs pre-push hook in root and in each `src/<module>/.git/hooks`. |
| `scripts/modules` | Single list of module names (one line); add a new repo here and in inject’s replace blocks. |

> **Note:** The target repos must exist under `https://github.com/aura-speak/`. If they are not created yet, the scripts will fail.

### go.mod replace (local only)

The `go.mod` files under `src/` must **not** contain `replace` directives in the remote repo; they are for local development only. `just setup` (or `just inject-replace`) injects them. Before push, the pre-push hook runs `strip-go-replace.sh` so `replace` never reaches the remote. If the hook strips anything, it aborts the push and asks you to commit and push again. After push, run `just inject-replace` to re-add replace for local work.

---

## Dev Rules

### Versioning (SemVer)

| Type   | Format   | When to use |
|--------|----------|-------------|
| **Major** | `X.0.0` | API or other breaking changes that may break existing parts. |
| **Minor** | `0.X.0` | Small additions (e.g. new routing part, new packet type). |
| **Patch** | `0.0.X` | Bugfixes without API changes. |

---

## License

See [LICENSE](LICENSE).
