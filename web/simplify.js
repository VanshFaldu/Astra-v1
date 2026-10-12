// Keep routine analysis prominent; research workflows remain available on demand.
(() => {
  const model=document.querySelector('#model');
  const evaluation=document.querySelector('#evaluation');
  const evaluationCard=document.createElement('article');evaluationCard.className='panel padded';
  evaluationCard.innerHTML='<h2>Model evaluation</h2><p>Compare the structural rules, classifier and hybrid policy on held-out examples.</p>';
  evaluationCard.append(evaluation);
  const training=document.querySelector('#training-file').closest('article');
  const advanced=document.createElement('details');advanced.className='panel padded advanced-research';advanced.id='advanced-research';
  advanced.innerHTML='<summary>Advanced / Research <span>Dataset preparation and replacement-model training</span></summary>';
  training.before(evaluationCard,advanced);advanced.append(training);
  const preparation=model.querySelector('.two-col');if(preparation)advanced.append(preparation);
  const experiment=[...model.querySelectorAll('article')].find(a=>a.querySelector('h2')?.textContent==='Comparative experiment');if(experiment)advanced.append(experiment);
  const settings=document.querySelector('.settings summary');settings.innerHTML='Advanced analysis settings <span>Optional rule thresholds</span>';
  const guide=document.querySelector('#guide');
  guide.innerHTML=`<div class="eyebrow">HELP WHEN YOU NEED IT</div><h1>Understand your analysis<span>.</span></h1><p class="lead">Paste Python code, analyze it, inspect the evidence, then export your report.</p><div class="two-col"><article class="panel padded"><h2>Start with the essentials</h2><p>The Demo tutorial button opens a short introduction to source code, findings, metrics, the AST and model predictions. Your workspace is restored afterward.</p><button id="quick-tour-help" class="secondary">Start quick tutorial</button></article><article class="panel padded"><h2>Explore the complete workflow</h2><p>The complete walkthrough also covers syntax errors, tokens, local variable usage, optional training, CSV export and reporting.</p><button id="full-tutorial" class="secondary">Complete walkthrough</button></article></div><article class="panel padded"><h2>How to read a finding</h2><p>Read the evidence, inspect the highlighted source and decide whether the suggested change fits your code. A code smell is a review prompt, not a proven bug. Magic-number hints are supplementary, low-priority suggestions.</p><h2>What the project analyzes</h2><p>Python supplies the tokenizer and parser. ASTRA measures the resulting tree and applies static-analysis rules. Local variable usage checks assignments and lexical reads; it is not full semantic analysis. Large class means many direct methods, not proof of a God Class.</p><h2>About the model</h2><p>The included classifier predicts whether a function needs review. Its assistant-authored training examples support demonstrations, not independently validated real-world accuracy. Specific smell names still come from the rules.</p><p>Presenter notes and viva preparation are included in docs/DEMO_AND_VIVA.md in the project folder.</p></article>`;
  const guideButton=document.querySelector('[data-page="guide"] span');guideButton.textContent='Help';
  const symbolHeading=document.querySelector('#symbols').parentElement.querySelector('h2');symbolHeading.textContent='Local variable usage';
  document.querySelector('#model > .lead').textContent='Function-review predictions and transparent evaluation. Retraining is optional.';
})();
