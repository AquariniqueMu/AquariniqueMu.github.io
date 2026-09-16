#!/usr/bin/env python3
"""Install four native macOS launchers without changing editor-global settings."""
import argparse
from pathlib import Path
import plistlib
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]
LAUNCHERS = {
    "New Draft": "new",
    "Preview": "preview",
    "Publish": "publish",
    "Open Writing Vault": "open",
}


def apple_string(value):
    return '"' + str(value).replace('\\', '\\\\').replace('"', '\\"') + '"'


def main():
    parser = argparse.ArgumentParser(description="Install Junwen'Log macOS writing launchers")
    parser.add_argument("--destination", type=Path, default=Path.home() / "Applications/Junwen Log")
    parser.add_argument("--no-desktop", action="store_true")
    args = parser.parse_args()
    destination = args.destination.expanduser().resolve()
    destination.mkdir(parents=True, exist_ok=True)
    (ROOT / ".local").mkdir(exist_ok=True)
    vault_settings = ROOT / "content/.obsidian"
    vault_settings.mkdir(parents=True, exist_ok=True)
    for config in (Path(__file__).parent / "obsidian-defaults").glob("*.json"):
        if not (vault_settings / config.name).exists():
            shutil.copyfile(config, vault_settings / config.name)
    template = (Path(__file__).parent / "launcher.applescript").read_text()
    for name, action in LAUNCHERS.items():
        target = destination / (name + ".app")
        identifier = "local.junwenlog." + action
        if target.exists():
            plist_path = target / "Contents/Info.plist"
            current = plistlib.loads(plist_path.read_bytes()) if plist_path.is_file() else {}
            if current.get("CFBundleIdentifier") != identifier:
                raise SystemExit(f"Refusing to overwrite an unrelated application: {target}")
            shutil.rmtree(target)
        source = template.replace("@BLOG@", apple_string(ROOT / "scripts/blog"))
        source = source.replace("@ACTION@", apple_string(action))
        source = source.replace("@LOG@", apple_string(ROOT / ".local" / f"launcher-{action}.log"))
        with tempfile.TemporaryDirectory(prefix="junwen-launcher-") as temp:
            script = Path(temp) / "main.applescript"
            script.write_text(source)
            subprocess.run(["/usr/bin/osacompile", "-o", str(target), str(script)], check=True)
        plist_path = target / "Contents/Info.plist"
        data = plistlib.loads(plist_path.read_bytes())
        data["CFBundleIdentifier"] = identifier
        data["CFBundleName"] = "Junwen Log · " + name
        data["CFBundleDisplayName"] = "Junwen Log · " + name
        data["NSHumanReadableCopyright"] = "Junwen'Log personal writing tools"
        plist_path.write_bytes(plistlib.dumps(data))
        # Re-sign after the metadata update, with an ad-hoc local signature.
        subprocess.run(["/usr/bin/codesign", "--force", "--sign", "-", str(target)], check=True, capture_output=True)
        print(target)
    guide = destination / "Start Here.txt"
    guide.write_text("Junwen'Log\n\n1. New Draft — choose a section, title and English URL slug.\n"
                     "2. Write and save in Obsidian (or MWeb).\n"
                     "3. Preview — inspect the site locally, including drafts.\n"
                     "4. Publish — select one draft, or publish saved site changes.\n\n"
                     "Drafts stay off the website but sync to the public source repository.\n"
                     "Keep private notes in another vault outside this repository.\n\n"
                     f"Writing guide: {ROOT / 'docs/WRITING.md'}\n"
                     f"Obsidian vault: {ROOT / 'content'}\n"
                     "On first use, open the content folder as a vault in Obsidian.\n"
                     "No community plugins or paid publishing service are needed.\n", encoding="utf-8")
    shortcut = Path.home() / "Desktop/Junwen Log"
    if not args.no_desktop and shortcut.parent.is_dir():
        if not shortcut.exists() and not shortcut.is_symlink():
            shortcut.symlink_to(destination, target_is_directory=True)
            print(f"Desktop shortcut: {shortcut}")
        else:
            print(f"Existing desktop item kept: {shortcut}")
    print("Ready. Drag individual apps to the Dock if desired.")


if __name__ == "__main__":
    main()
