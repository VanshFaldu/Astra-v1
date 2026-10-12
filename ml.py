"""Dependency-free decision tree for independently labeled function metrics."""
import csv, json, random, argparse, io, math
from pathlib import Path
from analyzer import FEATURES, DEFAULTS

def train(rows, depth=0):
    p = sum(r['label'] for r in rows)/len(rows)
    leaf = {'probability':p,'samples':len(rows)}
    if depth>=5 or len(rows)<6 or p in (0,1): return leaf
    best = None
    for feature in FEATURES:
        values = sorted(set(r[feature] for r in rows))
        for a,b in zip(values,values[1:]):
            threshold=(a+b)/2
            left=[r for r in rows if r[feature]<=threshold]; right=[r for r in rows if r[feature]>threshold]
            if min(len(left),len(right))<2: continue
            score=sum(len(g)*2*(sum(r['label'] for r in g)/len(g))*(1-sum(r['label'] for r in g)/len(g)) for g in (left,right))/len(rows)
            if best is None or score<best[0]: best=(score,feature,threshold,left,right)
    if best is None or best[0]>=2*p*(1-p): return leaf
    _,feature,threshold,left,right=best
    return {**leaf,'feature':feature,'threshold':threshold,'left':train(left,depth+1),'right':train(right,depth+1)}

def predict(tree,row):
    while 'feature' in tree: tree=tree['left' if row[tree['feature']]<=tree['threshold'] else 'right']
    return round(tree['probability'],4)

def evaluate(labels, decisions):
    tp=sum(y==1 and p for y,p in zip(labels,decisions)); fp=sum(y==0 and p for y,p in zip(labels,decisions))
    fn=sum(y==1 and not p for y,p in zip(labels,decisions)); tn=sum(y==0 and not p for y,p in zip(labels,decisions))
    precision=tp/(tp+fp) if tp+fp else 0; recall=tp/(tp+fn) if tp+fn else 0
    return {'precision':precision,'recall':recall,'f1':2*precision*recall/(precision+recall) if precision+recall else 0,'confusion_matrix':[[tn,fp],[fn,tp]],'positive_support':tp+fn,'negative_support':tn+fp}

def fit_csv(content):
    reader=csv.DictReader(io.StringIO(content.lstrip('\ufeff')))
    required=set(FEATURES+['label','repository','review_rationale'])
    if not required.issubset(reader.fieldnames or []): raise ValueError('Missing columns: '+', '.join(sorted(required-set(reader.fieldnames or []))))
    rows=list(reader)
    if len(rows)<30 or len(rows)>10000: raise ValueError('Provide 30–10,000 independently reviewed functions across at least 5 repositories.')
    data=[]
    for index,r in enumerate(rows,2):
        try:
            values={k:float(r[k]) for k in FEATURES}
            if any(not math.isfinite(v) or v<0 for v in values.values()): raise ValueError()
            if r['label'].strip() not in ('0','1') or not r['repository'].strip() or not r['review_rationale'].strip(): raise ValueError()
            data.append({**values,'label':int(r['label']),'group':r['repository'].strip()})
        except (ValueError,TypeError,AttributeError): raise ValueError(f'Invalid row {index}. Supply nonnegative numeric metrics, label 0/1, repository and review rationale.')
    groups=sorted(set(r['group'] for r in data)); random.Random(42).shuffle(groups)
    if len(groups)<5: raise ValueError('At least 5 repositories required to prevent repository leakage.')
    test_groups=set(groups[:max(1,len(groups)//5)])
    training=[r for r in data if r['group'] not in test_groups]; test=[r for r in data if r['group'] in test_groups]
    if {r['label'] for r in training}!={0,1} or {r['label'] for r in test}!={0,1}: raise ValueError('Both train and held-out repositories need both labels. Add representative data.')
    tree=train(training)
    labels=[r['label'] for r in test]
    rules=[any(r[k]>DEFAULTS[k] for k in ('loc','parameters','nesting','complexity')) for r in test]
    probabilities=[predict(tree,r) for r in test]
    ml=[p>=.5 for p in probabilities]
    # Policy is fixed before evaluation: high model proportion OR rule plus moderate model proportion.
    hybrid=[p>=.7 or (rule and p>=.4) for p,rule in zip(probabilities,rules)]
    evaluation={'train_samples':len(training),'test_samples':len(test),'held_out_repositories':sorted(test_groups),'variants':{'rules':evaluate(labels,rules),'ml':evaluate(labels,ml),'hybrid':evaluate(labels,hybrid)},'hybrid_policy':'p >= 0.7 OR (structural rule AND p >= 0.4)','rule_features':['loc','parameters','nesting','complexity']}
    return {'tree':tree,'features':FEATURES,'evaluation':evaluation,'target':'function requires review','dataset_kind':'user-supplied labels; independence must be verified by reviewers'}

def save_model(model):
    path=Path(__file__).parent/'model.json'
    temporary=path.with_suffix('.tmp')
    temporary.write_text(json.dumps(model,indent=2),encoding='utf-8'); temporary.replace(path)

def main():
    parser=argparse.ArgumentParser(); parser.add_argument('csv'); args=parser.parse_args()
    try: model=fit_csv(Path(args.csv).read_text(encoding='utf-8-sig')); save_model(model)
    except ValueError as e: raise SystemExit(str(e))
    print(json.dumps(model['evaluation'],indent=2))
if __name__=='__main__': main()
