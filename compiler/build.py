#!/usr/bin/env python3
"""Compile the YAML source Bible into print-ready (and phone-ready) PDFs.

    python compiler/build.py --publish         # regenerate the distribution PDFs:
                                               #   <Book>/           per-book, every edition
                                               #   Complete-Bible/   everything so far, every edition
    python compiler/build.py                   # dev build: whole text, every edition -> build/
    python compiler/build.py standard          # dev build: one edition (bare name or --standard)
    python compiler/build.py premium --large   # dev build: large-print variant of one edition

Editions: economy, standard, premium, mobile.  `--large` is a modifier.
`--publish` builds all editions and both variants of everything.

Pipeline:  YAML  ->  validate + canonical-order  ->  data.json + main.typ  ->  Typst -> PDF
"""
import datetime
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import yaml

from books import ORDER, HINDI

# Windows consoles/pipes often default to cp1252, which can't print ✓ or
# Devanagari — reconfigure so progress output never crashes the build.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass

HERE = Path(__file__).resolve().parent      # compiler/
ROOT = HERE.parent                          # repo root
SRC = ROOT                                  # book folders (YAML + PDFs) live in the root
FONTS = HERE / "fonts"
BUILD = ROOT / "build"                      # intermediates + dev builds (gitignored)

REQUIRED_FONTS = [
    "NotoSerifDevanagari-Regular.ttf",
    "NotoSerifDevanagari-Bold.ttf",
    "NotoSansDevanagari-Regular.ttf",
    "NotoSansDevanagari-Bold.ttf",
]

# --- Credits page. CC BY 4.0: free to copy/print/distribute, credit required. ---
ATTRIBUTION = [
    "आधुनिक हिन्दी बाइबिल — Modern Hindi Literal Translation",
    "",
    "यह बाइबिल सबके लिए मुफ़्त है। इसे छापें, कॉपी करें और स्वतंत्र",
    "रूप से बाँटें — किसी अनुमति की आवश्यकता नहीं है।",
    "This Bible is free for everyone. Print it, copy it, and",
    "distribute it freely — no permission needed.",
    "",
    "खुला स्रोत / Open source — Creative Commons Attribution 4.0.",
    "कृपया यह श्रेय बनाए रखें / Please keep this credit:",
    "PrimeBible — https://primebible.com",
    "स्रोत / Source: github.com/primebible/Modern-Hindi-Literal-2025-Bible",
]

# --- Editions.  Values are raw Typst expressions (strings are pre-quoted). ---
PROFILES = {
    "economy": {
        "edition": '"किफ़ायती संस्करण  ·  Economy Edition"',
        "page": '(paper: "a5", margin: (x: 1.1cm, y: 1.2cm))',
        "columns": "1",
        "col_gutter": "1em",
        "body_font": '"Noto Serif Devanagari"',
        "head_font": '"Noto Sans Devanagari"',
        "font_size": "8.5pt",
        "leading": "0.5em",
        "par_spacing": "0.5em",
        "justify": "true",
        "header": "false",
        "toc": "false",
        "dev_numerals": "true",
        "chapnum_size": "1.5em",
        "chapnum_color": "luma(30)",
        "versenum_color": "luma(55)",
        "book_break": "false",
        "chapter_break": "false",
        "book_space_before": "0.8em",
        "book_space_after": "0.5em",
        "book_title_size": "15pt",
    },
    "standard": {
        "edition": '"मानक संस्करण  ·  Standard Edition"',
        "page": "(width: 15.6cm, height: 23.4cm, margin: (x: 1.5cm, y: 1.7cm))",
        "columns": "2",
        "col_gutter": "1.2em",
        "body_font": '"Noto Serif Devanagari"',
        "head_font": '"Noto Sans Devanagari"',
        "font_size": "9.5pt",
        "leading": "0.62em",
        "par_spacing": "0.62em",
        "justify": "true",
        "header": "true",
        "toc": "true",
        "dev_numerals": "true",
        "chapnum_size": "1.9em",
        "chapnum_color": "luma(20)",
        "versenum_color": "luma(55)",
        "book_break": "true",
        "chapter_break": "false",
        "book_space_before": "0.5em",
        "book_space_after": "0.8em",
        "book_title_size": "20pt",
    },
    "premium": {
        "edition": '"प्रीमियम संस्करण  ·  Premium Edition"',
        # 6x9in POD trim with a wider inside (gutter) margin for binding.
        "page": "(width: 6in, height: 9in, margin: (inside: 2cm, outside: 1.4cm, top: 1.7cm, bottom: 1.7cm))",
        "columns": "2",
        "col_gutter": "1.3em",
        "body_font": '"Noto Serif Devanagari"',
        "head_font": '"Noto Sans Devanagari"',
        "font_size": "10pt",
        "leading": "0.72em",
        "par_spacing": "0.72em",
        "justify": "true",
        "header": "true",
        "toc": "true",
        "dev_numerals": "true",
        "chapnum_size": "2.4em",
        "chapnum_color": 'rgb("#7a1f1f")',
        "versenum_color": 'rgb("#7a1f1f")',
        "book_break": "true",
        "chapter_break": "false",
        "book_space_before": "0.6em",
        "book_space_after": "1em",
        "book_title_size": "24pt",
    },
    # On-screen edition for phones. Page is sized to a ~9:16 phone aspect ratio so a
    # PDF viewer fits it edge-to-edge with no pinch-zoom; single column, tight margins,
    # ragged-right (narrow measure), no running header (clutter on a small screen).
    # Book headings still emit PDF bookmarks, so readers get a tappable nav panel.
    "mobile": {
        "edition": '"मोबाइल संस्करण  ·  Mobile Edition"',
        "page": '(width: 9cm, height: 16cm, margin: (x: 0.75cm, y: 0.7cm))',
        "columns": "1",
        "col_gutter": "1em",
        "body_font": '"Noto Serif Devanagari"',
        "head_font": '"Noto Sans Devanagari"',
        "font_size": "11pt",
        "leading": "0.72em",
        "par_spacing": "0.6em",
        "justify": "false",
        "header": "false",
        "toc": "true",
        "dev_numerals": "true",
        "chapnum_size": "1.7em",
        "chapnum_color": "luma(20)",
        "versenum_color": "luma(55)",
        "book_break": "true",
        "chapter_break": "false",
        "book_space_before": "0.4em",
        "book_space_after": "0.7em",
        "book_title_size": "22pt",
    },
}

# Large-print accessibility overlay — applied on top of ANY edition with --large.
# Each edition keeps its own trim size, red-letter, TOC/header, binding margin, etc.;
# only the typography changes to large-print conventions: 16pt body, single column,
# ragged-right (justified spacing hurts low-vision tracking), generous leading.
# NOTE: numeral colours are intentionally NOT overridden — each edition keeps its
# own (premium's deep red, standard's dark grey) so the large variants stay visually
# distinct and retain edition identity. All base colours are dark enough for print.
LARGE_OVERLAY = {
    "columns": "1",
    "font_size": "16pt",
    "leading": "0.85em",
    "par_spacing": "0.95em",
    "justify": "false",
    "book_title_size": "30pt",
}

_warnings = 0


def warn(msg):
    global _warnings
    _warnings += 1
    print(f"  ! {msg}")


# Characters after which a quote mark is an OPENING quote (start-of-text included).
_OPENERS = set(" \t([{‘“-–—")


def beautify(text):
    """Normalize whitespace and convert straight quotes to typographic quotes.

    Position-based (opening iff preceded by start/space/bracket/another opener),
    so quotes that span verses still pair correctly — no cross-verse state needed.
    """
    text = " ".join(text.split())
    out = []
    prev = ""
    for c in text:
        if c == '"':
            c = "“" if (prev == "" or prev in _OPENERS) else "”"
        elif c == "'":
            c = "‘" if (prev == "" or prev in _OPENERS) else "’"
        out.append(c)
        prev = c
    return "".join(out)


def load_chapter(path, file_num, folder_name):
    """Parse and validate one chapter file. Returns a chapter dict or None."""
    try:
        doc = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as e:
        mark = getattr(e, "problem_mark", None)
        where = f" (line {mark.line + 1})" if mark else ""
        # Hard failure, not a warning: skipping an unparseable chapter would
        # silently publish scripture with a chapter missing.
        sys.exit(
            f"ERROR: {path} is not valid YAML{where}: {getattr(e, 'problem', e)}\n"
            "Fix the file (or restore it) and rebuild — refusing to publish "
            "with an unreadable chapter."
        )
    # Accept both shapes volunteers produce: a 1-element list (current repo
    # convention) or a plain top-level map (the upstream README's example).
    if isinstance(doc, list) and len(doc) == 1:
        obj = doc[0]
    elif isinstance(doc, dict):
        obj = doc
    else:
        warn(f"{path}: expected a mapping or 1-element list at top level — skipped")
        return None

    try:
        chap_num = int(obj.get("chapter"))
    except (TypeError, ValueError):
        warn(f"{path}: bad or missing 'chapter' field — using filename ({file_num})")
        chap_num = file_num
    if chap_num != file_num:
        warn(f"{path}: chapter field says {chap_num} but filename says {file_num} — using filename")
        chap_num = file_num

    book_hi = HINDI[folder_name]
    if obj.get("book") and obj["book"] != book_hi:
        warn(f"{path}: book name '{obj['book']}' ≠ expected '{book_hi}' for {folder_name}")

    verses = []
    seen = set()
    for v in obj.get("verses") or []:
        try:
            vnum = int(v["verse"])
            vtext = beautify(str(v["text"]))
        except (KeyError, TypeError, ValueError):
            warn(f"{path}: malformed verse entry {v!r} — skipped")
            continue
        if not vtext:
            warn(f"{path}: verse {vnum} has empty text — skipped")
            continue
        if vnum in seen:
            warn(f"{path}: duplicate verse {vnum} — keeping first")
            continue
        seen.add(vnum)
        out = {"verse": vnum, "text": vtext}
        # optional reserved fields pass through when present
        if v.get("heading"):
            out["heading"] = beautify(str(v["heading"]))
        if v.get("redletter"):
            out["redletter"] = True
        verses.append(out)

    if not verses:
        warn(f"{path}: no verses — skipped")
        return None
    verses.sort(key=lambda v: v["verse"])
    missing = sorted(set(range(1, verses[-1]["verse"] + 1)) - seen)
    if missing:
        warn(f"{path}: missing verse(s) {missing}")
    return {"chapter": chap_num, "verses": verses}


def load_books():
    """Read every book folder present on disk, ordered by canon; validate as we go."""
    books = []
    folders = [p for p in SRC.iterdir()
               if p.is_dir() and not p.name.startswith(".")]
    # Warn only about non-canon folders that actually contain chapter YAML —
    # likely a misspelled book name; infra dirs (compiler/, build/, …) are ignored.
    for p in folders:
        if p.name not in ORDER and any(p.glob("*.yaml")):
            warn(f"folder '{p.name}' contains YAML but is not a canonical book name — skipped")
    folders = sorted((p for p in folders if p.name in ORDER), key=lambda p: ORDER[p.name])

    for folder in folders:
        numbered = []
        for f in sorted(folder.glob("*.yaml")) + sorted(folder.glob("*.yml")):
            try:
                numbered.append((int(f.stem), f))
            except ValueError:
                warn(f"skipping {f} (filename is not a chapter number)")
        numbered.sort()

        chapters = []
        for n, f in numbered:
            ch = load_chapter(f, n, folder.name)
            if ch:
                chapters.append(ch)
        if not chapters:
            warn(f"{folder}: no usable chapters — book skipped")
            continue

        nums = [c["chapter"] for c in chapters]
        missing = sorted(set(range(1, max(nums) + 1)) - set(nums))
        if missing:
            warn(f"{folder.name}: missing chapter(s) {missing} — book will print without them")

        books.append({
            "name_en": folder.name,
            "name_hi": HINDI[folder.name],
            "chapters": chapters,
        })
        nverses = sum(len(c["verses"]) for c in chapters)
        print(f"  + {folder.name:<16} {len(chapters):>3} chapters, {nverses:>5} verses")

    if not books:
        sys.exit(f"no source books found under {SRC}")
    return books


def content_version(books):
    """Deterministic version derived from the compiled text itself.

    Format: <books>.<chapters>.<verses>+<sha8> (e.g. 1.28.1069+3f2a9c1b).
    The counts show translation progress at a glance; the hash pins the exact
    text — any verse change anywhere yields a new version, identical text always
    reproduces the same one. No manual bumping, no timestamps (reproducible).
    """
    canonical = json.dumps(books, ensure_ascii=False, sort_keys=True).encode("utf-8")
    sha8 = hashlib.sha256(canonical).hexdigest()[:8]
    nch = sum(len(b["chapters"]) for b in books)
    nvs = sum(len(c["verses"]) for b in books for c in b["chapters"])
    return f"{len(books)}.{nch}.{nvs}+{sha8}"


HINDI_MONTHS = ["जनवरी", "फ़रवरी", "मार्च", "अप्रैल", "मई", "जून",
                "जुलाई", "अगस्त", "सितंबर", "अक्टूबर", "नवंबर", "दिसंबर"]
DEV_DIGITS = str.maketrans("0123456789", "०१२३४५६७८९")


def compile_date():
    """Bilingual build date so anyone can tell which printing is newer."""
    d = datetime.date.today()
    hindi = f"{d.day} {HINDI_MONTHS[d.month - 1]} {d.year}".translate(DEV_DIGITS)
    return f"{hindi} / {d.strftime('%#d %B %Y') if sys.platform == 'win32' else d.strftime('%-d %B %Y')}"


def date_fields():
    """Day-granular date for the PDF's document metadata (PDF/A requires one)."""
    d = datetime.date.today()
    return {"y": d.year, "m": d.month, "d": d.day}


def write_data(books):
    """Content is edition-independent — write it once, shared by every edition."""
    version = content_version(books)
    compiled = compile_date()
    print(f"  text version: {version}   compiled: {compiled}")
    data = {
        "title": "पवित्र बाइबिल",
        "subtitle": "आधुनिक हिन्दी अनुवाद",
        "version": version,
        "compiled": compiled,
        "date": date_fields(),
        "attribution": ATTRIBUTION,
        "books": books,
    }
    BUILD.mkdir(parents=True, exist_ok=True)
    (BUILD / "data.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8"
    )


def build(profile, large=False, *, data_ref="/build/data.json",
          workdir=None, pdf=None, overrides=None):
    cfg = dict(PROFILES[profile])
    name = profile
    edition_text = cfg["edition"].strip('"')
    if large:
        cfg.update(LARGE_OVERLAY)          # accessibility typography over the base edition
        name = f"{profile}-large"
        edition_text += "  ·  बड़े अक्षर (Large Print)"
    if overrides:
        cfg.update(overrides)
    # json.dumps produces a valid Typst string literal (ensure_ascii keeps it clean)
    cfg["edition"] = json.dumps(edition_text, ensure_ascii=False)

    workdir = workdir or (BUILD / name)
    workdir.mkdir(parents=True, exist_ok=True)
    pdf = pdf or (workdir / f"hindi-bible-{name}.pdf")

    cfg_typst = "(\n" + "".join(f"  {k}: {v},\n" for k, v in cfg.items()) + ")"
    main_file = workdir / f"main-{name}.typ"
    main_file.write_text(
        '#import "/compiler/bible.typ": render\n'
        f'#render(json("{data_ref}"), {cfg_typst})\n',
        encoding="utf-8",
    )

    try:
        subprocess.run(
            ["typst", "compile", "--root", str(ROOT),
             "--font-path", str(FONTS), "--ignore-system-fonts",
             "--pdf-standard", "a-1b",
             str(main_file), str(pdf)],
            check=True,
        )
    except FileNotFoundError:
        sys.exit("typst not found on PATH — install it with:  winget install Typst.Typst")
    except subprocess.CalledProcessError:
        sys.exit(f"typst compile failed for '{name}' (see error above)")
    print(f"  ✓ {pdf.relative_to(ROOT)}  ({pdf.stat().st_size // 1024} KB)")


EDITION_LABEL = {"economy": "Economy", "standard": "Standard",
                 "premium": "Premium", "mobile": "Mobile"}


def publish(books):
    """Regenerate the distribution PDFs the repo serves to end users:
    one folder per book (every edition + large variants), plus Complete-Bible/."""
    for book in books:
        en = book["name_en"]
        print(f"\nPublishing {en}:")
        bdir = BUILD / "books" / en
        bdir.mkdir(parents=True, exist_ok=True)
        data = {
            "title": book["name_hi"],
            "subtitle": "आधुनिक हिन्दी अनुवाद",
            "version": content_version([book]),
            "compiled": compile_date(),
            "date": date_fields(),
            "attribution": ATTRIBUTION,
            "books": [book],
        }
        (bdir / "data.json").write_text(
            json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8"
        )
        outfolder = ROOT / en
        outfolder.mkdir(exist_ok=True)
        for profile in PROFILES:
            for large in (False, True):
                suffix = "-LargePrint" if large else ""
                build(profile, large=large,
                      data_ref=f"/build/books/{en}/data.json",
                      workdir=bdir,
                      pdf=outfolder / f"{en}-{EDITION_LABEL[profile]}{suffix}.pdf",
                      # a single book doesn't need a contents page
                      overrides={"toc": "false"})

    print("\nPublishing Complete-Bible (everything translated so far):")
    cdir = ROOT / "Complete-Bible"
    cdir.mkdir(exist_ok=True)
    for profile in PROFILES:
        for large in (False, True):
            suffix = "-LargePrint" if large else ""
            build(profile, large=large,
                  pdf=cdir / f"Hindi-Bible-{EDITION_LABEL[profile]}{suffix}.pdf")

    update_readme(books)


def update_readme(books):
    """Regenerate the books table in the root README between the BOOKS markers,
    so newly published books appear on the landing page automatically."""
    readme = ROOT / "README.md"
    start = "<!-- BOOKS:START — auto-generated by compiler/build.py --publish; do not edit by hand -->"
    end = "<!-- BOOKS:END -->"
    text = readme.read_text(encoding="utf-8")
    if start not in text or end not in text:
        warn("README.md books markers not found — table not updated")
        return
    rows = ["| पुस्तक | Book | पढ़ें / Read | सभी PDF / All PDFs |", "|---|---|---|---|"]
    for b in books:
        en = b["name_en"]
        link = en.replace(" ", "%20")
        rows.append(f"| {b['name_hi']} | {en} "
                    f"| [📖 PDF]({link}/{link}-Standard.pdf) | [📂 खोलें / open]({link}/) |")
    rows.append("| पूरी बाइबिल (अब तक की) | Complete Bible (all so far) "
                "| [📖 PDF](Complete-Bible/Hindi-Bible-Standard.pdf) "
                "| [📂 खोलें / open](Complete-Bible/) |")
    block = start + "\n" + "\n".join(rows) + "\n" + end
    text = text[:text.index(start)] + block + text[text.index(end) + len(end):]
    readme.write_text(text, encoding="utf-8")
    print("  ✓ README.md books table updated")


def main():
    # `--large` is a modifier that builds the large-print variant of each selected
    # edition. Editions are named bare or as --flags (economy/standard/premium/mobile).
    large = False
    do_publish = False
    targets = []
    for a in sys.argv[1:]:
        name = a[2:] if a.startswith("--") else a
        if name == "large":
            large = True
        elif name == "publish":
            do_publish = True
        else:
            targets.append(name)

    targets = list(dict.fromkeys(targets)) or list(PROFILES)   # dedupe; default: all
    for t in targets:
        if t not in PROFILES:
            sys.exit(f"unknown edition '{t}' (choose from {list(PROFILES)}, optionally with --large)")

    missing_fonts = [f for f in REQUIRED_FONTS if not (FONTS / f).exists()]
    if missing_fonts:
        sys.exit(
            f"missing font files in {FONTS}: {missing_fonts}\n"
            "download the Noto Devanagari TTFs there (see README)"
        )

    print("Loading source YAML:")
    books = load_books()
    write_data(books)
    if do_publish:
        publish(books)
    else:
        for t in targets:
            print(f"\nEdition: {t}{' (large print)' if large else ''}")
            build(t, large=large)
    if _warnings:
        print(f"\n⚠ {_warnings} warning(s) above — output built, but check the source data.")


if __name__ == "__main__":
    main()
