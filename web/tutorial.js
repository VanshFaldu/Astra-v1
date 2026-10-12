// An opt-in guided demo. User source, results and thresholds are restored on exit.
(() => {
  const launch = document.createElement('button');
  launch.id = 'demo-tutorial'; launch.className = 'secondary tutorial-launch';
  launch.textContent = 'Demo tutorial';
  document.querySelector('header').append(launch);
  const dialog = document.createElement('dialog');
  dialog.id = 'tutorial-dialog';
  dialog.setAttribute('aria-labelledby', 'tutorial-title');
  dialog.innerHTML = `<div class="tutorial-card"><div class="tutorial-top"><span id="tutorial-count"></span><button id="tutorial-close" aria-label="Close tutorial">Close</button></div><div class="tutorial-progress"><span></span></div><div class="eyebrow">YOUR FIRST ASTRA ANALYSIS</div><h2 id="tutorial-title"></h2><p id="tutorial-copy"></p><div id="tutorial-tip"></div><p id="tutorial-error" role="alert" hidden></p><div class="tutorial-controls"><button id="tutorial-back" class="secondary">Back</button><button id="tutorial-next" class="primary">Next step</button></div><small>Demo changes are temporary. Your code and results return when you finish or close.</small></div>`;
  const spotlight = document.createElement('div'); spotlight.id = 'tutorial-spotlight'; spotlight.hidden = true;
  document.body.append(spotlight, dialog);
  const q = s => dialog.querySelector(s);
  let index = 0, snapshot = null, busy = false, highlighted = null;
  const page = name => document.querySelector(`[data-page="${name}"]`).click();
  const tab = name => document.querySelector(`[data-tab="${name}"]`).click();
  function sample(name) { $('#sample').value = name; $('#sample').onchange(); }
  async function demo(name='smelly') {
    sample(name); await run();
    if (!$('#error').hidden) throw Error('The demo needs the local server. Start ASTRA using start.bat, then retry this step.');
  }
  const allSteps = [
    {title:'Welcome! Let us review code together', text:'ASTRA reads Python code and points out parts that may be hard to maintain. It never runs the code you submit. This walkthrough demonstrates each feature using temporary examples.',target:'.intro',tip:'Use Next step and Back. Close or press Escape whenever you like.',enter:()=>page('workspace')},
    {title:'Choose code to review',text:'This is the code editor. Normally you can paste your own Python code or use Open file to load a .py file. For this tutorial, we have selected an example with several maintainability concerns.',target:'.editor-panel',tip:'Your original code is saved for the duration of the tutorial.',enter:()=>{page('workspace');sample('smelly')}},
    {title:'Examples let you explore safely',text:'This menu offers a smelly example, a cleaner example, and a syntax-error example. You can try all three without preparing a file.',target:'#sample',tip:'Smelly does not mean broken. It means the code deserves a closer look.',enter:()=>page('workspace')},
    {title:'Analyze the code',text:'Analyze code asks the Python server to build a syntax tree, measure functions and produce findings. We have run it for you now using the smelly example.',target:'#analyze',tip:'Outside this tutorial, you can also press Ctrl + Enter in the editor.',enter:async()=>{page('workspace');await demo()}},
    {title:'Read the summary',text:'Issues detected counts review findings. Functions analyzed counts Python functions. AST nodes counts pieces of the parsed structure. The engine card tells you about the analysis methods.',target:'.stats',tip:'These numbers describe the analyzed code; they are not a pass/fail grade.',enter:()=>page('workspace')},
    {title:'Findings explain the concerns',text:'Each finding has a name, a source line and a severity. High, medium and low are rough review priorities. A finding is not proof of a bug.',target:'.result-panel',tip:'For example, a long parameter list means one function takes many separate inputs.',enter:()=>{page('workspace');tab('findings')}},
    {title:'Open a finding for evidence',text:'We have expanded a finding. Evidence tells you exactly why it was flagged. The suggestion gives you a possible improvement, such as splitting responsibilities or simplifying nesting.',target:'.finding',tip:'In normal use, click a finding heading to expand or collapse it.',enter:()=>{page('workspace');tab('findings');const f=$('.finding');if(f)f.open=true}},
    {title:'Jump to the relevant source',text:'View source selects the line associated with a finding in the editor. We have demonstrated that jump. This connects the explanation to the actual code.',target:'#source',tip:'If you edit the code after analysis, run analysis again before jumping to findings.',enter:()=>{page('workspace');tab('findings');const f=$('.finding');if(f){f.open=true;f.querySelector('.jump')?.click()}}},
    {title:'Filter by severity',text:'Use this menu to see high-, medium- or low-priority findings. Filtering changes only the view; it does not change the analysis.',target:'#severity',tip:'During your own review, start with high-priority findings and inspect their context.',enter:()=>{page('workspace');tab('findings')}},
    {title:'Metrics are the measurements',text:'LOC is the function length. Params counts inputs. Depth measures nested structures. CC estimates decision complexity. Calls counts function-call expressions. These measurements support the rule findings and the ML model.',target:'#result-content',tip:'A high measurement is a reason to review, not automatically bad design.',enter:()=>{page('workspace');tab('metrics')}},
    {title:'Explore the syntax tree',text:'An AST is code represented as a tree. FunctionDef means a function, If means a condition, Assign means an assignment and Return means a returned value. Expand branches in normal use to inspect the structure.',target:'#result-content',tip:'The parser can distinguish a real if statement from the word "if" inside a string.',enter:()=>{page('workspace');tab('tree');const children=$('.tree details details');if(children)children.open=true}},
    {title:'Customize the rule thresholds',text:'Thresholds are limits used by the rules. For example, a parameter limit of 5 flags functions with more than 5 inputs. You can change these numbers and analyze again. This does not retrain the ML model.',target:'.settings',tip:'We use default thresholds during the demo and restore your original settings afterward.',enter:()=>{page('workspace');$('.settings').open=true}},
    {title:'Compare with cleaner code',text:'We have analyzed the clean example. Compare its findings and measurements with the first example. Smaller, focused functions are often easier to read, but passing these checks does not prove perfect code.',target:'.work-grid',tip:'Outside the tutorial, use the example menu and Analyze code to compare for yourself.',enter:async()=>{page('workspace');tab('findings');await demo('clean')}},
    {title:'Understand syntax errors',text:'This example is missing a colon after a function definition. The parser reports an error and its line instead of treating invalid code as a successful analysis. Previous successful results can remain visible until the source is corrected.',target:'#error',tip:'Fix the source syntax first, then analyze again.',enter:async()=>{page('workspace');sample('syntax');await run();if($('#error').hidden)throw Error('The syntax-error demonstration did not produce the expected diagnostic.')}},
    {title:'See the compiler pipeline',text:'The pipeline is source code, tokens, AST, measurements and findings. Tokens are small pieces such as names, numbers and operators. We have restored the smelly example so you can inspect real artifacts.',target:'.pipeline-flow',tip:'Python supplies the tokenizer and parser. ASTRA implements the analysis around them.',enter:async()=>{await demo();page('pipeline')}},
    {title:'Inspect tokens and local variables',text:'The left table shows the pieces recognized by the tokenizer. The right table lists local variable bindings and whether a lexical read was found. This is a simple usage check, not complete type checking or proof of dead code.',target:'#pipeline .two-col',tip:'For instance, a variable assigned but never read may deserve review.',enter:()=>page('pipeline')},
    {title:'Understand your pretrained model',text:'The model predicts whether a function needs maintainability review. Rules still provide specific smell names. Your starter model uses assistant-authored educational examples; it is ready for a demo but is not independently validated on real-world projects.',target:'#model-status',tip:'A review proportion is based on labels in a decision-tree leaf, not guaranteed confidence.',enter:async()=>{page('model');await loadEvaluation()}},
    {title:'Read the evaluation results',text:'Precision asks whether flagged functions really had positive labels. Recall asks how many positive cases were found. F1 combines them. Confusion matrices show correct decisions, false alarms and missed cases for rules, ML and hybrid methods.',target:'#evaluation',tip:'Perfect scores on eight educational test examples do not mean perfect performance on arbitrary code.',enter:()=>page('model')},
    {title:'Optional: train a replacement model',text:'To improve the model, collect independently reviewed Python functions. Download metrics, add repository, label 0 or 1 and review rationale, then upload the CSV and train. At least 30 functions across 5 groups are required. Training replaces the local model.',target:'.training-controls',tip:'This tutorial does not upload data or retrain your model. You can use the current model immediately.',enter:()=>page('model')},
    {title:'Download function metrics',text:'Download current metrics CSV exports the measured functions from your latest analysis. It is a starting point for preparing training data, not an already labeled dataset.',target:'#dataset',tip:'A reviewer must add the labels and explanations before training.',enter:()=>page('model')},
    {title:'Export a readable report',text:'Export report downloads an HTML document containing the analyzed source, findings, measurements and thresholds. Open it in a browser and print to PDF if needed.',target:'#export',tip:'The tutorial does not download anything automatically.',enter:()=>{page('workspace');tab('findings')}},
    {title:'Your guide and presentation companion',text:'Help explains how to read findings, the compiler-design connection and the model limitations. Presenter notes and viva answers are available in the project documentation.',target:'#guide .two-col',tip:'Explain the structure, show the evidence, then discuss what the tool can and cannot conclude.',enter:()=>page('guide')},
    {title:'You are ready to use ASTRA',text:'Your normal workflow is: open or paste Python code, analyze, inspect findings, check the measurements and tree, then export a report. Finish will restore the code, results, settings and page you had before this demo.',target:'#demo-tutorial',tip:'You can restart this walkthrough anytime with Demo tutorial.',enter:()=>page('workspace')}
  ];
  let steps=allSteps;
  function position() {
    if(!dialog.open||!highlighted)return;
    dialog.classList.remove('tutorial-docked');
    dialog.style.maxHeight=`${innerHeight-24}px`;
    let r=highlighted.getBoundingClientRect();
    let p=tutorialPlacement(r,dialog.offsetWidth,dialog.offsetHeight,innerWidth,innerHeight);
    if(p.docked){
      dialog.classList.add('tutorial-docked');
      dialog.style.maxHeight=`${Math.floor(innerHeight*.44)}px`;
      const reserve=dialog.offsetHeight+32;
      document.body.style.setProperty('--tutorial-reserve',`${reserve}px`);
      document.body.classList.add('tutorial-reserved');
      if(r.top<12||r.top>innerHeight-reserve-70){
        window.scrollBy({top:r.top-16,behavior:'instant'});
        r=highlighted.getBoundingClientRect();
      }
      p={left:Math.max(12,innerWidth-dialog.offsetWidth-12),top:innerHeight-dialog.offsetHeight-12};
    }
    dialog.style.left=`${p.left}px`;dialog.style.top=`${p.top}px`;
    const bottom=Math.min(r.bottom+5,p.docked?innerHeight-dialog.offsetHeight-24:innerHeight-4);
    const top=Math.max(4,r.top-5),left=Math.max(4,r.left-5);
    spotlight.style.cssText=`left:${left}px;top:${top}px;width:${Math.max(0,Math.min(r.right+5,innerWidth-4)-left)}px;height:${Math.max(0,bottom-top)}px;`;
  }
  async function show(nextIndex) {
    if(busy)return; busy=true;index=nextIndex;
    document.body.classList.remove('tutorial-reserved');
    q('#tutorial-error').hidden=true;
    q('#tutorial-title').textContent=steps[index].title;
    q('#tutorial-copy').textContent=steps[index].text;
    q('#tutorial-tip').textContent=steps[index].tip;
    q('#tutorial-count').textContent=`Step ${index+1} of ${steps.length}`;
    q('.tutorial-progress span').style.width=`${(index+1)/steps.length*100}%`;
    q('#tutorial-next').disabled=true;q('#tutorial-back').disabled=true;
    q('#tutorial-next').textContent='Preparing step...';
    try {
      await steps[index].enter?.();
      if(document.querySelector(steps[index].target)?.closest('#advanced-research'))document.querySelector('#advanced-research').open=true;
      if(!dialog.open)return;
      highlighted=document.querySelector(steps[index].target);
      spotlight.hidden=!highlighted;
      highlighted?.scrollIntoView({block:'center',behavior:'instant'});
      q('#tutorial-next').textContent=index===steps.length-1?'Finish tutorial':'Next step';
      position();
      q('#tutorial-next').onclick=()=>index===steps.length-1?close():show(index+1);
    } catch(e) {
      q('#tutorial-error').textContent=e.message;q('#tutorial-error').hidden=false;
      q('#tutorial-next').textContent='Retry step';q('#tutorial-next').onclick=()=>show(index);
    } finally {
      busy=false;q('#tutorial-next').disabled=false;q('#tutorial-back').disabled=index===0;
      if(dialog.open)q('#tutorial-next').focus({preventScroll:true});
    }
  }
  function close() {
    if(busy){q('#tutorial-error').textContent='Please wait for the current analysis to finish, then close the tutorial.';q('#tutorial-error').hidden=false;return;}
    dialog.close();spotlight.hidden=true;highlighted=null;
    document.body.classList.remove('tutorial-reserved');document.body.style.removeProperty('--tutorial-reserve');
    if(snapshot){
      $('#source').value=snapshot.source;$('#filename').textContent=snapshot.filename;$('#sample').value=snapshot.sample;
      result=snapshot.result;analyzedSource=snapshot.analyzedSource;
      document.querySelectorAll('[data-limit]').forEach(i=>i.value=snapshot.thresholds[i.dataset.limit]);
      $('.settings').open=snapshot.settings;document.querySelector('#advanced-research').open=snapshot.advanced;
      for(const [selector,html] of Object.entries(snapshot.html))document.querySelector(selector).innerHTML=html;
      $('#error').textContent=snapshot.error;$('#error').hidden=snapshot.errorHidden;
      lines();page(snapshot.page);currentTab=snapshot.tab;
      document.querySelectorAll('[data-tab]').forEach(b=>b.classList.toggle('active',b.dataset.tab===currentTab));
      if(result)render();else $('#result-content').innerHTML=snapshot.empty;
      $('#source').setSelectionRange(snapshot.selection[0],snapshot.selection[1]);$('#source').scrollTop=snapshot.editorScroll;$('#numbers').scrollTop=snapshot.editorScroll;
      window.scrollTo(0,snapshot.scroll);snapshot=null;
    }
    launch.focus({preventScroll:true});toast('Tutorial closed. Your workspace has been restored.');
  }
  function start(complete=false){
    if($('#analyze').disabled){toast('Wait for the analysis to finish before starting the tutorial.');return;}
    const thresholds={};document.querySelectorAll('[data-limit]').forEach(i=>thresholds[i.dataset.limit]=i.value);
    const html={};['.stats','#finding-count','#duration','#tokens','#symbols','#predictions','#model-status','#model-description'].forEach(s=>html[s]=document.querySelector(s).innerHTML);
    snapshot={advanced:document.querySelector('#advanced-research').open,source:$('#source').value,filename:$('#filename').textContent,sample:$('#sample').value,result,analyzedSource,thresholds,html,settings:$('.settings').open,error:$('#error').textContent,errorHidden:$('#error').hidden,page:document.querySelector('nav button.active').dataset.page,tab:currentTab,empty:$('#result-content').innerHTML,scroll:scrollY,editorScroll:$('#source').scrollTop,selection:[$('#source').selectionStart,$('#source').selectionEnd]};
    document.querySelectorAll('[data-limit]').forEach(i=>i.value=limits[i.dataset.limit]);
    steps=complete?allSteps:[0,1,3,4,5,6,9,10,16,22].map(i=>allSteps[i]);
    dialog.showModal();show(0);
  };
  launch.onclick=()=>start(false);
  document.querySelector('#quick-tour-help').onclick=()=>start(false);
  document.querySelector('#full-tutorial').onclick=()=>start(true);
  q('#tutorial-close').onclick=close;q('#tutorial-back').onclick=()=>show(index-1);
  dialog.addEventListener('cancel',e=>{e.preventDefault();close()});
  window.addEventListener('resize',position);window.addEventListener('scroll',position,true);
})();
