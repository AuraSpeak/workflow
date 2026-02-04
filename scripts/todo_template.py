#!/usr/bin/env python3
"""
Write an implementation checklist template to todos/ (or --output).
Run from workflow repo root; uses scripts/ location to resolve repo root.
"""

import argparse
import re
from pathlib import Path


VALID_MODULES = frozenset({"client", "server", "protocol", "network", "debug-ui", "all"})


def slug_from_name(name: str) -> str:
    """Lowercase, replace non-alphanumeric with '-', collapse dashes, strip."""
    s = name.lower().strip()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = re.sub(r"-+", "-", s).strip("-")
    return s or "task"


def repo_root() -> Path:
    """Directory containing scripts/ (workflow repo root)."""
    return Path(__file__).resolve().parent.parent


def build_template(name: str, module: str) -> str:
    """Build markdown checklist; conditionally include Protocol and Debug-UI sections."""
    show_protocol = module in ("protocol", "all")
    show_debug_ui = module in ("debug-ui", "all")

    lines = [
        f"# Implementation: {name}",
        "",
        f"Module(s): {module}",
        "",
        "## Checklist",
        "",
    ]

    if show_protocol:
        lines.extend([
            "- [ ] **Protocol** (if packets): Update `src/protocol/packets.yaml`, run `go generate ./protocol/...` in `src/`.",
            "",
        ])

    lines.extend([
        "- [ ] **Code**: Implementation in the relevant module(s) under `src/`.",
        "",
        "- [ ] **Tests**: Unit tests; `go test ./...` in module(s); `just test-all` from workflow root.",
        "",
        "- [ ] **Documentation**: Package/public comments; update module README (Requirements, Structure, Quick start, Testing).",
        "",
    ])

    if show_debug_ui:
        lines.extend([
            "- [ ] **Debug-UI** (if applicable): Backend route + handler; frontend API + types; UI components/states.",
            "",
        ])

    lines.extend([
        "- [ ] **Versioning**: Bump SemVer (minor for feature, patch for fix).",
        "",
        "- [ ] **Build**: `just bootstrap` and `just test-all` from workflow root.",
        "",
    ])

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Write an implementation checklist template to todos/ (or --output)."
    )
    parser.add_argument(
        "--name",
        required=True,
        help="Feature/task name; used for title and filename slug.",
    )
    parser.add_argument(
        "--module",
        default="all",
        choices=sorted(VALID_MODULES),
        help="Affected module(s): client, server, protocol, network, debug-ui, or all (default: all).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output file path (default: todos/implement-<slug>.md under repo root).",
    )
    args = parser.parse_args()

    root = repo_root()
    slug = slug_from_name(args.name)
    out_path = args.output if args.output is not None else root / "todos" / f"implement-{slug}.md"

    out_path.parent.mkdir(parents=True, exist_ok=True)
    content = build_template(args.name, args.module)
    out_path.write_text(content, encoding="utf-8")
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
