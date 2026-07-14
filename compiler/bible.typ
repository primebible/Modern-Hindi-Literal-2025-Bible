// Reusable Bible layout template.
//   render(data, cfg)  — data = compiled JSON, cfg = per-profile settings.
// Devanagari shaping is handled automatically by Typst's HarfBuzz-based engine;
// the only requirement is a Devanagari-capable font (Noto Serif/Sans Devanagari).

#let devdigits = ("०", "१", "२", "३", "४", "५", "६", "७", "८", "९")

// Format an integer, optionally as Devanagari numerals (१२३ vs 123).
#let num(n, dev) = {
  if dev {
    str(n).clusters().map(c => devdigits.at(int(c))).join()
  } else {
    str(n)
  }
}

// Balanced columns: Typst fills column 1 fully before column 2, so a short
// chapter on its own page would use only the left half. We measure the content
// at column width and cap the block height near total/n, forcing an even split.
// Chapters taller than a page fall back to normal full-page column flow.
#let balanced_cols(n, gutter, slack, body) = {
  if n <= 1 { return body }
  layout(size => {
    let colw = (size.width - (n - 1) * gutter) / n
    let h = measure(block(width: colw, body)).height
    let target = calc.min(h / n + slack, size.height)
    block(height: target, columns(n, gutter: gutter, body))
  })
}

#let render(data, cfg) = {
  // date: none keeps PDFs byte-identical across same-text rebuilds (no embedded
  // timestamp) — required so CI can detect "nothing changed" and skip commits.
  set document(title: data.title, author: "PrimeBible", date: none)
  set text(font: cfg.body_font, size: cfg.font_size, lang: "hi")
  set par(justify: cfg.justify, leading: cfg.leading, spacing: cfg.par_spacing)

  // Running head resolves to the last chapter marker that begins on or before
  // the current page — robust against state-update ordering (no off-by-one).
  let header = if cfg.header {
    context {
      let pg = here().page()
      let cur = none
      for m in query(<chapmark>) {
        if m.location().page() <= pg { cur = m.value }
      }
      if cur == none { return }
      set text(font: cfg.head_font, size: 8pt, fill: luma(90))
      pad(bottom: 3pt, grid(
        columns: (1fr, 1fr),
        align(left)[#cur.book],
        align(right)[#cur.book #num(cur.chap, cfg.dev_numerals)],
      ))
    }
  } else { none }

  set page(
    ..cfg.page,
    numbering: (..n) => num(n.pos().first(), cfg.dev_numerals),
    header: header,
  )

  // ---- Front matter (header auto-hides while book state is empty) ----
  align(center + horizon)[
    #text(font: cfg.head_font, size: 26pt, weight: "bold")[#data.title]
    #v(0.6em)
    #text(font: cfg.head_font, size: 13pt, fill: luma(80))[#data.subtitle]
    #v(3em)
    #text(size: 11pt)[#cfg.edition]
  ]
  pagebreak()

  // Credits page — free-distribution notice + required CC BY credit.
  v(1fr)
  {
    set par(justify: false)
    set text(size: 9pt)
    for line in data.attribution [#line \ ]
    v(0.8em)
    // Content-derived version: identifies the exact text of this printing.
    // Compile date: lets anyone tell at a glance which printing is newer.
    text(font: cfg.head_font, size: 8pt, fill: luma(70))[
      पाठ संस्करण / Text version: #raw(data.version) \
      संकलन तिथि / Compiled: #data.compiled
    ]
  }
  pagebreak()

  // Table of contents
  if cfg.toc {
    show outline.entry: it => { set text(font: cfg.head_font, size: 11pt); it }
    outline(title: text(font: cfg.head_font)[विषय-सूची], depth: 1)
    pagebreak()
  }

  // ---- Book title styling ----
  show heading.where(level: 1): it => {
    set text(font: cfg.head_font, weight: "bold")
    if cfg.book_break { pagebreak(weak: true) }
    v(cfg.book_space_before)
    align(center, text(size: cfg.book_title_size)[#it.body])
    v(0.3em)
    align(center, line(length: 40%, stroke: 0.6pt + luma(120)))
    v(cfg.book_space_after)
  }

  // ---- Section (pericope) heading styling, when present in the data ----
  show heading.where(level: 2): it => {
    set text(font: cfg.head_font, weight: "bold", size: 1em)
    v(0.5em); it.body; v(0.25em)
  }

  // Render one chapter's verses (used inside a columns region).
  let chapter_body = (book_hi, ch) => {
    // zero-size marker that feeds the running head
    [#metadata((book: book_hi, chap: ch.chapter))<chapmark>]
    let first = true
    for v in ch.verses {
      // Optional section heading (reserved schema field)
      let sec = v.at("heading", default: none)
      if sec != none { heading(level: 2, sec) }

      let opens_chapter = first
      if first {
        // Large chapter number opening the chapter
        text(
          size: cfg.chapnum_size,
          weight: "bold",
          fill: cfg.chapnum_color,
          font: cfg.head_font,
        )[#num(ch.chapter, cfg.dev_numerals)]
        h(0.35em)
        first = false
      }

      // Red-letter (words of Christ) when flagged — reserved schema field.
      let vtext = s => if v.at("redletter", default: false) {
        text(fill: rgb("#b00000"), s)
      } else {
        s
      }

      if opens_chapter and v.verse == 1 {
        // Verse 1's number is implied by the chapter numeral (Bible convention).
        vtext(v.text)
      } else {
        // Raised verse number — sans reads more clearly at small size than the
        // serif; built manually (not super()) to avoid double-shrinking. The
        // number is boxed together with the verse's FIRST WORD: h() spacing is
        // a legal line-break point, so a bare number could be orphaned at a
        // line end with its verse starting on the next line.
        let words = v.text.split(" ")
        let numbox = box(baseline: -0.26em, text(
          size: 0.74em,
          weight: "bold",
          font: cfg.head_font,
          fill: cfg.versenum_color,
        )[#num(v.verse, cfg.dev_numerals)])
        box(numbox + h(0.22em) + vtext(words.first()))
        if words.len() > 1 {
          [ ]
          vtext(words.slice(1).join(" "))
        }
      }
      [ ]
    }
    parbreak()
  }

  // ---- Body ----
  for book in data.books {
    [= #book.name_hi]

    if cfg.chapter_break {
      // Each chapter opens on a fresh page, in its own balanced columns region.
      // (pagebreak can't live inside columns(), so it goes between regions.)
      let first_ch = true
      for ch in book.chapters {
        if not first_ch { pagebreak(weak: true) }
        first_ch = false
        balanced_cols(cfg.columns, cfg.col_gutter, cfg.font_size * 3, chapter_body(book.name_hi, ch))
      }
    } else {
      // Chapters flow continuously through one columns region (paper-saving).
      columns(cfg.columns, gutter: cfg.col_gutter, {
        for ch in book.chapters { chapter_body(book.name_hi, ch) }
      })
    }
  }
}
