---
name: pdf-paper-formula-workflow
description: Use this skill when you need to read digitally-generated PDF papers, recover formulas or algorithm steps from native PDF text, explain why formula extraction succeeded or failed, or turn that process into structured notes. Best for arXiv-style technical reports, papers with embedded text layers, equation-heavy sections, and workflows that must be reusable across models such as OpenAI, DeepSeek, or Qwen.
---

# PDF Paper Formula Workflow

## Overview

Use this skill when a user wants high-fidelity extraction of formulas, symbols, or algorithm steps from a PDF paper, especially a native-text technical PDF rather than a scanned image PDF.

This skill is optimized for the workflow that worked well on the DeepSeek reports:

1. Verify that the PDF has a usable text layer.
2. Locate the right section by title or keyword instead of reading the whole paper blindly.
3. Extract page-local context around the target equations.
4. Reconstruct formulas conservatively into Markdown math.
5. Preserve uncertainty explicitly when the extracted text is ambiguous.

## When This Works Well

- The PDF is digitally generated and its formulas are encoded as text glyphs, not just pixels.
- The target equations are surrounded by readable prose, captions, or section titles.
- You only need selected sections, not perfect full-document TeX reconstruction.
- The model is good at symbolic cleanup and disciplined about not inventing notation.

## When This Works Poorly

- The PDF is scanned or image-only.
- The extractor returns garbled token order, missing superscripts, or broken symbols.
- The paper uses exotic fonts or heavy two-column layout that destroys reading order.
- The task requires exact publisher-grade reconstruction of every formula in the whole paper.

In those cases, fall back to OCR or multimodal page reading and mark the result as lower confidence.

## Workflow

### Step 1: Check Whether The PDF Has A Native Text Layer

Try extracting 1-2 pages with `pypdf`. If the output contains readable section titles, symbols, and equation fragments, stay on the native-text path.

Use the bundled script:

```bash
python3 skills/pdf-paper-formula-workflow/scripts/extract_pdf_context.py \
  raw/paper.pdf \
  --pages 7-9
```

If the output is mostly empty, heavily scrambled, or missing equations entirely, stop treating the PDF as a text-first source and switch to OCR/multimodal reading.

### Step 2: Find Anchors Before Reconstructing Formulas

Do not ask the model to recover formulas from the entire PDF at once.

Instead, locate anchors such as:

- section titles like `2.3.1 Compressed Sparse Attention`
- concept names like `Muon`, `MLA`, `Sinkhorn-Knopp`
- variable names like `n_win`, `t_max`, `d_c`
- figure captions or algorithm labels

Use the script with `--term`:

```bash
python3 skills/pdf-paper-formula-workflow/scripts/extract_pdf_context.py \
  raw/paper.pdf \
  --term "Muon" \
  --term "Compressed Sparse Attention"
```

Then extract the surrounding pages, not just the keyword hit snippet.

### Step 3: Prefer Page-Local Reconstruction

Once you know the right pages, extract those pages in full and reconstruct formulas from that local window.

This is why the DeepSeek formulas came out well:

- the reports are native PDFs with accessible text layers
- the equations were near matching prose definitions
- the extraction was scoped to the exact section
- the model only had to normalize notation, not guess the whole paper structure

### Step 4: Reconstruct Conservatively

When turning extracted text into Markdown math:

- preserve original variable names exactly
- prefer the paper's notation over your own
- keep one formula per display block when possible
- use prose to explain missing pieces instead of silently filling them in
- if an operator, bound, or superscript is unclear, say so explicitly

Good pattern:

```markdown
The report gives the update as:

$$
W_t = W_{t-1}(1 - \eta \lambda) - \eta O_t
$$

The surrounding text indicates that $O_t$ comes from hybrid Newton-Schulz orthogonalization.
```

Bad pattern:

- silently replacing unreadable symbols with guessed ones
- mixing paper notation with remembered notation from another source
- writing synthetic formulas that are merely plausible

### Step 5: Use The Model As A Symbolic Normalizer, Not As OCR

The model's strongest role here is:

- cleaning token order
- restoring mathematical formatting
- aligning formulas with nearby prose
- spotting when the extracted text contradicts the intended equation

Its weakest role is inventing missing symbols from memory. Keep the model on a short leash.

## Model Adaptation

This workflow is reusable across OpenAI, DeepSeek, and Qwen-class models if the PDF extraction step is deterministic and the prompting is strict.

Use the same division of labor:

- script/extractor: find pages and emit raw text windows
- model: normalize notation, structure formulas, explain uncertainty

Expected behavior by model family:

- Strong frontier models usually do better at symbolic cleanup and consistency across long snippets.
- Strong open models such as newer DeepSeek or Qwen variants can work well if you keep the extraction window tight and instruct them not to guess.
- Smaller or weaker models degrade first on superscripts, nested subscripts, piecewise conditions, and long dependency chains across multiple equations.

If switching models, tighten the workflow rather than trusting raw capability:

1. Extract fewer pages at a time.
2. Ask for exact transcription before explanation.
3. Ask the model to list uncertain symbols separately.
4. Compare reconstructed formulas against the raw extracted snippet.

## Scripts And References

- For deterministic extraction and keyword/page search, use `scripts/extract_pdf_context.py`.
- For rationale, fallbacks, and model-specific guidance, read `references/workflow.md`.

## Output Patterns

Use this skill for outputs such as:

- wiki concept pages with Markdown formulas
- source notes that separate verified formulas from inferred explanation
- side-by-side "raw extraction vs normalized math" artifacts
- reusable extraction workflows for other papers and models
