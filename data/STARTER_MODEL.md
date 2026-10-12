# Included pretrained educational model

This model uses 40 Python functions authored by the AI assistant in five domain modules: orders, accounts, inventory, telemetry and scheduling. Half are labeled acceptable and half require review. These are examples, not collected open-source repositories or independently human-reviewed observations.

Labels were attached to source based on cohesion, clarity of interfaces, mixed responsibilities and interdependent control flow before extracting metrics. They were not copied from the rule detector. Nevertheless, the same assistant authored and labeled the examples. That is not independent annotation, and the designed contrast between examples can make classification artificially easy.

Source files with label rationale are in `data/starter_sources`. Exact metrics and labels are in `data/starter_training.csv`. Training, group split, tree and evaluation are reproducible with:

```
py prepare_starter_model.py
```

Four modules (32 functions) train the tree; one module (8 functions) is held out using the existing seeded split. Related structural patterns occur across domains, so module separation is not equivalent to validating on independently collected repositories. Scores in `starter_evaluation.json` describe only this educational corpus and must not be advertised as real-world detection accuracy.

The trained classifier predicts a binary function-review target. It does not identify individual smell categories or understand arbitrary business context. Rules still supply specific smell findings. To establish research performance, replace this starter dataset with independently reviewed real Python functions, retain provenance and licenses, and evaluate on unseen repositories.
