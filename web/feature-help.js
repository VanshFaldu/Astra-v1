// Delegated hover/focus help also supports findings rendered after analysis.
(() => {
  const descriptions = [
    ['[data-tab="metrics"]','Function metrics','View measurements for each Python function.'],
    ['[data-tab="tree"]','AST explorer','Expand the tree to inspect the parsed structure of your code.'],
    ['#severity','Severity filter','Show findings by review priority. This does not change the analysis.'],
    ['.finding summary','Code smell finding','Click to see evidence and an improvement suggestion. A finding is not a proven bug.'],
    ['.settings > summary','Analysis thresholds','Adjust the limits used by the rule detector.'],
    ['[data-limit="loc"]','Method length limit','Flag a function when its source span exceeds this number of lines.'],
    ['[data-limit="parameters"]','Parameter count limit','Flag a function when it takes more than this many inputs.'],
    ['[data-limit="nesting"]','Nesting depth limit','Flag structured statements nested deeper than this limit.'],
    ['[data-limit="complexity"]','Complexity limit','Flag functions with more decision complexity than this limit.'],
    ['[data-limit="methods"]','Class method limit','Flag classes with more direct methods than this limit.'],
    ['#training-file','Labeled training dataset','Select a CSV with metrics, repository groups, labels and review rationale.'],
    ['.training-controls > label','Select labeled CSV','Choose reviewed training data. Selecting a file alone does not train the model.'],
    ['#train-model','Train and evaluate','Replace the local model using the selected dataset and evaluate held-out groups.'],
    ['#dataset','Download function metrics','Export the current measurements as CSV for dataset preparation.'],
    ['#model-status','Model status','Shows whether a trained classifier is available.'],
    ['#predictions','ML predictions','Shows the model\'s function-review predictions, not specific smell categories.'],
    ['#tokens','Lexical tokens','Names, keywords, literals and operators recognized in the source.'],
    ['#symbols','Local variable bindings','Assignments and detected lexical reads within functions.'],
    ['.tree summary','Syntax tree node','A program construct. Expand the node to inspect its children.'],
    ['.stats article:nth-child(1)','Issues detected','Number of review findings in the latest successful analysis.'],
    ['.stats article:nth-child(2)','Functions analyzed','Number of Python functions inspected in the source.'],
    ['.stats article:nth-child(3)','AST nodes','Number of structural nodes in the parsed syntax tree.'],
    ['.stats article:nth-child(4)','Analysis engine','Rule detection and the availability of a trained classifier.']
  ];
  const metricHelp={Function:'The Python function being measured.',LOC:'The function source span, including blank lines and comments.',Params:'Number of input parameters.',Depth:'Maximum nesting of structured statements.',CC:'Cyclomatic complexity: a decision-count estimate.',Calls:'Number of function-call expressions.',Precision:'Among predicted review cases, the fraction labeled as needing review.',Recall:'Among labeled review cases, the fraction detected.',F1:'A combined precision and recall score.'};
  const tooltip=document.createElement('div');tooltip.id='feature-tooltip';tooltip.setAttribute('role','tooltip');tooltip.hidden=true;document.body.append(tooltip);
  let active=null,timer=null;
  function hide(){clearTimeout(timer);if(active){active.classList.remove('feature-hover');const ids=(active.getAttribute('aria-describedby')||'').split(' ').filter(x=>x&&x!=='feature-tooltip');if(ids.length)active.setAttribute('aria-describedby',ids.join(' '));else active.removeAttribute('aria-describedby');}active=null;tooltip.hidden=true;}
  function find(element){
    if(!(element instanceof Element)||element.closest('#tutorial-dialog,#feature-tooltip'))return null;
    const cell=element.closest('th');
    if(cell&&metricHelp[cell.textContent.trim()])return {el:cell,name:cell.textContent.trim(),text:metricHelp[cell.textContent.trim()]};
    for(const [selector,name,text] of descriptions){const el=element.closest(selector);if(el)return {el,name:el.matches('.finding summary')?(el.querySelector('h3')?.textContent||name):el.matches('.tree summary')?el.textContent.trim():name,text};}
    return null;
  }
  function position(){if(!active)return;const r=active.getBoundingClientRect(),width=tooltip.offsetWidth,height=tooltip.offsetHeight;let left=Math.min(Math.max(8,r.left),innerWidth-width-8);let top=r.bottom+9;if(top+height>innerHeight-8)top=r.top-height-9;if(top<8)top=8;tooltip.style.left=left+'px';tooltip.style.top=top+'px';}
  function show(info,immediate=false){
    if(info?.el===active)return;
    hide();if(!info||document.querySelector('#tutorial-dialog')?.open)return;
    active=info.el;active.classList.add('feature-hover');
    const reveal=()=>{if(active!==info.el)return;tooltip.replaceChildren();const name=document.createElement('strong');name.textContent=info.name;const copy=document.createElement('span');copy.textContent=info.text;tooltip.append(name,copy);tooltip.hidden=false;const ids=new Set((active.getAttribute('aria-describedby')||'').split(' ').filter(Boolean));ids.add('feature-tooltip');active.setAttribute('aria-describedby',[...ids].join(' '));position();};
    if(immediate)reveal();else timer=setTimeout(reveal,300);
  }
  document.addEventListener('pointerover',e=>{if(e.pointerType!=='touch')show(find(e.target));});
  document.addEventListener('pointerout',e=>{if(active&&!active.contains(e.relatedTarget))hide();});
  document.addEventListener('focusin',e=>show(find(e.target),true));
  document.addEventListener('focusout',hide);
  document.addEventListener('keydown',e=>{if(e.key==='Escape')hide();});
  document.addEventListener('click',hide);
  window.addEventListener('scroll',hide,true);window.addEventListener('resize',hide);
})();
