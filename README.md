# Aura-Speak Workflow

Workflow scripts and conventions for Aura-Speak development.

---

## Overview

This repo holds scripts and rules to clone the Aura-Speak repositories and work on them locally in a Go workspace layout.

### Scripts

| Script | Purpose |
|--------|---------|
| `scripts/clone-all.sh` | Clones all required repos (`protocol`, `router`, `client`, `server`, `debug-ui`) into `src/`. |
| `scripts/go-work-init.sh` | Creates a `go.work` file and wires in `protocol`, `router`, `client`, and `server` so you can develop across modules without re-cloning. |

> **Note:** The target repos must exist under `https://github.com/aura-speak/`. If they are not created yet, the scripts will fail.

---

## Usage (once the repos exist)

1. **Clone repos**
   ```bash
   ./scripts/clone-all.sh
   ```
   Creates `src/` with: `protocol`, `router`, `client`, `server`, `debug-ui`.

2. **Init Go workspace**
   ```bash
   ./scripts/go-work-init.sh
   ```
   Creates `go.work` in `src/` with `protocol`, `router`, `client`, `server`.

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
