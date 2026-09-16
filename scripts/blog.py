#!/usr/bin/env python3
"""Junwen'Log's local writing desk. Python standard library only."""
from __future__ import annotations

import argparse
import contextlib
import datetime as dt
import fcntl
import json
import os
from pathlib import Path
import re
import shutil
import signal
import socket
import subprocess
import sys
import tempfile
import time
import unicodedata
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "content"
STATE = ROOT / ".local"
SECTIONS = {"tech": "Tech", "notes": "Notes", "daily": "Daily"}
PREVIEW_URL = "http://localhost:1313/"
SHANGHAI = dt.timezone(dt.timedelta(hours=8), "Asia/Shanghai")
SLUG_RE = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")
SAFE_ROOT_FILES = {
    ".gitignore", ".gitmodules", ".editorconfig", "hugo.toml", "hugo.yaml",
    "hugo.json", "go.mod", "go.sum", "README.md", "LICENSE", "LICENSE.md",
    "package.json", "package-lock.json", "netlify.toml",
}
SAFE_DIRS = {"content", "config", "layouts", "assets", "static", "archetypes", "scripts", "docs"}


class BlogError(Exception):
    pass


def run(args, *, capture=False, check=True, cwd=None, **kwargs):
    result = subprocess.run([str(x) for x in args], cwd=cwd or ROOT, text=True,
                            capture_output=capture, **kwargs)
    if check and result.returncode:
        detail = (result.stderr or result.stdout or "").strip() if capture else ""
        raise BlogError(f"Command failed ({result.returncode}): {' '.join(str(x) for x in args[:3])}" +
                        (f"\n{detail}" if detail else ""))
    return result


def binary(name):
    for candidate in (Path.home() / ".local/bin" / name, Path("/opt/homebrew/bin") / name,
                      Path("/usr/local/bin") / name):
        if candidate.is_file() and os.access(candidate, os.X_OK):
            return str(candidate)
    found = shutil.which(name)
    if not found:
        raise BlogError(f"{name} is not installed or cannot be found in PATH.")
    return found


def git(*args, **kwargs):
    return run([binary("git"), *args], **kwargs)


def now():
    return dt.datetime.now(SHANGHAI).replace(microsecond=0)


def suggest_slug(title):
    ascii_title = unicodedata.normalize("NFKD", title).encode("ascii", "ignore").decode()
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_title.lower()).strip("-")[:80].rstrip("-")
    return slug or "note-" + now().strftime("%Y%m%d-%H%M%S")


def new_draft(section, title, slug, language="en"):
    title = title.strip()
    if section not in SECTIONS:
        raise BlogError("Section must be tech, notes, or daily. Posts lists all articles; create technical articles in tech.")
    if not title or len(title) > 200 or any(ord(c) < 32 for c in title):
        raise BlogError("Use a nonempty, single-line title (up to 200 characters).")
    if not SLUG_RE.fullmatch(slug) or len(slug) > 90:
        raise BlogError("The slug must use lowercase English letters, numbers and single hyphens, e.g. reading-on-the-train.")
    if language not in {"en", "zh-CN"}:
        raise BlogError("Language must be en or zh-CN.")
    bundle = CONTENT / section / slug
    if bundle.exists():
        raise BlogError(f"This article already exists; nothing was overwritten:\n{bundle}")
    bundle.mkdir(parents=True, exist_ok=False)
    path = bundle / "index.md"
    body = "Start with the idea, observation, or question you want to remember."
    if language == "zh-CN":
        body = "从一个值得记录的想法、见闻或问题开始。"
    text = "\n".join([
        "---", "title: " + json.dumps(title, ensure_ascii=False), "slug: " + slug,
        "date: " + now().isoformat(), "draft: true", "description: \"\"",
        "tags: []", "contentLanguage: " + language, "---", "", body, "",
    ])
    path.write_text(text, encoding="utf-8")
    return path


def frontmatter(text):
    match = re.match(r"\A---\r?\n(.*?)\r?\n---(?:\r?\n|$)", text, re.S)
    if not match:
        raise BlogError("This article must have YAML front matter delimited by ---.")
    return match


def is_draft(path):
    try:
        meta = frontmatter(path.read_text(encoding="utf-8")).group(1)
        return bool(re.search(r"(?m)^draft:\s*true\s*(?:#.*)?$", meta))
    except (BlogError, OSError):
        return False


def article_path(value):
    candidate = Path(value).expanduser()
    path = (candidate if candidate.is_absolute() else ROOT / candidate).resolve()
    if path.is_dir():
        path /= "index.md"
    try:
        rel = path.relative_to(CONTENT.resolve())
    except ValueError:
        raise BlogError("Choose an article inside this site's content directory.")
    if len(rel.parts) != 3 or rel.parts[0] not in SECTIONS or rel.name != "index.md" or not path.is_file():
        raise BlogError("Choose a page bundle's index.md under content/tech, content/notes or content/daily.")
    if not SLUG_RE.fullmatch(rel.parts[1]):
        raise BlogError("Article folder names must be lowercase English slugs.")
    return path


def open_editor(path=None, editor="obsidian"):
    if editor == "mweb":
        run(["/usr/bin/open", "-a", "MWeb", path or CONTENT])
    else:
        # Register content/ as a vault once in Obsidian's UI before using this URI.
        query = {"path": str(path or CONTENT)}
        run(["/usr/bin/open", "obsidian://open?" + urllib.parse.urlencode(query, quote_via=urllib.parse.quote)])


def preview_process():
    state_path = STATE / "preview.json"
    if not state_path.exists():
        return None
    try:
        data = json.loads(state_path.read_text())
        pid = int(data["pid"])
        command = run(["/bin/ps", "-p", str(pid), "-o", "command="], capture=True, check=False).stdout
        # Check ownership and the exact source marker before signalling a saved PID.
        if "hugo" in command and f"--source {ROOT}" in command and "server" in command:
            return pid
    except (ValueError, KeyError, OSError, json.JSONDecodeError):
        pass
    state_path.unlink(missing_ok=True)
    return None


def check_preview_port_available(port=1313):
    with socket.socket() as sock:
        # A stopped Hugo server may leave accepted connections in TIME_WAIT.
        # Like Hugo's listener, permit their reuse without sharing a live port.
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.bind(("127.0.0.1", port))
        except OSError:
            raise BlogError(f"Port {port} is being used by another process. Close it first; no process was stopped.")


def preview(open_browser=True):
    STATE.mkdir(exist_ok=True)
    if preview_process():
        print(f"Preview is already running: {PREVIEW_URL}")
        if open_browser:
            run(["/usr/bin/open", PREVIEW_URL])
        return
    check_preview_port_available()
    log_path = STATE / "preview.log"
    with log_path.open("w") as log:
        process = subprocess.Popen([
            binary("hugo"), "server", "--source", str(ROOT), "--bind", "127.0.0.1",
            "--port", "1313", "--baseURL", PREVIEW_URL, "--buildDrafts", "--buildFuture",
            "--disableFastRender", "--renderToMemory", "--noHTTPCache",
        ], cwd=ROOT, stdout=log, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL,
            start_new_session=True)
    (STATE / "preview.json").write_text(json.dumps({"pid": process.pid, "root": str(ROOT)}))
    for _ in range(80):
        if process.poll() is not None:
            (STATE / "preview.json").unlink(missing_ok=True)
            raise BlogError(f"Preview could not start. See {log_path}\n" + log_path.read_text()[-5000:])
        try:
            with urllib.request.urlopen(PREVIEW_URL, timeout=0.3) as response:
                if response.status == 200:
                    print(f"Preview, including drafts: {PREVIEW_URL}\nLog: {log_path}")
                    if open_browser:
                        run(["/usr/bin/open", PREVIEW_URL])
                    return
        except (OSError, TimeoutError):
            time.sleep(0.25)
    raise BlogError(f"Preview is still starting. Inspect {log_path} and run blog status.")


def stop_preview():
    pid = preview_process()
    if pid:
        os.killpg(pid, signal.SIGTERM)
        print("Local preview stopped.")
    else:
        print("No Junwen'Log preview is running.")
    (STATE / "preview.json").unlink(missing_ok=True)


def check():
    checker = ROOT / "scripts/check_site.py"
    if not checker.is_file():
        raise BlogError("scripts/check_site.py is missing; publishing requires the site's validation script.")
    with tempfile.TemporaryDirectory(prefix="junwen-log-build-") as temp:
        destination = Path(temp) / "public"
        run([binary("hugo"), "--environment", "production", "--gc", "--minify",
             "--destination", destination, "--cleanDestinationDir"])
        run([sys.executable, checker, "--public-dir", destination])
    print("Production build and site checks passed.")


def allowed_path(name):
    path = Path(name)
    parts = path.parts
    if path.is_absolute() or ".." in parts or not parts:
        return False
    if name in SAFE_ROOT_FILES or name == "themes/blowfish":
        return True
    if parts[:2] == (".github", "workflows"):
        return len(parts) == 3 and path.suffix in {".yml", ".yaml"}
    if parts[0] not in SAFE_DIRS:
        return False
    if any(p.startswith(".") or p.lower() in {"private", "secrets", "node_modules", "__pycache__"} for p in parts):
        return False
    if path.suffix.lower() in {".pem", ".key", ".p12", ".pfx", ".pyc", ".log"}:
        return False
    if path.name.lower() in {"credentials.json", "secrets.json", "token.txt", "id_rsa", "id_ed25519"}:
        return False
    return not (ROOT / path).is_symlink()


def git_paths(*args):
    return [s for s in git(*args, capture=True).stdout.split("\0") if s]


@contextlib.contextmanager
def publishing_lock():
    STATE.mkdir(exist_ok=True)
    with (STATE / "publish.lock").open("w") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise BlogError("Another publish is already running. Let it finish first.")
        yield


def site_url():
    result = run([binary("hugo"), "config", "--environment", "production", "--format", "json"], capture=True)
    data = json.loads(result.stdout)
    return data.get("baseURL") or data.get("baseurl") or ""


def watch_deployment(sha):
    try:
        gh = binary("gh")
    except BlogError:
        print("Pushed. Install/sign in to gh to watch deployment automatically.")
        return False
    if run([gh, "auth", "status"], capture=True, check=False).returncode:
        print("Pushed. GitHub CLI is not signed in; check Actions on GitHub for deployment status.")
        return False
    for _ in range(20):
        result = run([gh, "run", "list", "--commit", sha, "--limit", "10", "--json",
                      "databaseId,workflowName,status,conclusion"], capture=True, check=False)
        if result.returncode == 0:
            workflows = json.loads(result.stdout)
            pages = [w for w in workflows if any(term in w["workflowName"].lower() for term in ("pages", "deploy"))]
            if pages:
                run([gh, "run", "watch", str(pages[0]["databaseId"]), "--exit-status", "--interval", "5"])
                print("GitHub Pages deployment succeeded.")
                return True
        time.sleep(3)
    print("Pushed. GitHub has not exposed a Pages run yet; check the repository's Actions page.")
    return False


def publish(selected=None, *, watch=True, open_browser=False):
    with publishing_lock():
        if Path(git("rev-parse", "--show-toplevel", capture=True).stdout.strip()).resolve() != ROOT.resolve():
            raise BlogError("Run this script from its own Git repository.")
        branch = git("branch", "--show-current", capture=True).stdout.strip()
        if branch != "main":
            raise BlogError(f"Publishing is configured for main. Current branch is {branch or 'detached HEAD'!r}.")
        git("remote", "get-url", "origin", capture=True)
        for marker in ("MERGE_HEAD", "rebase-merge", "rebase-apply", "CHERRY_PICK_HEAD"):
            marker_path = git("rev-parse", "--git-path", marker, capture=True).stdout.strip()
            if (ROOT / marker_path).exists():
                raise BlogError("Finish or abort the current merge/rebase/cherry-pick before publishing.")
        if git("diff", "--cached", "--quiet", check=False).returncode:
            raise BlogError("The Git staging area is not empty. Commit or unstage your existing changes first.")
        tracked = git_paths("diff", "--name-only", "-z")
        excluded = [p for p in tracked if not allowed_path(p)]
        if excluded:
            raise BlogError("Tracked changes outside the publishing allowlist need manual handling:\n" + "\n".join(excluded))

        changed_article = None
        original = updated = None
        if selected:
            changed_article = article_path(selected)
            original = changed_article.read_text(encoding="utf-8")
            match = frontmatter(original)
            meta = match.group(1)
            if re.search(r"(?m)^draft:\s*true\s*(?:#.*)?$", meta):
                meta = re.sub(r"(?m)^draft:\s*true\s*(?:#.*)?$", "draft: false", meta, count=1)
                updated = original[:match.start(1)] + meta + original[match.end(1):]
                changed_article.write_text(updated, encoding="utf-8")
                print(f"Selected for publication: {changed_article.relative_to(ROOT)}")
            elif not re.search(r"(?m)^draft:\s*false\s*(?:#.*)?$", meta):
                raise BlogError("The selected article needs an explicit draft: true or draft: false field.")
        try:
            check()
        except BaseException:
            if updated is not None and changed_article.read_text(encoding="utf-8") == updated:
                changed_article.write_text(original, encoding="utf-8")
            raise

        candidates = sorted(set(git_paths("ls-files", "--modified", "--deleted", "--others", "--exclude-standard", "-z")))
        candidates = [p for p in candidates if allowed_path(p)]
        if candidates:
            print("Staging site files:\n" + "\n".join(f"  {p}" for p in candidates))
            git("add", "--", *candidates)
        if git("diff", "--cached", "--quiet", check=False).returncode:
            message = "Publish " + (changed_article.parent.name if selected else "site updates") + " · " + now().strftime("%Y-%m-%d %H:%M")
            git("commit", "-m", message)
        else:
            print("No new site changes to commit; checking for a pending push.")
        checked_sha = git("rev-parse", "HEAD", capture=True).stdout.strip()
        # No auto-stash and no force-push: unrelated work is never silently rewritten.
        upstream = git("ls-remote", "--heads", "origin", "main", capture=True)
        if upstream.stdout.strip():
            pull = git("-c", "rebase.autoStash=false", "pull", "--rebase", "origin", "main", check=False)
            if pull.returncode:
                rebase_path = git("rev-parse", "--git-path", "rebase-merge", capture=True).stdout.strip()
                apply_path = git("rev-parse", "--git-path", "rebase-apply", capture=True).stdout.strip()
                if (ROOT / rebase_path).exists() or (ROOT / apply_path).exists():
                    git("rebase", "--abort", check=False)
                raise BlogError("Pull/rebase failed and the rebase was aborted. Your local commit is retained. Resolve the remote difference before publishing again.")
        # A rebase may have brought in new templates/content: check only if it changed HEAD.
        if git("rev-parse", "HEAD", capture=True).stdout.strip() != checked_sha:
            check()
        git("push", "origin", "HEAD:main")
        sha = git("rev-parse", "HEAD", capture=True).stdout.strip()
        print(f"Pushed commit {sha[:12]}.")
        deployed = watch_deployment(sha) if watch else False
        url = site_url()
        if url:
            print(f"Site: {url}")
            if open_browser and deployed:
                run(["/usr/bin/open", url])
        return deployed


def osascript(source, *args):
    result = run(["/usr/bin/osascript", "-e", source, *args], capture=True, check=False)
    if result.returncode:
        if "(-128)" in result.stderr:
            raise KeyboardInterrupt
        raise BlogError(result.stderr.strip())
    return result.stdout.strip()


def choose(title, choices, prompt):
    return osascript('''on run argv
set options to items 3 thru -1 of argv
activate
set answer to choose from list options with title (item 1 of argv) with prompt (item 2 of argv) default items {item 1 of options} OK button name "Continue" cancel button name "Cancel"
if answer is false then error number -128
return item 1 of answer
end run''', title, prompt, *choices)


def ask(prompt, default=""):
    return osascript('''on run argv
activate
set answer to display dialog (item 1 of argv) default answer (item 2 of argv) with title "Junwen'Log · New Draft" buttons {"Cancel", "Continue"} default button "Continue"
return text returned of answer
end run''', prompt, default)


def dialog(message, title="Junwen'Log"):
    osascript('''on run argv
activate
display dialog (item 1 of argv) with title (item 2 of argv) buttons {"OK"} default button "OK"
end run''', message, title)


def gui(action):
    try:
        if action == "new":
            options = [f"{v} · {k}" for k, v in SECTIONS.items()]
            section = choose("Junwen'Log · New Draft", options, "Choose a section / 选择分区").split(" · ")[-1]
            title = ask("Article title / 文章标题（可用中文）")
            slug = ask("URL slug / 英文链接名（小写英文、数字、短横线）", suggest_slug(title))
            language = "zh-CN" if re.search(r"[\u3400-\u9fff]", title) else "en"
            path = new_draft(section, title, slug, language)
            print(path)
            open_editor(path)
        elif action == "preview":
            preview()
        elif action == "open":
            open_editor()
        elif action == "publish":
            drafts = sorted(p for section in SECTIONS for p in (CONTENT / section).glob("*/index.md") if is_draft(p))
            site_only = "Publish saved site changes · keep drafts off the website"
            choices = [site_only] + [str(p.relative_to(ROOT)) for p in drafts]
            selected = choose("Junwen'Log · Publish", choices,
                              "Choose a draft, or publish site changes only.\n选择一篇草稿，或只发布网站修改。\nDrafts stay off the website but sync to the public source repository.\n草稿仍会同步到公开源码仓库；私密笔记请留在其他库。")
            selected = None if selected == site_only else selected
            osascript('''display notification "Building and checking the site, then deploying with GitHub Pages…" with title "Junwen'Log"''')
            deployed = publish(selected, open_browser=True)
            dialog("Published successfully. GitHub Pages is live." if deployed else "Changes pushed to GitHub. Check Actions for deployment status.")
    except BlogError as error:
        dialog(str(error), "Junwen'Log · Needs attention")
        raise


def main():
    parser = argparse.ArgumentParser(description="Junwen'Log · write locally, publish with confidence")
    commands = parser.add_subparsers(dest="command", required=True)
    new = commands.add_parser("new", help="Create a page-bundle draft")
    new.add_argument("section", choices=SECTIONS,
                     help="tech: technical articles; notes: notes of any kind; daily: everyday life and travel")
    new.add_argument("title")
    new.add_argument("--slug", required=True)
    new.add_argument("--language", choices=["en", "zh-CN"], default="en")
    new.add_argument("--open", action="store_true")
    new.add_argument("--editor", choices=["obsidian", "mweb"], default="obsidian")
    preview_parser = commands.add_parser("preview", help="Start a persistent local preview, including drafts")
    preview_parser.add_argument("--no-open", action="store_true")
    commands.add_parser("stop-preview", help="Stop only this site's local preview")
    commands.add_parser("check", help="Build and validate the production website")
    publish_parser = commands.add_parser("publish", help="Commit, synchronize, push, and watch deployment")
    publish_parser.add_argument("path", nargs="?", help="Explicit draft bundle/index.md to publish; omitted means preserve all draft flags")
    publish_parser.add_argument("--no-watch", action="store_true")
    publish_parser.add_argument("--open", action="store_true")
    open_parser = commands.add_parser("open", help="Open the writing vault or an article")
    open_parser.add_argument("path", nargs="?")
    open_parser.add_argument("--editor", choices=["obsidian", "mweb"], default="obsidian")
    commands.add_parser("status", help="Show local preview and Git status")
    gui_parser = commands.add_parser("gui", help="Native macOS writing dialogs")
    gui_parser.add_argument("action", choices=["new", "preview", "publish", "open"])
    args = parser.parse_args()
    if args.command == "new":
        path = new_draft(args.section, args.title, args.slug, args.language)
        print(path)
        if args.open:
            open_editor(path, args.editor)
    elif args.command == "preview":
        preview(not args.no_open)
    elif args.command == "stop-preview":
        stop_preview()
    elif args.command == "check":
        check()
    elif args.command == "publish":
        publish(args.path, watch=not args.no_watch, open_browser=args.open)
    elif args.command == "open":
        open_editor(article_path(args.path) if args.path else None, args.editor)
    elif args.command == "status":
        print(f"Workspace: {ROOT}\nPreview: {PREVIEW_URL if preview_process() else 'stopped'}")
        git("status", "--short")
    elif args.command == "gui":
        gui(args.action)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Cancelled. Nothing else will be published.", file=sys.stderr)
        sys.exit(130)
    except (BlogError, OSError) as error:
        print(f"\nJunwen'Log: {error}", file=sys.stderr)
        sys.exit(1)
