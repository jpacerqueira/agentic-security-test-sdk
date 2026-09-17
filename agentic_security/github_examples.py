"""Download a public GitHub repo zip into examples/ for use as a pipeline source tree.

Outbound hosts are always api.github.com / codeload.github.com, built from a
regex-parsed (owner, repo, ref) — never from a client-supplied host (SSRF-closed).
"""

from __future__ import annotations

import io
import json
import re
import shutil
import zipfile
from pathlib import Path
from urllib.parse import urlsplit

import httpx

_GITHUB_PATH = re.compile(r"^/([\w.-]+)/([\w.-]+?)(?:\.git)?(?:/tree/([\w./-]+))?/?$")
_MAX_ZIP_BYTES = 200 * 1024 * 1024
_MAX_UNCOMPRESSED = 500 * 1024 * 1024
_UA = "macro-search-agentic-security"


class GitHubFetchError(Exception):
    def __init__(self, status: int, detail: str):
        super().__init__(detail)
        self.status = status
        self.detail = detail


def parse_github_url(github_url: str) -> tuple[str, str, str | None]:
    parsed = urlsplit((github_url or "").strip())
    if parsed.scheme != "https" or parsed.netloc.lower() not in ("github.com", "www.github.com"):
        raise GitHubFetchError(
            400, "Enter a GitHub repository URL, e.g. https://github.com/owner/repo"
        )
    match = _GITHUB_PATH.match(parsed.path)
    if not match:
        raise GitHubFetchError(
            400, "Enter a GitHub repository URL, e.g. https://github.com/owner/repo"
        )
    return match.group(1), match.group(2), match.group(3)


def extract_zip_to_examples(
    content: bytes, safe_name: str, examples_dir: Path | None = None
) -> dict:
    examples_dir = Path(examples_dir or "examples")
    examples_dir.mkdir(exist_ok=True)
    dest = examples_dir / safe_name
    base = safe_name
    counter = 1
    while dest.exists():
        dest = examples_dir / f"{base}_{counter}"
        counter += 1
    dest.mkdir(parents=True)
    resolved_dest = dest.resolve()
    try:
        with zipfile.ZipFile(io.BytesIO(content)) as zf:
            names = [n for n in zf.namelist() if n not in ("/", "")]
            total = sum(zf.getinfo(n).file_size for n in names)
            if total > _MAX_UNCOMPRESSED:
                raise GitHubFetchError(413, "Archive too large once extracted — maximum is 500 MB.")
            common_root: str | None = None
            if names:
                first_root = names[0].split("/")[0]
                if all(n == first_root + "/" or n.startswith(first_root + "/") for n in names):
                    common_root = first_root
            for member in names:
                rel = member
                if common_root:
                    if rel == common_root + "/":
                        continue
                    rel = rel[len(common_root) + 1 :]
                if not rel:
                    continue
                target = (resolved_dest / rel).resolve()
                try:
                    target.relative_to(resolved_dest)
                except ValueError:
                    continue
                if member.endswith("/"):
                    target.mkdir(parents=True, exist_ok=True)
                else:
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(zf.read(member))
    except zipfile.BadZipFile as exc:
        shutil.rmtree(dest, ignore_errors=True)
        raise GitHubFetchError(400, "Invalid or corrupt zip file.") from exc
    except GitHubFetchError:
        shutil.rmtree(dest, ignore_errors=True)
        raise
    except Exception as exc:
        shutil.rmtree(dest, ignore_errors=True)
        raise GitHubFetchError(500, f"Extraction failed: {exc}") from exc
    return {"name": dest.name, "path": str(dest)}


def write_source_meta(dest: Path, github_url: str) -> None:
    (dest / ".source.json").write_text(
        json.dumps({"github_url": github_url}, indent=2), encoding="utf-8"
    )


def list_examples(examples_dir: Path | None = None) -> list[dict]:
    root = Path(examples_dir or "examples")
    out: list[dict] = []
    if not root.is_dir():
        return out
    for d in sorted(root.iterdir()):
        if not d.is_dir() or d.name.startswith("."):
            continue
        github_url = ""
        meta = d / ".source.json"
        if meta.exists():
            try:
                github_url = json.loads(meta.read_text(encoding="utf-8")).get("github_url") or ""
            except json.JSONDecodeError:
                github_url = ""
        out.append({"name": d.name, "path": str(d), "github_url": github_url})
    return out


def fetch_github_zip(owner: str, repo: str, ref: str | None) -> tuple[bytes, str]:
    headers = {"User-Agent": _UA, "Accept": "application/vnd.github+json"}
    timeout = httpx.Timeout(60.0)
    with httpx.Client(timeout=timeout, follow_redirects=True, headers=headers) as client:
        resolved = ref
        if not resolved:
            api = f"https://api.github.com/repos/{owner}/{repo}"
            try:
                resp = client.get(api)
            except httpx.HTTPError as exc:
                raise GitHubFetchError(502, f"Could not reach GitHub: {exc}") from exc
            if resp.status_code == 404:
                raise GitHubFetchError(404, f"Repository {owner}/{repo} not found (or private).")
            if resp.status_code >= 400:
                raise GitHubFetchError(
                    502,
                    f"GitHub API error while resolving default branch: {resp.status_code}",
                )
            try:
                resolved = resp.json()["default_branch"]
            except (KeyError, json.JSONDecodeError) as exc:
                raise GitHubFetchError(502, "Unexpected response from GitHub API.") from exc
        zip_url = f"https://codeload.github.com/{owner}/{repo}/zip/refs/heads/{resolved}"
        try:
            with client.stream("GET", zip_url, headers={"User-Agent": _UA}) as resp:
                if resp.status_code == 404:
                    raise GitHubFetchError(
                        404, f"Branch/ref '{resolved}' not found for {owner}/{repo}."
                    )
                if resp.status_code >= 400:
                    raise GitHubFetchError(
                        502, f"GitHub returned an error downloading the archive: {resp.status_code}"
                    )
                chunks: list[bytes] = []
                total = 0
                for chunk in resp.iter_bytes(1024 * 1024):
                    total += len(chunk)
                    if total > _MAX_ZIP_BYTES:
                        raise GitHubFetchError(
                            413, "Repository archive too large — maximum is 200 MB."
                        )
                    chunks.append(chunk)
                return b"".join(chunks), resolved
        except GitHubFetchError:
            raise
        except httpx.HTTPError as exc:
            raise GitHubFetchError(
                502, f"Could not download the repository archive: {exc}"
            ) from exc


def import_github_repo(github_url: str, examples_dir: Path | None = None) -> dict:
    owner, repo, ref = parse_github_url(github_url)
    content, resolved_ref = fetch_github_zip(owner, repo, ref)
    safe_name = re.sub(r"[^a-zA-Z0-9_\-]", "_", f"{owner}_{repo}").strip("_") or "github_repo"
    card = extract_zip_to_examples(content, safe_name, examples_dir=examples_dir)
    canonical = f"https://github.com/{owner}/{repo}"
    write_source_meta(Path(card["path"]), canonical)
    card["github_url"] = canonical
    card["ref"] = resolved_ref
    return card
