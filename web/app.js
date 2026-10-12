const $=s=>document.querySelector(s);
const examples={smelly:`def calculate_checkout(items, customer, discount, tax_rate, shipping, currency, region):
    total = 0
    unused_receipt = "draft"
    for item in items:
        if item["available"]:
            if item["quantity"] > 0:
                if customer["active"]:
                    if region == "domestic":
                        total += item["price"] * item["quantity"]
                    else:
                        total += item["price"] * item["quantity"] * 1.15
                else:
                    total += item["price"] * 1.25
            else:
                print("Invalid quantity")
        else:
            print("Unavailable item")
    if discount > 0 and customer["active"]:
        total = total * (1 - discount)
    if total > 500:
        shipping = 0
    if region == "international" or currency != "INR":
        shipping += 250
    if tax_rate > 0:
        total += total * tax_rate
    return round(total + shipping, 2)
`,clean:`FREE_SHIPPING_LIMIT = 500

def item_total(items):
    return sum(item["price"] * item["quantity"] for item in items)

def shipping_cost(subtotal, standard_cost):
    if subtotal >= FREE_SHIPPING_LIMIT:
        return 0
    return standard_cost

def checkout(items, tax_rate, shipping):
    subtotal = item_total(items)
    tax = subtotal * tax_rate
    delivery = shipping_cost(subtotal, shipping)
    return round(subtotal + tax + delivery, 2)
`,syntax:`def checkout(items)
    return sum(items)
`};
let result=null,currentTab='findings',analyzedSource='';
const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
function lines(){const n=$('#source').value.split('\n').length;$('#numbers').textContent=Array.from({length:n},(_,i)=>i+1).join('\n');$('#line-count').textContent=`${n} lines · Python · UTF-8`;$('#numbers').scrollTop=$('#source').scrollTop}
$('#source').value=examples.smelly;lines();
$('#source').addEventListener('input',()=>{lines();if(result){$('#duration').textContent='Source changed · rerun';}});$('#source').addEventListener('scroll',()=>$('#numbers').scrollTop=$('#source').scrollTop);
$('#source').addEventListener('keydown',e=>{if(e.key==='Tab'){e.preventDefault();const el=e.target;el.setRangeText('    ',el.selectionStart,el.selectionEnd,'end');lines()}if((e.ctrlKey||e.metaKey)&&e.key==='Enter'){e.preventDefault();run()}});
$('#sample').onchange=()=>{$('#source').value=examples[$('#sample').value];$('#filename').textContent=$('#sample').value+'.py';lines();$('#duration').textContent='Source changed · rerun'};
$('#file').onchange=async e=>{const f=e.target.files[0];if(!f)return;if(f.size>180000){toast('Please select a file smaller than 180 KB.');return}$('#source').value=await f.text();$('#filename').textContent=f.name;lines();$('#duration').textContent='Source changed · rerun'};
const limits={loc:40,parameters:5,nesting:3,complexity:10,methods:10};const names={loc:'Method LOC',parameters:'Parameters',nesting:'Nesting depth',complexity:'Complexity',methods:'Class methods'};
$('#thresholds').innerHTML=Object.entries(limits).map(([k,v])=>`<label>${names[k]}<input type="number" min="1" max="1000" value="${v}" data-limit="${k}"></label>`).join('');
document.querySelectorAll('[data-page]').forEach(b=>b.onclick=()=>{document.querySelectorAll('.page').forEach(p=>p.hidden=p.id!==b.dataset.page);document.querySelectorAll('[data-page]').forEach(x=>x.classList.toggle('active',x===b));$('#page-title').textContent=b.querySelector('span').textContent;window.scrollTo(0,0)});
document.querySelectorAll('[data-tab]').forEach(b=>b.onclick=()=>{currentTab=b.dataset.tab;document.querySelectorAll('[data-tab]').forEach(x=>x.classList.toggle('active',x===b));render()});
function table(headers,rows){return `<div class="table-wrap"><table><thead><tr>${headers.map(h=>`<th>${esc(h)}</th>`).join('')}</tr></thead><tbody>${rows.map(r=>`<tr>${r.map(v=>`<td>${esc(v)}</td>`).join('')}</tr>`).join('')}</tbody></table></div>`}
function tree(n){return n.children.length?`<details><summary>${esc(n.label)} ${n.line?`<small>L${n.line}</small>`:''}</summary>${n.children.map(tree).join('')}</details>`:`<details><summary>${esc(n.label)} ${n.line?`<small>L${n.line}</small>`:''}</summary></details>`}
function render(){if(!result)return;
 const el=$('#result-content');
 if(currentTab==='metrics'){el.innerHTML=result.functions.length?table(['Function','LOC','Params','Depth','CC','Calls'],result.functions.map(f=>[f.name,f.loc,f.parameters,f.nesting,f.complexity,f.calls])):'<div class="empty"><h3>No functions in this source</h3><p>Module-level code is still parsed and inspected.</p></div>';return}
 if(currentTab==='tree'){el.innerHTML=`<div class="filter"><span>${result.summary.nodes} nodes · expand to explore</span><span>Depth display capped at 14</span></div><div class="tree">${tree(result.ast)}</div>`;el.querySelector('details').open=true;return}
 el.innerHTML=`<div class="filter"><span>Source-mapped diagnostics</span><select id="severity" aria-label="Filter severity"><option value="all">All severities</option><option>high</option><option>medium</option><option>low</option></select></div><div id="finding-list"></div>`;
 const show=()=>{const fs=result.findings.filter(f=>$('#severity').value==='all'||f.severity===$('#severity').value);$('#finding-list').innerHTML=fs.length?fs.map(f=>`<details class="finding ${f.severity}"><summary><div><h3>${esc(f.type)}</h3><span class="location">${esc(f.scope)} · line ${f.line} · ${esc(f.method)}</span></div><span class="severity">${f.severity}</span></summary><p>${esc(f.evidence)}</p><p class="suggestion">↳ ${esc(f.suggestion)}</p><button class="jump" data-line="${f.line}">View source →</button></details>`).join(''):'<div class="empty"><div class="empty-icon">✓</div><h3>No findings for this selection</h3><p>Passing these checks does not prove code quality.</p></div>';document.querySelectorAll('[data-line]').forEach(b=>b.onclick=()=>{if($('#source').value!==analyzedSource){toast('Source changed. Analyze again before jumping to a finding.');return}const l=Number(b.dataset.line),parts=$('#source').value.split('\n'),start=parts.slice(0,l-1).join('\n').length+(l>1?1:0);$('#source').focus();$('#source').setSelectionRange(start,start+parts[l-1].length);$('#source').scrollTop=Math.max(0,(l-4)*22);$('#numbers').scrollTop=$('#source').scrollTop})};$('#severity').onchange=show;show();
}
async function run(){const button=$('#analyze');if(button.disabled)return;button.disabled=true;button.textContent='Analyzing…';$('#error').hidden=true;const start=performance.now();try{const thresholds={};document.querySelectorAll('[data-limit]').forEach(i=>thresholds[i.dataset.limit]=Number(i.value));const source=$('#source').value;const response=await fetch('/api/analyze',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({source,thresholds})});const data=await response.json();if(!response.ok)throw Error(`${data.line?'Line '+data.line+': ':''}${data.error}`);result=data;analyzedSource=source;document.querySelectorAll('.pending-stat').forEach(el=>el.classList.remove('pending-stat'));$('#s-issues').textContent=data.summary.findings;$('#s-functions').textContent=data.summary.functions;$('#s-nodes').textContent=data.summary.nodes;$('#issue-note').textContent=`${data.summary.severity.high||0} high · ${data.summary.severity.medium||0} medium · ${data.summary.severity.low||0} low`;$('#finding-count').textContent=data.summary.findings+' findings';$('#duration').textContent=Math.round(performance.now()-start)+' ms';$('#ml-note').textContent=data.ml_status==='trained'?'Decision tree predictions available':'ML awaits a reviewed dataset';$('#tokens').innerHTML=table(['Token','Value','Line'],data.tokens.map(t=>[t.type,t.value,t.line]));$('#symbols').innerHTML=data.symbols.length?table(['Binding','Scope','Line','Read'],data.symbols.map(s=>[s.name,s.scope,s.line,s.used?'Yes':'No'])):'No local assignments found.';$('#model-status').textContent=data.ml_status==='trained'?'Trained decision tree loaded':'No trained model loaded';$('#model-description').textContent=data.ml_status==='trained'?'Predictions below come from your locally trained model. Review model.json for held-out evaluation results.':'Rule-based analysis is fully available. We do not present threshold-generated labels as independent AI evidence.';$('#predictions').innerHTML=data.predictions.length?table(['Function','Review proportion','ML decision'],data.predictions.map(p=>[p.name,(p.probability*100).toFixed(1)+'%',p.probability>=.5?'Review':'Below cutoff'])):'';render();if(typeof loadEvaluation==='function')loadEvaluation();toast('Analysis complete. Explore the evidence.')}catch(e){$('#error').textContent=e.message;$('#error').hidden=false;toast('Analysis could not complete. Check the source or server.')}finally{button.disabled=false;button.innerHTML='Analyze code <span>↗</span>'}}
$('#analyze').onclick=run;
function toast(message){$('#toast').textContent=message;$('#toast').classList.add('visible');setTimeout(()=>$('#toast').classList.remove('visible'),3500)}
function download(name,content,type){const url=URL.createObjectURL(new Blob([content],{type}));const a=document.createElement('a');a.href=url;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000)}
$('#export').onclick=()=>{if(!result){toast('Analyze code before exporting.');return}download('astra-analysis-report.html',`<!doctype html><html><meta charset="utf-8"><title>ASTRA Analysis Report</title><style>body{max-width:1000px;margin:50px auto;font:14px/1.8 system-ui;color:#273431}table{border-collapse:collapse;width:100%}td,th{border:1px solid #ddd;padding:10px}pre{padding:20px;background:#f4f5f6;white-space:pre-wrap}h1{border-bottom:3px solid #96ba73}@media print{body{margin:20px}}</style><h1>ASTRA · Code Analysis Report</h1><p>Generated ${esc(new Date().toLocaleString())} · ${esc($('#filename').textContent)}</p><p>${result.summary.findings} findings · ${result.summary.functions} functions · ${result.summary.nodes} AST nodes · ML: ${esc(result.ml_status)}</p><h2>Thresholds</h2><p>${esc(JSON.stringify(result.thresholds))}</p><h2>Findings</h2>${table(['Smell','Line','Severity','Evidence','Suggestion'],result.findings.map(f=>[f.type,f.line,f.severity,f.evidence,f.suggestion]))}<h2>Function metrics</h2>${table(['Function','LOC','Parameters','Nesting','Complexity'],result.functions.map(f=>[f.name,f.loc,f.parameters,f.nesting,f.complexity]))}<h2>Analyzed source</h2><pre>${esc(analyzedSource)}</pre><h2>Interpretation limits</h2><p>Heuristic single-file analysis. Findings are review prompts, not proven bugs. Unused-local checks are lexical; duplication uses exact AST bodies. No benchmark performance is claimed without independent evaluation. Use your browser's Print command to save this report as PDF.</p></html>`,'text/html');toast('Report downloaded. Print it to save as PDF.')};
$('#dataset').onclick=()=>{if(!result||!result.functions.length){toast('Analyze a file with functions first.');return}const keys=['loc','statements','parameters','nesting','complexity','calls','loops','branches'];download('function-metrics.csv','repository,function,line,'+keys.join(',')+',label,review_rationale\n'+result.functions.map(f=>['',f.name,f.line,...keys.map(k=>f[k]),'',''].map(x=>'"'+String(x).replace(/"/g,'""')+'"').join(',')).join('\n'),'text/csv');toast('Add repository, independent labels and rationale before training.')};
