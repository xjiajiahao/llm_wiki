# LLM Wiki Agent Schema

This repository is a local-first LLM-maintained wiki for large-model knowledge.

## Operating Model

- Treat `raw/` as immutable source material. Never modify files in `raw/`.
- Treat markdown files outside `raw/` as the maintained wiki layer.
- Update `index.md` whenever pages are created, renamed, or materially changed.
- Append a dated entry to `log.md` for each ingest, major query artifact, or lint pass.
- Prefer Obsidian-style wiki links such as `[[concepts/mixture-of-experts]]`.
- Preserve uncertainty explicitly. If a claim has not been verified from a raw source, mark it as pending instead of inferring details.
- Default to concept-first organization. Reusable knowledge belongs in `concepts/`; model pages should mainly capture how a model instantiates, modifies, or combines those concepts.

## Directory Conventions

- `sources/`: one page per raw source.
- `entities/`: organizations, people, products, datasets.
- `models/`: model-specific pages.
- `concepts/`: reusable technical concepts such as architectures, modules, objectives, optimizers, parallelism, quantization, and inference mechanisms.
- `notes/`: synthesized query outputs, comparisons, and working notes.

## Ingest Workflow

1. Identify the raw source and create or update a page in `sources/`.
2. Extract verifiable metadata first: title, date, authors if available, raw path, checksum.
3. Summarize the source in the source page.
4. Propagate durable facts into relevant concept pages first, then update entity/model pages with instance-specific details.
5. Update `index.md`.
6. Append an entry to `log.md`.

## Concept Page Expectations

- Each concept page should explain:
  - what the concept is;
  - what problem it solves;
  - how it works at a high level;
  - any concrete formulas, routing rules, or algorithmic steps that are stable enough to state;
  - where it appears in specific model families.
- If the current sources only justify a partial explanation, keep the page as a scoped stub instead of inventing missing math.

## Query Workflow

1. Read `index.md` to find relevant pages.
2. Read the minimum set of pages needed to answer the question.
3. Cite the pages used.
4. If the answer is durable, save it in `notes/` and log it.

## Lint Workflow

- Look for orphan pages, missing backlinks, stale summaries, duplicated concepts, and unresolved placeholders.
- Record lint results in `log.md`.

## Shell Convention

- Prefix shell commands with `rtk` when feasible in this repo.
