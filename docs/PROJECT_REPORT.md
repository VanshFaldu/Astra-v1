# ASTRA: AST-based code smell detection with a trainable classifier

## Abstract

ASTRA is a Python static-analysis application for examining maintainability indicators in source code. It uses lexical tokenization, abstract syntax tree construction, scope-local traversal, structural metric extraction and explainable detection rules. A locally trainable decision tree adds a binary function-review prediction. The application provides source-mapped diagnostics, syntax-tree exploration, a compiler pipeline view, configurable thresholds and report exports. Its training workflow uses repository-held-out evaluation to compare a structural rules baseline, a classifier and a predefined hybrid decision policy. No source submitted for analysis is executed. Model performance depends on the independently reviewed dataset supplied by the researcher.

## Problem and objectives

Code can be syntactically correct yet difficult to maintain. ASTRA makes structural concerns visible and explains them in terms a developer can inspect. Objectives are to derive repeatable metrics from syntax, preserve function boundaries, explain every rule finding, inspect compiler artifacts, train on independently reviewed examples, and evaluate alternatives without splitting functions from one repository across training and test sets.

## Scope

Python source, one file per analysis. Seven primary checks and additional magic-number hints. Analysis does not implement a complete compiler, generate machine code, prove defects or automatically rewrite source. Python supplies lexical and syntax processing. The project implements static-analysis passes, the classifier, evaluation and presentation.

## Compiler design mapping

| Phase | Implementation | Artifact |
|---|---|---|
| Lexical analysis | Python tokenize | Token categories, values, locations |
| Syntax analysis | ast.parse | Abstract syntax tree or syntax diagnostic |
| Scope inspection | Local visitors, assignment/read inspection | Local binding table |
| Intermediate structure | AST traversal | Function metric vectors |
| Static analysis | Configurable rules | Source-mapped findings |
| Learned analysis | Binary decision tree | Function review proportion |

Scope inspection is not a full semantic-analysis implementation. ASTRA does not perform type checking or complete name resolution.

## Architecture and implementation

The browser submits JSON to a localhost Python HTTP server. The server parses source and derives metrics; no submitted code is imported or executed. Results include tokens, bindings, an AST representation, diagnostics and optional model predictions. The browser renders these artifacts and generates HTML reports. A terminal entry point emits equivalent JSON reports.

### Metrics

LOC is the function source span, including blank lines and comments. Statement count counts local statement nodes. Parameter count includes positional-only, positional-or-keyword, keyword-only and variadic parameters. Nesting is the maximum depth of structured statements in the function body. Complexity starts at one and counts supported decision nodes, boolean alternatives, comprehension decisions and non-default pattern branches. Calls, loops and branches are also counted. Nested function and class bodies are excluded from outer-function metrics.

### Detection

Long method, parameter list, nesting and complexity compare a metric with its configurable threshold using strictly greater-than. Large class counts direct methods. Duplicate implementation compares exact AST bodies of at least three statements, ignoring locations and formatting. Unused locals have no lexical read in the function subtree; closure reads conservatively count as usage. Magic-number hints identify selected nontrivial numeric literals in expressions.

These definitions should be demonstrated using representative edge cases, rather than described as universal standards.

### Learning algorithm

The classifier recursively chooses a feature threshold that minimizes weighted Gini impurity. Maximum depth is five and each split leaf must contain at least two training samples. Predictions are positive-label proportions in the reached leaf; they are not calibrated confidence. The target is whether a function requires maintainability review. Individual smell categories continue to come from rules.

## Dataset methodology

Export metric vectors from the application. Collect functions from at least five repositories and record provenance, license, function identity and reviewer rationale. Have reviewers judge maintainability independently of the rule thresholds. Prefer two reviewers with disagreements resolved and agreement measured. The CSV workflow requires nonnegative finite metrics, binary labels, repository groups and rationales. The application cannot verify the independence or truthfulness of uploaded labels.

The minimum of thirty samples is an implementation guard, not a scientific sample-size justification. Larger, representative datasets and repeated group-based evaluation are needed for strong research conclusions.

## Evaluation protocol

Sort repository groups, shuffle with seed 42 and hold out approximately twenty percent of groups, with at least one group. Both partitions must contain both classes. Train only on training groups. Compute precision, recall, F1, positive/negative support and confusion matrices on the same held-out examples for:

1. Structural rules: LOC > 40, parameters > 5, nesting > 3 or complexity > 10.
2. ML: positive leaf proportion >= 0.5.
3. Hybrid: proportion >= 0.7, or structural rule true and proportion >= 0.4.

The hybrid policy is defined before evaluation. The rules baseline is a function-level structural baseline and does not encompass file-level duplication, unused-local or class findings. No tuning on held-out repositories should be performed.

### Results to fill after real training

| Variant | Precision | Recall | F1 | Test support |
|---|---|---|---|---|
| Rules | From model.json | From model.json | From model.json | From model.json |
| ML | From model.json | From model.json | From model.json | From model.json |
| Hybrid | From model.json | From model.json | From model.json | From model.json |

Discuss false positives and false negatives with concrete source examples. Do not claim that ML improves rules unless the experiment supports it.

## Validation and demonstration

Automated tests cover branch counting, string literals, function isolation, closure reads, parameter kinds, nesting, duplicate AST bodies, syntax failure, non-execution, tree learning, HTTP analysis and syntax diagnostics. Additional training tests cover invalid datasets and repository isolation. The UI supports clean, smelly and syntax-error demonstrations, source navigation, threshold changes, dataset export, model training and report export.

## Limitations and future work

Single-file and Python-only analysis; lexical usage rather than dataflow; exact-body rather than renamed-clone detection; method-count class heuristic; human-dependent labels; small-data overfitting; one fixed repository holdout; no calibrated probabilities. Future work can add control-flow graphs, def-use chains, interprocedural analysis, repeated grouped validation, richer clone normalization and external evaluation.

## Submission preparation

Add institution, course, student names, faculty guide and date. Insert screenshots captured from the running application. Add verified references to the exact Python documentation version used and relevant original research. Complete the dataset provenance and results sections only with actual collected evidence.
