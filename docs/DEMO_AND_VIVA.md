# Presentation sequence

1. State the problem: valid code may still be difficult to maintain.
2. Show the checkout example and run analysis.
3. Expand deep nesting and high complexity findings; explain their evidence.
4. Jump to the relevant source line.
5. Inspect metrics and expand AST nodes to connect syntax with the findings.
6. Open compiler pipeline: show tokens, local bindings and traversal conventions.
7. Switch to the clean example; discuss fewer findings without claiming perfect code.
8. Trigger the syntax error demo; show a parser diagnostic.
9. Adjust thresholds and rerun to show configurable heuristics.
10. Export an HTML report and print to PDF if needed.
11. Open Model & evaluation. Upload the independently reviewed CSV, train and explain repository separation, precision, recall, F1 and confusion matrices.
12. Discuss limitations and defend the project's compiler-design scope.

# Questions and concise answers

**Why an AST?** It encodes syntactic structure independently of formatting; textual occurrences of keywords are not confused with decision nodes.

**Parse tree versus AST?** A parse tree follows grammar productions and retains more syntactic detail. An AST represents the constructs needed for analysis and generally omits punctuation and intermediate grammar nodes.

**Does this implement a compiler?** It uses a compiler front-end representation to implement static-analysis passes. The Python runtime supplies tokenization and parsing. Code generation is outside scope.

**Why ML when rules work?** Rules expose explicit assumptions; ML can learn interactions from independent reviewer labels. Whether that improves usefulness is an empirical question answered by held-out evaluation.

**What is leakage?** Related functions from one repository may share style and structure. Keeping entire repositories in one partition reduces that source of leakage.

**Why not accuracy alone?** Class imbalance can hide failure on positive examples. Precision measures the fraction of predicted review cases that are labeled positive; recall measures the fraction of labeled positives found. F1 summarizes both.

**Are findings bugs?** No. They are maintainability prompts requiring contextual review.

**Is an unused variable proven dead?** No. This implementation checks lexical reads, not full dataflow or dynamic usage.

**Are probabilities confidence?** They are leaf label proportions, not calibrated confidence estimates.
