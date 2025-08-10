#!/usr/bin/env python3
# Minimal uploader: place one or more TXT files into the repo's inbox/ and create a commit.
# Requirements: git is installed and the repository is already cloned.
# Usage: python tools/upload_txt.py /path/to/file1.txt [/path/to/file2.txt ...]

import os, sys, shutil, subprocess, pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
INBOX = ROOT / "inbox"

def run(cmd, cwd=None):
    print("+", " ".join(cmd))
    subprocess.check_call(cmd, cwd=cwd or ROOT)

def main():
    if len(sys.argv) < 2:
        print("Usage: python tools/upload_txt.py file1.txt [file2.txt ...]")
        sys.exit(1)
    INBOX.mkdir(parents=True, exist_ok=True)
    for fp in sys.argv[1:]:
        src = pathlib.Path(fp)
        if not src.exists() or src.suffix.lower() != ".txt":
            print(f"Skip non-existing or non-txt: {src}")
            continue
        dest = INBOX / src.name
        shutil.copyfile(src, dest)
        print(f"Copied {src} -> {dest}")
    # commit
    try:
        run(["git", "add", "inbox"])
        run(["git", "commit", "-m", "chore: add txt to inbox"])
        run(["git", "push"])
        print("Uploaded and pushed. GitHub Action will ingest automatically.")
    except subprocess.CalledProcessError as e:
        print("Git command failed:", e)
        sys.exit(e.returncode)

if __name__ == "__main__":
    main()