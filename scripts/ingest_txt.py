#!/usr/bin/env python3
import os, re, shutil, datetime, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
INBOX = ROOT / "inbox"
PROCESSED = ROOT / "processed"
DEST_ROOT = ROOT / "src" / "content" / "posts"

TZ = datetime.timezone(datetime.timedelta(hours=8))  # Asia/Taipei

def slugify(s: str) -> str:
    s = s.strip().lower()
    # keep CJK, letters, numbers; replace spaces with '-'; remove others
    s = re.sub(r'\s+', '-', s)
    s = re.sub(r'[^\w\-\u4e00-\u9fff]+', '', s)
    s = re.sub(r'-{2,}', '-', s).strip('-')
    return s or "post"

def parse_meta_from_header(lines):
    meta = {}
    remaining = []
    for i, line in enumerate(lines[:8]):
        m1 = re.match(r'^\s*(?:Title|標題)\s*:\s*(.+)$', line, re.I)
        m2 = re.match(r'^\s*(?:Category|分類)\s*:\s*(.+)$', line, re.I)
        m3 = re.match(r'^\s*(?:Tags|標籤)\s*:\s*(.+)$', line, re.I)
        if m1:
            meta['title'] = m1.group(1).strip()
            continue
        if m2:
            meta['category'] = m2.group(1).strip()
            continue
        if m3:
            meta['tags'] = [t.strip() for t in m3.group(1).split(',') if t.strip()]
            continue
    # remove matched meta lines from content
    used = set()
    for key, pat in [('title', r'^\s*(?:Title|標題)\s*:\s*'),
                     ('category', r'^\s*(?:Category|分類)\s*:\s*'),
                     ('tags', r'^\s*(?:Tags|標籤)\s*:\s*')]:
        pass
    for line in lines:
        if re.match(r'^\s*(?:Title|標題)\s*:\s*', line, re.I): continue
        if re.match(r'^\s*(?:Category|分類)\s*:\s*', line, re.I): continue
        if re.match(r'^\s*(?:Tags|標籤)\s*:\s*', line, re.I): continue
        remaining.append(line)
    # first non-empty H1 as title if not provided
    if 'title' not in meta and remaining:
        m = re.match(r'^\s*#\s+(.+?)\s*$', remaining[0])
        if m:
            meta['title'] = m.group(1).strip()
            remaining = remaining[1:]
    return meta, remaining

def parse_from_filename(name):
    meta = {}
    m = re.search(r'(\d{4})[-_/\.]?(\d{2})[-_/\.]?(\d{2})', name)
    if m:
        y, mo, d = m.groups()
        try:
            dt = datetime.date(int(y), int(mo), int(d))
            meta['date'] = dt.isoformat()
        except Exception:
            pass
    m = re.search(r'__([^_]+?)__', name)
    if m:
        meta['category'] = m.group(1)
    else:
        parts = re.split(r'[-_]', name)
        if len(parts) >= 3:
            meta.setdefault('category', parts[1])
    base = re.sub(r'\.[^.]+$', '', name)
    base = re.sub(r'^\d{4}[-_/\.]?\d{2}[-_/\.]?\d{2}', '', base)
    base = re.sub(r'__[^_]+__', '', base)
    base = base.strip('-_ ')
    if base:
        meta['title'] = base
    return meta

def ensure_dirs():
    (ROOT / "inbox").mkdir(parents=True, exist_ok=True)
    (ROOT / "processed").mkdir(parents=True, exist_ok=True)
    (ROOT / "src" / "content" / "posts").mkdir(parents=True, exist_ok=True)

def convert_file(path: pathlib.Path):
    raw = path.read_text(encoding='utf-8', errors='ignore')
    lines = raw.splitlines()
    meta1, remaining = parse_meta_from_header(lines)
    meta2 = parse_from_filename(path.name)
    meta = {**meta2, **meta1}  # headers override filename
    if 'date' not in meta:
        meta['date'] = datetime.datetime.now(tz=TZ).date().isoformat()
    category = meta.get('category', 'uncategorized')
    title = meta.get('title') or path.stem
    tags = meta.get('tags', [])

    yyyy, mm, *_ = meta['date'].split('-')
    dest_dir = DEST_ROOT / category / yyyy / mm
    dest_dir.mkdir(parents=True, exist_ok=True)
    fname = f"{meta['date']}-{slugify(title)}.md"
    dest = dest_dir / fname

    fm_lines = ["---"]
    # escape double quotes in title
    safe_title = title.replace('"', '\\"')
    fm_lines.append(f'title: "{safe_title}"')
    fm_lines.append(f"date: {meta['date']}")
    fm_lines.append(f'category: "{category}"')
    if tags:
        fm_lines.append("tags: [" + ", ".join([f'"{t}"' for t in tags]) + "]")
    fm_lines.append("draft: false")
    fm_lines.append("---")
    fm = "\\n".join(fm_lines)

    content = "\\n".join(remaining).strip() + "\\n"
    dest.write_text(fm + "\\n" + content, encoding='utf-8')

    rel = path.relative_to(INBOX)
    processed_dest = PROCESSED / rel
    processed_dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(path), str(processed_dest))
    print(f"Converted {path} -> {dest}")

def main():
    ensure_dirs()
    count = 0
    for p in sorted(INBOX.rglob("*.txt")):
        convert_file(p)
        count += 1
    print(f"Done. {count} file(s) converted.")

if __name__ == "__main__":
    main()