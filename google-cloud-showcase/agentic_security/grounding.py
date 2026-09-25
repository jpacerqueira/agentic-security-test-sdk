"""Per-run evidence pack for Ultra-Professional LLM grounding.

Scrapes the assessment's own source tree (and, when the tree came from GitHub,
public repo metadata via api.github.com). Outbound hosts are never taken from
a client-supplied URL — same SSRF-closed construction as github_examples.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any
import json
import logging
import re

import httpx

from agentic_security.github_examples import GitHubFetchError, parse_github_url

log = logging.getLogger("agentic_security.grounding")

_SKIP_DIRS = {
    ".git",
    ".venv",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    "dist",
    "build",
    ".mypy_cache",
}
_MANIFESTS = (
    "README.md",
    "README",
    "readme.md",
    "pyproject.toml",
    "package.json",
    "requirements.txt",
    "go.mod",
    "pom.xml",
    "Cargo.toml",
    "Dockerfile",
    "docker-compose.yml",
    ".source.json",
)
_ROUTE = re.compile(
    r"""(?:\.(?:get|post|put|patch|delete)\(\s*['\"](/[^'\"]+)['\"]"""
    r"""|['\"](/(?:api|login|runs|health|admin)[^'\"]{0,60})['\"])""",
    re.I,
)
_SECRETISH = re.compile(
    r"(api[_-]?key|password|secret|token|AKIA[0-9A-Z]{8,})\s*[=:]\s*['\"]?([^\s'\"]+)",
    re.I,
)
_UA = "macro-search-agentic-security"


def _iter_files(root: Path):
    for p in root.rglob("*"):
        if not p.is_file():
            continue
        if any(part in _SKIP_DIRS for part in p.parts):
            continue
        yield p


def _read_excerpt(path: Path, limit: int = 1800) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")[:limit]
    except OSError:
        return ""


def _github_url_from_tree(root: Path, target_url: str) -> str:
    meta = root / ".source.json"
    if meta.exists():
        try:
            url = json.loads(meta.read_text(encoding="utf-8")).get("github_url") or ""
            if url:
                return url
        except json.JSONDecodeError:
            pass
    if target_url and "github.com" in target_url.lower():
        return target_url
    return ""


def fetch_github_meta(github_url: str) -> dict[str, Any]:
    """Public repo description/topics. Host is always api.github.com."""
    try:
        owner, repo, _ref = parse_github_url(github_url)
    except GitHubFetchError as exc:
        return {"error": exc.detail}
    api = f"https://api.github.com/repos/{owner}/{repo}"
    headers = {"User-Agent": _UA, "Accept": "application/vnd.github+json"}
    try:
        with httpx.Client(timeout=20.0, follow_redirects=True, headers=headers) as client:
            resp = client.get(api)
    except httpx.HTTPError as exc:
        return {"error": f"Could not reach GitHub: {exc}"}
    if resp.status_code == 404:
        return {"error": f"Repository {owner}/{repo} not found (or private)."}
    if resp.status_code >= 400:
        return {"error": f"GitHub API {resp.status_code}"}
    try:
        data = resp.json()
    except json.JSONDecodeError:
        return {"error": "Unexpected GitHub API response"}
    return {
        "full_name": data.get("full_name") or f"{owner}/{repo}",
        "description": data.get("description") or "",
        "language": data.get("language") or "",
        "topics": data.get("topics") or [],
        "default_branch": data.get("default_branch") or "",
        "html_url": f"https://github.com/{owner}/{repo}",
        "license": (data.get("license") or {}).get("spdx_id") or "",
    }


def collect_grounding(
    source_path: str,
    *,
    target_url: str = "",
    client_name: str = "",
    github_meta: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a fact pack from this run's tree. Safe with or without network."""
    root = Path(source_path) if source_path else None
    facts: list[dict[str, Any]] = []
    inventory = {"files": 0, "extensions": {}, "top_files": []}
    github_url = ""
    if root and root.is_dir():
        github_url = _github_url_from_tree(root, target_url)
        files = list(_iter_files(root))
        inventory["files"] = len(files)
        exts: dict[str, int] = {}
        names: list[str] = []
        for p in files:
            ext = p.suffix.lower() or "none"
            exts[ext] = exts.get(ext, 0) + 1
            try:
                names.append(str(p.relative_to(root)))
            except ValueError:
                names.append(p.name)
        inventory["extensions"] = dict(sorted(exts.items(), key=lambda kv: -kv[1])[:12])
        inventory["top_files"] = sorted(names)[:40]
        n = 1
        for name in _MANIFESTS:
            path = root / name
            if not path.is_file():
                continue
            text = _read_excerpt(path)
            if not text.strip():
                continue
            facts.append(
                {
                    "id": f"G-{n:03d}",
                    "kind": "manifest",
                    "path": name,
                    "text": text,
                }
            )
            n += 1
        for p in files:
            if p.suffix.lower() not in {".py", ".js", ".ts", ".java", ".go", ".cs"}:
                continue
            raw = _read_excerpt(p, 4000)
            if not raw:
                continue
            rel = str(p.relative_to(root)) if root in p.parents or p.parent == root else p.name
            routes = [g for m in _ROUTE.finditer(raw) for g in m.groups() if g]
            if routes:
                facts.append(
                    {
                        "id": f"G-{n:03d}",
                        "kind": "route",
                        "path": rel,
                        "text": ", ".join(routes[:8]),
                    }
                )
                n += 1
            secrets = _SECRETISH.findall(raw)
            if secrets:
                kinds = sorted({s[0] for s in secrets})[:6]
                facts.append(
                    {
                        "id": f"G-{n:03d}",
                        "kind": "secret_pattern",
                        "path": rel,
                        "text": "Literal assignment-like names in source: " + ", ".join(kinds),
                    }
                )
                n += 1
            if n > 40:
                break
    if github_meta and not github_meta.get("error"):
        facts.append(
            {
                "id": f"G-{len(facts)+1:03d}",
                "kind": "github",
                "path": github_meta.get("html_url") or github_url,
                "text": json.dumps(
                    {
                        k: github_meta.get(k)
                        for k in (
                            "full_name",
                            "description",
                            "language",
                            "topics",
                            "license",
                        )
                    },
                    indent=2,
                ),
            }
        )
    pack = {
        "enabled": True,
        "client": client_name,
        "source_path": source_path,
        "target_url": target_url,
        "github_url": github_url,
        "github_meta": github_meta or {},
        "inventory": inventory,
        "facts": facts,
        "contract": (
            "Use only the facts below. Cite fact ids (G-00n) next to any claim. "
            "If a detail is not in this pack, write unknown — do not invent hosts, "
            "CVEs, staff names, or product features."
        ),
    }
    return pack


def collect_grounding_for_run(source_path: str, target_url: str = "", client_name: str = "") -> dict[str, Any]:
    """Sync helper used from asyncio.to_thread: local scrape + optional GitHub API."""
    root = Path(source_path) if source_path else None
    github_url = _github_url_from_tree(root, target_url) if root and root.is_dir() else ""
    meta: dict[str, Any] = {}
    if github_url:
        meta = fetch_github_meta(github_url)
        if meta.get("error"):
            log.warning("github meta skipped: %s", meta["error"])
    return collect_grounding(
        source_path,
        target_url=target_url,
        client_name=client_name,
        github_meta=meta or None,
    )


def format_grounding_prompt(pack: dict[str, Any] | None, limit: int = 7000) -> str:
    if not pack or not pack.get("enabled"):
        return ""
    lines = [pack.get("contract") or "", "Grounding facts for this run:"]
    for fact in pack.get("facts") or []:
        lines.append(
            f"- {fact.get('id')} [{fact.get('kind')}] {fact.get('path')}: {fact.get('text')}"
        )
    inv = pack.get("inventory") or {}
    lines.append(
        f"Inventory: {inv.get('files', 0)} files; extensions={inv.get('extensions')}"
    )
    return "\n".join(lines)[:limit]
