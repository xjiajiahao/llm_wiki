# PDF Formula Extraction Workflow

## Why The DeepSeek PDFs Worked Well

The good formula recovery on the DeepSeek reports did not come from raw OCR quality alone. It came from the combination of four factors:

1. **Native PDF text layer**
   The DeepSeek reports are digitally generated PDFs. Their equations are represented as positioned text glyphs, so `pypdf` can often recover enough symbols to reconstruct the math.

2. **Section-first retrieval**
   We did not ask the model to "read the whole PDF and find formulas". We used section titles such as `2.1.1 Multi-Head Latent Attention` and `2.4 Muon Optimizer` to narrow the search window.

3. **Local context over global OCR**
   Once the right pages were found, we extracted full surrounding pages. Nearby prose usually defined the variables, which made symbolic cleanup much easier.

4. **Conservative normalization**
   The model was used to turn noisy linearized text into Markdown math, not to invent missing content. Whenever the source was incomplete, the workflow preserved uncertainty.

## Failure Modes

- Superscripts or subscripts collapse into linear token order.
- Multi-column papers interleave text from both columns.
- Piecewise definitions lose braces or alignment.
- Matrix expressions become unreadable if row layout is destroyed.
- Scanned PDFs have no usable text layer and need OCR or multimodal reading.

## Recommended Prompt Pattern

When using a non-OpenAI model, keep the prompt strict:

```text
You are reconstructing formulas from a native-text PDF extraction.
Use only the supplied snippet.
Do not invent symbols.
First transcribe equations into Markdown math.
Then list any uncertain symbols or positions.
Then explain the meaning in prose.
```

## Adaptation Guidance For DeepSeek And Qwen

This workflow should transfer well to strong DeepSeek and Qwen models if:

- you give them extracted text, not raw page images, when the PDF has a text layer
- you limit each turn to one section or a small page range
- you ask for exact transcription before interpretation
- you require an explicit uncertainty list

It will transfer less well if:

- you ask for too many sections at once
- you mix extraction, interpretation, and comparison in one step
- you rely on the model to infer missing notation from prior knowledge

## Practical Heuristic

Use this decision rule:

- If the PDF text layer is readable: text extraction first, model second.
- If the PDF text layer is poor but pages are visually clean: multimodal/OCR first, model second.
- If both are poor: do not promise exact reconstruction; produce a best-effort note with uncertainty markers.
