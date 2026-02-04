#!/usr/bin/env python3
"""
Run `act` in each repo under src/, write per-repo logs and an optional combined log,
then print and optionally save a summary (status, exit code, duration, log path).

Reads GITHUB_TOKEN from .env in the workflow repo root for repo/API access.
Run from workflow repo root; uses scripts/ location to resolve repo root.
"""

import argparse
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

EVENT_REF_MAIN = "refs/heads/main"
EVENT_REF_TAG = "refs/tags/v0.0.0-pre0.1"

# Workflow filenames by trigger: act does not filter by ref, so we run only these per event.
WORKFLOWS_PUSH_MAIN = ("ci.yml", "scorecard.yml", "govulncheck.yml")
WORKFLOWS_PUSH_TAG = ("release.yml",)


def repo_root() -> Path:
    """Directory containing scripts/ (workflow repo root)."""
    return Path(__file__).resolve().parent.parent


def discover_repos(src_dir: Path) -> list[str]:
    """
    Return repo names: directories under src_dir that contain .github/workflows/.
    """
    repos = []
    if not src_dir.is_dir():
        return repos
    for entry in sorted(src_dir.iterdir()):
        if entry.is_dir() and (entry / ".github" / "workflows").is_dir():
            repos.append(entry.name)
    return repos


def _expand_env(value: str) -> str:
    """Replace ${VAR} in value with os.environ.get('VAR', '')."""
    def repl(m: re.Match) -> str:
        return os.environ.get(m.group(1), "")
    return re.sub(r"\$\{([^}]+)\}", repl, value)


def load_github_token(root: Path) -> str | None:
    """
    Read .env in root; return value of GITHUB_TOKEN= or None if missing/not found.
    Simple format: one KEY=VALUE per line. ${VAR} in the value is expanded from the environment.
    """
    env_file = root / ".env"
    if not env_file.is_file():
        return None
    try:
        with open(env_file, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("GITHUB_TOKEN="):
                    raw_value = line[13:].strip().strip("'\"")
                    value = _expand_env(raw_value)
                    return value if value else None
    except OSError:
        pass
    return None


def ensure_event_files(log_dir: Path) -> tuple[Path, Path]:
    """Create event_push_main.json and event_push_tag.json in log_dir; return (main_path, tag_path)."""
    main_path = log_dir / ".event_push_main.json"
    tag_path = log_dir / ".event_push_tag.json"
    with open(main_path, "w", encoding="utf-8") as f:
        json.dump({"ref": EVENT_REF_MAIN}, f)
    with open(tag_path, "w", encoding="utf-8") as f:
        json.dump({"ref": EVENT_REF_TAG}, f)
    return (main_path, tag_path)


def get_workflow_paths(repo_path: Path, filenames: tuple[str, ...]) -> list[str]:
    """
    Return relative paths (e.g. .github/workflows/ci.yml) for workflow files that exist
    in repo_path/.github/workflows/ and whose name is in filenames.
    """
    workflows_dir = repo_path / ".github" / "workflows"
    if not workflows_dir.is_dir():
        return []
    return [
        f".github/workflows/{f.name}"
        for f in workflows_dir.iterdir()
        if f.is_file() and f.name in filenames
    ]


def _run_act_once(
    repo_path: Path,
    event: str,
    env: dict[str, str],
    event_file: Path | None,
    workflow_path: str | None,
) -> tuple[int, str, float]:
    """Run act once. If workflow_path is set, pass -W workflow_path. Return (returncode, output, duration)."""
    start = time.perf_counter()
    act_cmd: list[str] = ["act", event]
    if event_file is not None:
        act_cmd.extend(["-e", str(event_file)])
    if workflow_path is not None:
        act_cmd.extend(["-W", workflow_path])
    token_val = env.get("GITHUB_TOKEN")
    if token_val:
        act_cmd.extend(["-s", f"GITHUB_TOKEN={token_val}", "-s", f"GITHUB_AUTH_TOKEN={token_val}"])
    try:
        result = subprocess.run(
            act_cmd,
            cwd=repo_path,
            env=env,
            capture_output=True,
            text=True,
            timeout=3600,
        )
        duration = time.perf_counter() - start
        out = (result.stdout or "") + (result.stderr or "")
        return (result.returncode, out, duration)
    except subprocess.TimeoutExpired:
        duration = time.perf_counter() - start
        return (-1, "act timed out after 3600s\n", duration)
    except FileNotFoundError:
        duration = time.perf_counter() - start
        return (-1, "act not found (install e.g. via brew install act)\n", duration)
    except Exception as e:
        duration = time.perf_counter() - start
        return (-1, f"Error running act: {e}\n", duration)


def run_act(
    repo_path: Path,
    event: str,
    env: dict[str, str],
    event_file: Path | None = None,
    workflow_paths: list[str] | None = None,
) -> tuple[int, str, float]:
    """
    Run act in repo_path with the given event and environment.
    If event_file is set, pass -e event_file to act.
    If workflow_paths is set, run act once per path (act uses only the last -W when given multiple)
    and aggregate: returncode = max, output = concatenated, duration = sum.
    Return (returncode, combined stdout+stderr, duration_seconds).
    """
    if not workflow_paths:
        return _run_act_once(repo_path, event, env, event_file, None)
    all_out: list[str] = []
    max_rc = 0
    total_dur = 0.0
    for w in workflow_paths:
        rc, out, dur = _run_act_once(repo_path, event, env, event_file, w)
        max_rc = max(max_rc, rc)
        total_dur += dur
        all_out.append(out)
    return (max_rc, "\n".join(all_out), total_dur)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run act in each repo under src/, write logs and a summary."
    )
    parser.add_argument(
        "--event",
        default="push",
        help="Event to pass to act (default: push)",
    )
    parser.add_argument(
        "--log-dir",
        default="act-logs",
        help="Directory for log files, relative to repo root (default: act-logs)",
    )
    parser.add_argument(
        "--no-combined",
        action="store_true",
        help="Do not write a combined log file",
    )
    parser.add_argument(
        "--summary-file",
        default=None,
        metavar="PATH",
        help="Write summary to this path (default: log-dir/summary.txt); pass empty string to skip file",
    )
    parser.add_argument(
        "--repos",
        default=None,
        metavar="LIST",
        help="Comma-separated list of repo names to run (default: all). Example: client,server,protocol",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List available repos and exit",
    )
    parser.add_argument(
        "--single-event",
        action="store_true",
        help="Run act once per repo with default event (no push-main/push-tag split); scorecard may fail",
    )
    args = parser.parse_args()

    root = repo_root()
    src_dir = root / "src"
    log_dir = root / args.log_dir
    log_dir.mkdir(parents=True, exist_ok=True)

    all_repos = discover_repos(src_dir)
    if not all_repos:
        print("No repos with .github/workflows/ found under src/", file=sys.stderr)
        return 1

    if args.list:
        for r in all_repos:
            print(r)
        return 0

    if args.repos:
        wanted = {s.strip() for s in args.repos.split(",") if s.strip()}
        repos = [r for r in all_repos if r in wanted]
        unknown = wanted - set(all_repos)
        if unknown:
            print(f"Unknown repo(s): {', '.join(sorted(unknown))}", file=sys.stderr)
            print(f"Available: {', '.join(all_repos)}", file=sys.stderr)
            return 1
        if not repos:
            print("No repos selected.", file=sys.stderr)
            return 1
    else:
        repos = all_repos

    token = load_github_token(root)
    base_env = os.environ.copy()
    if token:
        base_env["GITHUB_TOKEN"] = token
        base_env["GITHUB_AUTH_TOKEN"] = token  # used by e.g. ossf/scorecard-action
    if not token:
        print(
            "Note: GITHUB_TOKEN not found in .env; using existing env or act may fail for private repos.",
            file=sys.stderr,
        )

    results: list[tuple[str, int, float, Path]] = []
    combined_lines: list[str] = []
    n = len(repos)
    single_event = args.single_event

    if single_event:
        print(f"Running act (event={args.event}, single run) in {n} repo(s): {', '.join(repos)}")
    else:
        print(f"Running act (push main + push tag) in {n} repo(s): {', '.join(repos)}")
    print()

    if not single_event:
        event_main_path, event_tag_path = ensure_event_files(log_dir)

    for i, repo in enumerate(repos, 1):
        repo_path = src_dir / repo
        if not repo_path.is_dir():
            print(f"  [{i}/{n}] {repo}: skip (not a directory)")
            continue
        log_path = log_dir / f"{repo}.log"

        if single_event:
            print(f"  [{i}/{n}] {repo}: running ...", flush=True)
            returncode, output, duration = run_act(repo_path, args.event, base_env)
            results.append((repo, returncode, duration, log_path))
            status = "OK" if returncode == 0 else "FAIL"
            print(f"  [{i}/{n}] {repo}: {status} (exit {returncode}, {duration:.1f}s) -> {log_path}", flush=True)
            with open(log_path, "w", encoding="utf-8") as f:
                f.write(output)
            sep = f"\n{'='*60}\n{repo} | act {args.event} | exit {returncode} | {duration:.1f}s\n{'='*60}\n"
            combined_lines.append(sep + output)
        else:
            # Run 1: push main (only ci, scorecard, govulncheck – act does not filter by ref)
            main_workflows = get_workflow_paths(repo_path, WORKFLOWS_PUSH_MAIN)
            print(f"  [{i}/{n}] {repo}: push main ...", flush=True)
            rc_main, out_main, dur_main = run_act(
                repo_path, "push", base_env,
                event_file=event_main_path,
                workflow_paths=main_workflows if main_workflows else None,
            )
            status_main = "OK" if rc_main == 0 else "FAIL"
            print(f"  [{i}/{n}] {repo}: push main {status_main} (exit {rc_main}, {dur_main:.1f}s)", flush=True)
            # Run 2: push tag (only release workflow)
            tag_workflows = get_workflow_paths(repo_path, WORKFLOWS_PUSH_TAG)
            if tag_workflows:
                print(f"  [{i}/{n}] {repo}: push tag ...", flush=True)
                rc_tag, out_tag, dur_tag = run_act(
                    repo_path, "push", base_env,
                    event_file=event_tag_path,
                    workflow_paths=tag_workflows,
                )
                status_tag = "OK" if rc_tag == 0 else "FAIL"
                print(f"  [{i}/{n}] {repo}: push tag {status_tag} (exit {rc_tag}, {dur_tag:.1f}s) -> {log_path}", flush=True)
                returncode = max(rc_main, rc_tag)
                duration = dur_main + dur_tag
                block_main = f"\n{'='*60}\n{repo} | act push (refs/heads/main) | exit {rc_main} | {dur_main:.1f}s\n{'='*60}\n"
                block_tag = f"\n{'='*60}\n{repo} | act push (refs/tags/...) | exit {rc_tag} | {dur_tag:.1f}s\n{'='*60}\n"
                full_output = block_main + out_main + block_tag + out_tag
            else:
                rc_tag, out_tag, dur_tag = 0, "", 0.0
                returncode = rc_main
                duration = dur_main
                print(f"  [{i}/{n}] {repo}: push tag skipped (no release workflow) -> {log_path}", flush=True)
                block_main = f"\n{'='*60}\n{repo} | act push (refs/heads/main) | exit {rc_main} | {dur_main:.1f}s\n{'='*60}\n"
                full_output = block_main + out_main
            results.append((repo, returncode, duration, log_path))
            with open(log_path, "w", encoding="utf-8") as f:
                f.write(full_output)
            combined_lines.append(f"\n{'='*60}\n{repo} | main+tag | exit {returncode} | {duration:.1f}s\n{'='*60}\n" + full_output)

    print()

    if not args.no_combined:
        combined_path = log_dir / "combined.log"
        with open(combined_path, "w", encoding="utf-8") as f:
            f.write("\n".join(combined_lines))
        print(f"Wrote combined log: {combined_path}")

    summary_lines = [
        "Summary",
        "-------",
        f"{'repo':<12} {'status':<6} {'exit':<6} {'duration':<10} log",
        "-" * 50,
    ]
    for repo, returncode, duration, log_path in results:
        status = "OK" if returncode == 0 else "FAIL"
        summary_lines.append(
            f"{repo:<12} {status:<6} {returncode:<6} {duration:>8.1f}s  {log_path}"
        )
    summary_text = "\n".join(summary_lines)
    print(summary_text)

    summary_path = args.summary_file if args.summary_file is not None else str(log_dir / "summary.txt")
    if summary_path:
        summary_path = summary_path.strip()
    if summary_path:
        out_path = Path(summary_path)
        if not out_path.is_absolute():
            out_path = root / out_path
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(summary_text)

    return 0 if all(r[1] == 0 for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
