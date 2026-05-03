---
name: epub-kb
description: >
  Reference a book knowledge base built from an EPUB with epub_clipper.
  Use when the user asks what the book says about a topic, when a decision
  should be grounded in the source material, or when checking the author's
  framework before advising. Also use to record decisions, insights, or
  open questions against a chapter.
allowed-tools: Read, Grep, Edit
---

# epub-kb: Book Knowledge Base

Knowledge base lives at ./knowledge_base/ — one markdown file per chapter,
produced by epub_clipper (github.com/robinmarin/epub_clipper).

## File layout

  knowledge_base/
    _index.md               ← start here every time
    chapter_01_<slug>.md
    chapter_02_<slug>.md
    ...

Each chapter file has:
- YAML frontmatter: title, chapter, slug, book, author
- ## 📝 Agent Notes     ← write decisions here
- ## ❓ Open Questions   ← write unresolved questions here
- ## 🔗 Cross-References ← write links to related chapters here
- ## Original Text       ← read-only source material

## How to navigate

1. Read _index.md first — always. Find the right chapter(s) before opening anything.
2. Open the relevant chapter file(s).
3. Answer from the original text. Cite as [Chapter N: Section X.Y].
4. Write back any decision, insight, or open question before ending the session.

Never scan chapters sequentially. Never skip _index.md.

## How to write notes

  ## 📝 Agent Notes
  <!-- 2024-03-12: chose 12-1 momentum lookback per section 4.2 -->

  ## ❓ Open Questions
  <!-- how does momentum interact with our low-vol tilt? → check Ch.7 -->

  ## 🔗 Cross-References
  <!-- Ch.7 (Low Volatility) — related factor construction concerns -->

One note per line, prefixed YYYY-MM-DD, reference section if relevant.
Book-level decisions go in _index.md. Chapter-level decisions go in that chapter.

## Rules

- Only use information from the chapter files.
- Never answer from training knowledge when the book covers the topic.
- Always cite inline as [Chapter N: Section X.Y].
- If the book doesn't cover it, say so — don't fill the gap.
- If chapters conflict, surface the tension rather than silently resolving it.
