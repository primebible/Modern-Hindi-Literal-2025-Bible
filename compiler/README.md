# Compiler — how the PDFs are made

Turns the YAML source text (the chapter files in each book folder at the repo
root) into the print-ready PDFs published alongside them. Devanagari is shaped
correctly via Typst's HarfBuzz engine + Noto Serif/Sans Devanagari.

## Quick start

```bash
python compiler/build.py --publish        # regenerate ALL distribution PDFs
                                          #   <Book>/          per-book, every edition
                                          #   Complete-Bible/  everything so far
```

That one command is all a maintainer needs after the source text changes.

Dev builds (whole text, output to gitignored `build/`, faster iteration):

```bash
python compiler/build.py                  # every edition
python compiler/build.py standard         # one edition (bare name or --standard)
python compiler/build.py premium --large  # large-print variant of one edition
```

## Editions

| Edition      | Page             | Layout           | Extras                                   | Use                     |
|--------------|------------------|------------------|------------------------------------------|-------------------------|
| **economy**  | A5               | 1 column, dense  | verse #s only                            | cheap giveaways/tracts  |
| **standard** | 15.6 × 23.4 cm   | 2 column         | running heads, TOC, book pages           | reading / pew Bible     |
| **premium**  | 6 × 9 in + gutter| 2 column         | red-letter, deep-red chapter numerals, TOC, binding margin | bound POD edition |
| **mobile**   | 9 × 16 cm        | 1 column         | phone-shaped page, no pinch-zoom needed  | reading on a phone      |

`--large` is a **modifier**, not an edition: it layers large-print typography
(16 pt, single column, ragged-right, generous leading) onto any edition while
keeping that edition's trim size, red-letter, and binding margins. Numeral
colours are kept per-edition so large variants stay visually distinct.

## How it fits together

```
<Book>/<n>.yaml   (repo root)       # source of truth (see docs/SCHEMA.md)
        │
        ▼  compiler/build.py        # validate + canonical order + emit
build/…/data.json  +  main-*.typ    # intermediates (gitignored)
        │
        ▼  typst compile            # HarfBuzz Devanagari shaping
<Book>/<Book>-<Edition>.pdf         # distribution PDFs (committed)
```

- **`books.py`** — full 66-book canonical order + Hindi names. Add a book by
  dropping a `<EnglishName>/` folder with chapter YAML in the repo root —
  no code change needed.
- **`bible.typ`** — the layout template. Edition differences are pure config.
- **`build.py`** — the `PROFILES` dict defines each edition; `LARGE_OVERLAY`
  defines the large-print modifier; `publish()` writes the distribution PDFs.
- **`fonts/`** — Noto Serif/Sans Devanagari (OFL licence), passed to Typst via
  `--font-path --ignore-system-fonts`, so rendering is identical on every machine.

## Text versioning

Every build stamps a **content-derived version** on the credits page, e.g.
`1.28.1069+356ce17b`:

- `1.28.1069` — books.chapters.verses currently in the text
- `+356ce17b` — first 8 chars of a SHA-256 over the compiled text

Change any verse and the hash changes; identical text always reproduces the
identical version. Below it, a bilingual **compile date** (१४ जुलाई २०२६ /
14 July 2026) lets anyone tell which printing is newer without understanding
hashes. Same version + different date = same text, later printing.

## Data quality & typography

- The build **validates sources** and warns on missing/duplicate chapters and
  verses, mismatched book/chapter fields, and malformed entries — it still
  builds, so in-progress translations aren't blocked (see [docs/SCHEMA.md](docs/SCHEMA.md)).
- Straight quotes in the YAML become **typographic quotes** (“ ” ‘ ’).
- Verse numbers are bound to the first word of their verse so they can never be
  orphaned at a line end; verse 1's number is omitted (the chapter numeral
  implies it), per standard Bible typography.
- Reserved per-verse fields already supported: `heading:` (section titles) and
  `redletter:` (words of Christ, red in premium) — see the schema doc.

## Requirements

- Python 3 + `pyyaml`
- [Typst](https://typst.app) 0.15+ (`winget install Typst.Typst`)
- The four Noto Devanagari TTFs in `fonts/` (the build checks and tells you if
  they're missing)

## POD notes

- Premium uses a 6×9 in trim with a wider **inside** margin (gutter) for
  binding — the interior size most POD services (KDP, Lulu) accept.
- Fonts are embedded; no bleed is used (fine for text-only interiors).
