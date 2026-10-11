#!/usr/bin/env python3
"""Local equivalent of .github/workflows/release.yml (minus the GitHub release).

Reproduces the workflow logic:
  1. Create client.zip from the contents of modpack/
  2. Download required mods from CurseForge into modpack/mods/
  3. If modpack/overrides/config exists, move it to modpack/config
  4. Create server.zip containing config/ and mods/ (or just mods/)
"""

import json
import re
import sys
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MODPACK = ROOT / "modpack"
MANIFEST = MODPACK / "manifest.json"

CHUNK_SIZE = 64 * 1024


def parse_args(argv):
    import argparse

    parser = argparse.ArgumentParser(
        description="Build client.zip and server.zip from the modpack manifest."
    )
    parser.add_argument(
        "--no-client",
        action="store_true",
        help="skip creating client.zip",
    )
    parser.add_argument(
        "--client-only",
        action="store_true",
        help="only create client.zip (skip downloads and server.zip)",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=ROOT,
        help="directory to write the zips into (default: repository root)",
    )
    return parser.parse_args(argv)


def create_client_zip(out_dir: Path) -> None:
    """Equivalent of: (cd modpack && zip -r client.zip *)

    In CI this runs before mods are downloaded and before overrides/config is
    moved in, so exclude those to match the workflow's output regardless of
    any leftover files from a previous run.
    """
    exclude = {MODPACK / "mods", MODPACK / "config"}
    dest = out_dir / "client.zip"
    print(f"Creating {dest} ...")
    with zipfile.ZipFile(dest, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(MODPACK.rglob("*")):
            if not path.is_file():
                continue
            if any(parent in exclude for parent in path.parents):
                continue
            zf.write(path, path.relative_to(MODPACK))
    print(f"  wrote {dest}")


def content_disposition_filename(headers, url: str) -> str:
    """Mimic wget's --content-disposition: prefer Content-Disposition filename,
    falling back to the basename of the URL."""
    cd = headers.get("Content-Disposition", "")
    match = re.search(r"filename\*=(?:UTF-8'')?\"?([^\";]+)\"?", cd, re.IGNORECASE)
    if match:
        return match.group(1)
    match = re.search(r'filename="([^"]+)"', cd)
    if match:
        return match.group(1)
    match = re.search(r"filename=([^;]+)", cd)
    if match:
        return match.group(1).strip().strip('"')
    return url.rstrip("/").rsplit("/", 1)[-1]


def download_mods() -> None:
    """Equivalent of:
    print_curseforge_urls.py | wget -q -i - -P mods/ --content-disposition
    """
    manifest = json.loads(MANIFEST.read_text())
    files = [f for f in manifest["files"] if f["required"]]
    if not files:
        print("No required mods listed in manifest.json.")
        return

    mods_dir = MODPACK / "mods"
    mods_dir.mkdir(exist_ok=True)

    for entry in files:
        project_id = entry["projectID"]
        file_id = entry["fileID"]
        url = (
            "https://www.curseforge.com/api/v1/mods/"
            f"{project_id}/files/{file_id}/download"
        )
        try:
            with urllib.request.urlopen(url) as response:
                filename = content_disposition_filename(response.headers, response.url)
                dest = mods_dir / filename
                size = int(response.headers.get("Content-Length", 0))
                downloaded = 0
                with open(dest, "wb") as fh:
                    while True:
                        chunk = response.read(CHUNK_SIZE)
                        if not chunk:
                            break
                        fh.write(chunk)
                        downloaded += len(chunk)
                        if size:
                            pct = min(100, downloaded * 100 // size)
                            print(
                                f"\r  {filename}: {pct}% ({downloaded}/{size})", end=""
                            )
                print(f"\r  {filename}: done ({downloaded} bytes)      ")
        except Exception as exc:  # noqa: BLE001
            print(f"  FAILED to download {url}: {exc}", file=sys.stderr)
            raise SystemExit(1)


def move_overrides() -> bool:
    """Equivalent of: mv modpack/overrides/config modpack/config && rm -rf overrides

    Returns True if an overrides/config folder was found (so the server zip
    should include config).
    """
    overrides = MODPACK / "overrides"
    src = overrides / "config"
    if not src.is_dir():
        return False

    dest = MODPACK / "config"
    print("Moving overrides/config -> modpack/config")
    if dest.exists():
        print(
            f"  {dest} already exists; aborting to avoid clobbering it.",
            file=sys.stderr,
        )
        raise SystemExit(1)
    dest.parent.mkdir(parents=True, exist_ok=True)
    src.rename(dest)

    # The workflow's `rm -rf overrides` ran from the repo root by mistake;
    # we remove the actual modpack/overrides folder instead.
    if overrides.exists():
        for path in sorted(overrides.rglob("*"), reverse=True):
            if path.is_file() or path.is_symlink():
                path.unlink()
            elif path.is_dir():
                path.rmdir()
        overrides.rmdir()
    return True


def create_server_zip(out_dir: Path, has_config: bool) -> None:
    """Equivalent of: (cd modpack && zip -r ../server.zip config mods)
    (or just `mods` when there is no config folder)"""
    dest = out_dir / "server.zip"
    dirs = ["config", "mods"] if has_config else ["mods"]
    print(f"Creating {dest} (contents: {', '.join(dirs)}) ...")
    with zipfile.ZipFile(dest, "w", zipfile.ZIP_DEFLATED) as zf:
        for d in dirs:
            folder = MODPACK / d
            if not folder.is_dir():
                print(
                    f"  warning: modpack/{d} does not exist; skipping", file=sys.stderr
                )
                continue
            for path in sorted(folder.rglob("*")):
                if path.is_file():
                    zf.write(path, path.relative_to(MODPACK))
    print(f"  wrote {dest}")


def main(argv=None) -> None:
    args = parse_args(argv if argv is not None else sys.argv[1:])
    if not MANIFEST.is_file():
        print(f"error: {MANIFEST} not found", file=sys.stderr)
        raise SystemExit(1)

    out_dir = args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    if not args.no_client:
        create_client_zip(out_dir)

    if args.client_only:
        print("\nDone.")
        return

    download_mods()
    has_config = move_overrides()
    create_server_zip(out_dir, has_config)

    print("\nDone.")


if __name__ == "__main__":
    main()
