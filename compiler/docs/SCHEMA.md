# Source YAML schema

One folder per book (English canonical name — e.g. `Matthew/`), one `.yaml` file
per chapter (`Matthew/1.yaml`). Book ordering and Hindi display names come from
`compiler/books.py`, so the folder name is the only thing that must match.

## Current (required) fields

```yaml
- book: "मत्ती"
  chapter: 16
  verses:
    - verse: 1
      text: "फरीसी और सदूकी उसके पास आए ..."
```

## Reserved (optional) fields — safe to start using now

The compiler already reads these; add them per-verse when the content warrants it.
Files without them stay 100% valid, so contributors are never blocked.

```yaml
- book: "मत्ती"
  chapter: 5
  verses:
    - verse: 1
      heading: "पहाड़ी उपदेश"      # section/pericope title, printed above the verse
      text: "भीड़ को देखकर यीशु पहाड़ पर चढ़ गया ..."
    - verse: 2
      redletter: true              # words of Christ — rendered red in the premium tier
      text: "और उसने बोलना आरंभ किया ..."
```

| Field       | Type    | Meaning                                              | Tiers that show it        |
|-------------|---------|------------------------------------------------------|---------------------------|
| `heading`   | string  | Section title printed before this verse              | all                       |
| `redletter` | boolean | Verse is spoken by Christ                            | premium (red); others: plain |

### Not yet wired, but reserve the names before books multiply

If you expect to want these, agree on the field names now so 66 books don't need
retrofitting later:

- `footnotes` — list of `{marker, text}` for translation/textual notes
- `poetry: true` — indent as verse/poetry (Psalms, Proverbs)
- `paragraph: true` — start a new prose paragraph at this verse

## Note on the top-level shape

The compiler accepts **both** file shapes, so contributors can't get it wrong:
a 1-element list (`- book: ...`, the current repo convention) or a plain
top-level map (`book: ...`, as shown in the upstream README). `.yml` and
`.yaml` extensions both work; the filename must be the chapter number.

## What the compiler does to your text

- Whitespace is normalized (leading/trailing stripped, doubles collapsed).
- Straight quotes are converted to typographic quotes (`"` → “ ”, `'` → ‘ ’)
  based on position, so quotations spanning verses pair correctly.

## Validation

The build warns (but still builds) on: missing/duplicate chapters or verses,
`chapter:` not matching the filename, `book:` not matching the folder's Hindi
name, empty verse text, and malformed entries. Gaps can be legitimate — e.g.
Matthew 17:21 and 18:11 are textual variants intentionally omitted by modern
translations — so warnings are informational, for a human to review.
