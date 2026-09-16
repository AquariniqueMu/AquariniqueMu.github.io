#!/usr/bin/env python3
"""Regression tests run only against temporary directories and local Git remotes."""
import contextlib
import datetime
import io
from pathlib import Path
import socket
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import blog


class WritingToolsTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="junwen-writing-test-")
        self.base = Path(self.temp.name).resolve()
        self.root = self.base / "site"
        self.root.mkdir()
        self.stack = contextlib.ExitStack()
        self.stack.enter_context(patch.object(blog, "ROOT", self.root))
        self.stack.enter_context(patch.object(blog, "CONTENT", self.root / "content"))
        self.stack.enter_context(patch.object(blog, "STATE", self.root / ".local"))
        self.stack.enter_context(contextlib.redirect_stdout(io.StringIO()))

    def tearDown(self):
        self.stack.close()
        self.temp.cleanup()

    def git(self, *args, cwd=None):
        return subprocess.run([blog.binary("git"), *args], cwd=cwd or self.root,
                              capture_output=True, text=True, check=True).stdout.strip()

    def init_repo(self):
        self.git("init", "-b", "main")
        self.git("config", "user.name", "Writing Test")
        self.git("config", "user.email", "writing-test@example.invalid")
        (self.root / ".gitignore").write_text(".local/\ncontent/.obsidian/\n")
        self.git("add", ".gitignore")
        self.git("commit", "-m", "Initial test")
        remote = self.base / "remote.git"
        self.git("init", "--bare", "--initial-branch=main", str(remote))
        self.git("remote", "add", "origin", str(remote))
        self.git("push", "-u", "origin", "main")
        return remote

    def test_unicode_draft_and_date(self):
        path = blog.new_draft("notes", "读书：技术与生活", "technology-and-life", "zh-CN")
        text = path.read_text()
        self.assertIn('title: "读书：技术与生活"', text)
        self.assertIn("slug: technology-and-life", text)
        self.assertIn("draft: true", text)
        self.assertIn("contentLanguage: zh-CN", text)
        date = next(line[6:] for line in text.splitlines() if line.startswith("date: "))
        self.assertEqual(datetime.datetime.fromisoformat(date).utcoffset(), datetime.timedelta(hours=8))
        self.assertEqual(path.name, "index.md")

    def test_section_paths_support_new_navigation(self):
        for section in ("tech", "notes", "daily"):
            path = blog.new_draft(section, "Example", "example")
            self.assertEqual(path, self.root / "content" / section / "example/index.md")
            self.assertEqual(blog.article_path(str(path)), path)
        for old_section in ("posts", "travel"):
            with self.assertRaisesRegex(blog.BlogError, "tech, notes, or daily"):
                blog.new_draft(old_section, "Wrong section", "wrong-section")
        aggregate_article = self.root / "content/posts/example/index.md"
        aggregate_article.parent.mkdir(parents=True)
        aggregate_article.write_text("---\ndraft: true\n---\n")
        with self.assertRaisesRegex(blog.BlogError, "content/tech"):
            blog.article_path(str(aggregate_article))

    def test_gui_offers_current_writing_sections(self):
        with patch.object(blog, "choose", return_value="Daily · daily") as choose, \
             patch.object(blog, "ask", side_effect=["日常见闻", "a-daily-note"]), \
             patch.object(blog, "open_editor") as editor:
            blog.gui("new")
        self.assertEqual(choose.call_args.args[1], ["Tech · tech", "Notes · notes", "Daily · daily"])
        draft = self.root / "content/daily/a-daily-note/index.md"
        editor.assert_called_once_with(draft)
        self.assertIn("contentLanguage: zh-CN", draft.read_text())

    def test_preview_port_check_allows_recently_closed_connections(self):
        with socket.socket() as previous:
            previous.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            previous.bind(("127.0.0.1", 0))
            port = previous.getsockname()[1]
            previous.listen()
            with socket.create_connection(("127.0.0.1", port), timeout=2) as client:
                connection, _ = previous.accept()
                with connection:
                    connection.shutdown(socket.SHUT_WR)
                    self.assertEqual(client.recv(1), b"")
                # The server initiates the close so its local port enters TIME_WAIT.
        blog.check_preview_port_available(port)

    def test_preview_port_check_preserves_existing_listener(self):
        with socket.socket() as listener:
            listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            listener.bind(("127.0.0.1", 0))
            port = listener.getsockname()[1]
            listener.listen()
            with self.assertRaisesRegex(blog.BlogError, "no process was stopped"):
                blog.check_preview_port_available(port)
            with socket.create_connection(("127.0.0.1", port), timeout=2):
                connection, _ = listener.accept()
                connection.close()

    def test_invalid_slug_and_existing_draft_are_preserved(self):
        for slug in ("../escape", "中文", "Bad-Slug", "two--hyphens", "-leading", "a/b"):
            with self.assertRaises(blog.BlogError):
                blog.new_draft("tech", "Title", slug)
        path = blog.new_draft("tech", "First title", "existing")
        original = path.read_bytes()
        with self.assertRaises(blog.BlogError):
            blog.new_draft("tech", "Replacement", "existing")
        self.assertEqual(path.read_bytes(), original)

    def test_allowlist_excludes_private_editor_and_secret_files(self):
        for path in (".env", "content/.obsidian/app.json", "content/private/note.md", "static/key.pem",
                     "scripts/__pycache__/blog.pyc", "docs/credentials.json", "../README.md"):
            self.assertFalse(blog.allowed_path(path), path)
        for path in ("content/tech/a/index.md", "static/image.jpg", "scripts/blog.py",
                     ".github/workflows/hugo.yml", ".gitignore", "themes/blowfish"):
            self.assertTrue(blog.allowed_path(path), path)

    def test_failed_build_restores_only_selected_draft(self):
        self.init_repo()
        selected = blog.new_draft("tech", "Selected", "selected")
        other = blog.new_draft("notes", "Other", "other")
        original, other_original = selected.read_bytes(), other.read_bytes()
        with patch.object(blog, "check", side_effect=blog.BlogError("test build failure")):
            with self.assertRaisesRegex(blog.BlogError, "test build failure"):
                blog.publish(str(selected), watch=False)
        self.assertEqual(selected.read_bytes(), original)
        self.assertEqual(other.read_bytes(), other_original)
        self.assertEqual(self.git("diff", "--cached", "--name-only"), "")

    def test_publish_explicit_draft_to_local_remote(self):
        remote = self.init_repo()
        selected = blog.new_draft("tech", "Selected", "selected")
        other = blog.new_draft("notes", "Other", "other")
        secret = self.root / "content/.obsidian"
        secret.mkdir()
        (secret / "app.json").write_text('{"private":"local only"}')
        with patch.object(blog, "check") as checker, patch.object(blog, "site_url", return_value=""):
            blog.publish(str(selected), watch=False)
            self.assertEqual(checker.call_count, 1)
        self.assertFalse(blog.is_draft(selected))
        self.assertTrue(blog.is_draft(other))
        self.assertEqual(self.git("rev-parse", "HEAD"), self.git("rev-parse", "main", cwd=remote))
        tracked = self.git("ls-tree", "-r", "--name-only", "HEAD")
        self.assertNotIn(".obsidian", tracked)
        self.assertNotIn(".local", tracked)

    def test_rebase_conflict_is_aborted_without_pushing(self):
        remote = self.init_repo()
        article = blog.new_draft("tech", "Example", "example")
        self.git("add", "content")
        self.git("commit", "-m", "Add example")
        self.git("push")
        peer = self.base / "peer"
        self.git("clone", str(remote), str(peer))
        self.git("config", "user.name", "Peer", cwd=peer)
        self.git("config", "user.email", "peer@example.invalid", cwd=peer)
        peer_file = peer / "content/tech/example/index.md"
        peer_file.write_text(peer_file.read_text().replace("Start with the idea", "Remote replaces the idea"))
        self.git("add", "content", cwd=peer)
        self.git("commit", "-m", "Peer edit", cwd=peer)
        self.git("push", cwd=peer)
        remote_head = self.git("rev-parse", "main", cwd=remote)
        article.write_text(article.read_text().replace("Start with the idea", "Local replaces the idea"))
        with patch.object(blog, "check"), patch.object(blog, "site_url", return_value=""):
            with self.assertRaisesRegex(blog.BlogError, "rebase was aborted"):
                blog.publish(str(article), watch=False)
        self.assertEqual(remote_head, self.git("rev-parse", "main", cwd=remote))
        self.assertFalse((self.root / ".git/rebase-merge").exists())
        self.assertIn("Local replaces the idea", article.read_text())
        self.assertEqual(self.git("status", "--porcelain"), "")


if __name__ == "__main__":
    unittest.main(verbosity=2)
