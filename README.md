# ASTRA — AI-assisted code smell detection using AST

A local Compiler Design project with a responsive analysis workspace, source-mapped diagnostics, token and symbol inspection, AST explorer, configurable thresholds, HTML report export, and an independently trainable decision tree.

## Run

Python 3.10 or newer. No external Python packages required.

```powershell
py server.py
```

Open http://127.0.0.1:8000. Windows users may double-click `start.bat`. The server binds only to localhost. Fonts have local fallbacks when offline. Submitted source is parsed, never executed or persisted by the server. Browser session state is in memory.

## Verify

```powershell
py -m unittest discover -s tests -v
```

## Train the AI component

1. Analyze files and download function metrics in **Model & evaluation**.
2. Combine metrics from multiple repositories. Fill `repository`, binary `label` (1 = review warranted, 0 = acceptable), and `review_rationale` using independent human review. Keep licensing and provenance records. Do not derive labels from the same rule thresholds.
3. Upload the completed CSV in **Model & evaluation** and click **Train & evaluate**, or run `py ml.py dataset.csv`. At least 30 samples and five repositories are required; both training and held-out data must contain both classes. Prefer a much larger balanced and reviewed dataset.
4. The script writes `model.json`, including the decision tree and repository-held-out precision, recall, F1 and confusion matrix. Refresh and analyze to activate function predictions. Model files are local project artifacts; do not load untrusted replacements.

The model predicts a **binary function review target**, not the individual smell types. Leaf proportions are not calibrated confidence. Rules remain separate from model predictions. Training evaluates a four-metric structural rules baseline, ML and a predefined hybrid policy on the same held-out repositories. An educational starter model is bundled; its provenance and limitations are described below. No real-world accuracy is claimed. Independent data collection remains necessary before drawing research conclusions.

## Submission materials and terminal usage

`docs/PROJECT_REPORT.md` contains a formal report draft with methodology, architecture, definitions and an honest results template. `docs/DEMO_AND_VIVA.md` contains the presentation sequence and viva answers. `data/annotation_template.csv` is an empty dataset template.

```powershell
py cli.py examples/clean.py --output report.json
```

The application now includes dataset upload, training validation, repository-held-out comparisons and confusion matrices. After source updates, restart the Python server and reload the browser to ensure new API routes are available. If `py` is unavailable, `start.bat` also checks the installed local Python interpreter.

## Architecture

`source → tokenize → ast.parse → local tree visitors → metrics → rule diagnostics / trained decision tree → interactive report`

`analyzer.py`: AST analysis. `ml.py`: CART-style binary decision tree using Gini impurity, bounded depth and minimum leaves. `server.py`: local HTTP API and static assets. `web/`: UI. `tests/`: semantic and classifier checks.

Seven primary smells: long method, long parameter list, deep nesting, high complexity, large class, duplicate implementation, unused local. Magic-number hints are additionally reported. Thresholds use strictly greater-than comparisons.

## Academic report outline

1. Abstract and problem statement.
2. Compiler phase mapping and AST versus parse tree.
3. Related work with independently verified citations.
4. Architecture, visitors, feature definitions and algorithms.
5. Dataset provenance, annotation protocol and reviewer agreement.
6. Repository-separated evaluation: rules, ML and predefined hybrid policy.
7. Precision, recall, F1, confusion matrix and false-positive case studies.
8. UI screenshots, demonstration sequence and testing.
9. Limitations and future work.

## Limitations

Python only; built-in parser rather than a custom grammar. No bytecode generation or full semantic analyzer. LOC counts source span including blank lines/comments. Nesting counts structured statements, not comprehension depth. Unused locals use lexical reads, count closure reads conservatively and do not model dynamic `locals()` or full name resolution. Duplicate detection compares exact AST bodies of at least three statements; identifier-renamed clones are not detected. Large-class detection counts direct methods only. Magic number rules are context heuristics. AST display caps depth at 14. Source request limit is 200 KB. Intended for local academic demonstrations, not exposed production hosting.

## Suggested viva demo

Analyze the supplied smelly example, expand a finding, jump to its source, inspect metrics and the AST, inspect tokens and symbols, compare the clean example, trigger the syntax-error demo, customize thresholds and export the report. Present the training methodology and current model status honestly. Exported HTML can be printed to PDF.


## Pretrained educational starter (added 9 October 2026)

A ready-to-use model is now included in `model.json`. It was trained on 40 assistant-authored and assistant-labeled source examples (32 training, 8 held-out), not a public or independently annotated research dataset. See `data/STARTER_MODEL.md` for provenance and limitations. Source, CSV and held-out evaluation are retained in `data/`. Reproduce with `py prepare_starter_model.py`. Research claims still require independent real-world evaluation.


## Guided first-use demo

Click **Demo tutorial** in the top bar for a 23-step walkthrough. Next and Back explain and demonstrate the editor, examples, analysis, findings, source navigation, filters, metrics, AST, thresholds, clean-code comparison, syntax diagnostics, compiler pipeline, pretrained ML, evaluation, optional training, CSV export, reporting and project guide. The demo uses temporary source and default thresholds. Finishing, Close or Escape restores the prior workspace. No file download or model training is performed automatically. The local server must be running for analysis steps.


## Simplified interface

Routine code analysis remains the main workspace. The default Demo tutorial now has 10 steps; Help offers the complete walkthrough. Training, metrics CSV preparation and comparative experiment instructions are collapsed under Advanced / Research. Evaluation remains visible. Thresholds are under Advanced analysis settings. Hover explanations remain for technical terms and less familiar controls. Viva preparation stays in docs/DEMO_AND_VIVA.md. Magic-number hints remain supplementary and low priority.

## GitHub repository

https://github.com/VanshFaldu/Astra-v1

