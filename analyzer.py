"""AST-based static analysis. Submitted code is parsed, never executed."""
import ast
import io
import tokenize
import hashlib
from collections import Counter

FEATURES = ['loc', 'statements', 'parameters', 'nesting', 'complexity', 'calls', 'loops', 'branches']
DEFAULTS = {'loc': 40, 'parameters': 5, 'nesting': 3, 'complexity': 10, 'methods': 10}

class LocalVisitor(ast.NodeVisitor):
    def __init__(self):
        self.nodes = []
        self.depth = self.maximum = 0
    def visit_FunctionDef(self, node): pass
    visit_AsyncFunctionDef = visit_FunctionDef
    def visit_ClassDef(self, node): pass
    def generic_visit(self, node):
        self.nodes.append(node)
        nested = isinstance(node, (ast.If, ast.For, ast.AsyncFor, ast.While, ast.Try, ast.With, ast.AsyncWith, ast.Match))
        if nested:
            self.depth += 1
            self.maximum = max(self.maximum, self.depth)
        super().generic_visit(node)
        if nested: self.depth -= 1

def metrics(node):
    visitor = LocalVisitor()
    for child in node.body: visitor.visit(child)
    ns = visitor.nodes
    args = node.args
    params = len(args.posonlyargs) + len(args.args) + len(args.kwonlyargs) + bool(args.vararg) + bool(args.kwarg)
    complexity = 1
    for n in ns:
        if isinstance(n, (ast.If, ast.For, ast.AsyncFor, ast.While, ast.ExceptHandler, ast.IfExp)): complexity += 1
        if isinstance(n, ast.BoolOp): complexity += len(n.values) - 1
        if isinstance(n, ast.comprehension): complexity += 1 + len(n.ifs)
        if isinstance(n, ast.Match): complexity += sum(not (isinstance(c.pattern, ast.MatchAs) and c.pattern.pattern is None and c.guard is None) for c in n.cases)
    return dict(zip(FEATURES, [node.end_lineno-node.lineno+1, sum(isinstance(n, ast.stmt) for n in ns), params, visitor.maximum, complexity, sum(isinstance(n, ast.Call) for n in ns), sum(isinstance(n, (ast.For, ast.AsyncFor, ast.While)) for n in ns), sum(isinstance(n, ast.If) for n in ns)]))

def analyze(source, thresholds=None):
    limits = DEFAULTS.copy()
    if thresholds:
        for k in limits:
            if k in thresholds: limits[k] = max(1, min(1000, int(thresholds[k])))
    tree = ast.parse(source)
    tokens = [{'type': tokenize.tok_name[t.type], 'value': t.string, 'line': t.start[0], 'column': t.start[1]} for t in tokenize.generate_tokens(io.StringIO(source).readline) if t.type not in (tokenize.ENDMARKER, tokenize.ENCODING)]
    findings, functions, symbols = [], [], []
    def flag(kind, node, detail, suggestion, severity='medium', name=None):
        findings.append({'id': len(findings)+1, 'type': kind, 'line': node.lineno, 'end_line': getattr(node, 'end_lineno', node.lineno), 'scope': name or getattr(node, 'name', 'module'), 'severity': severity, 'evidence': detail, 'suggestion': suggestion, 'method': 'AST rule'})
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            m = metrics(node)
            functions.append({'name': node.name, 'line': node.lineno, **m})
            for key, title, suggestion in [('loc','Long method','Extract cohesive operations into smaller named functions.'), ('parameters','Long parameter list','Group related inputs in a dataclass or configuration object.'), ('nesting','Deep nesting','Use guard clauses and extract nested logic.'), ('complexity','High complexity','Separate decisions into focused functions and add branch tests.')]:
                if m[key] > limits[key]: flag(title,node,f'{key}: {m[key]} exceeds threshold {limits[key]}.',suggestion,'high' if key in ('complexity','nesting') else 'medium')
            v = LocalVisitor()
            for child in node.body: v.visit(child)
            assigned = {n.id: n for n in v.nodes if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Store)}
            loaded = {n.id for n in ast.walk(node) if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load)}
            for name, n in assigned.items():
                symbols.append({'name':name,'scope':node.name,'line':n.lineno,'used':name in loaded})
                # Conservative lexical heuristic: closure reads count as use; no control-flow claims.
                if name not in loaded and not name.startswith('_'): flag('Unused local', n, f'Local "{name}" has no lexical read in this function.', 'Remove the binding if its value is unnecessary; preserve calls with side effects.', 'low', node.name)
        if isinstance(node, ast.ClassDef):
            count = sum(isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) for n in node.body)
            if count > limits['methods']: flag('Large class',node,f'{count} methods exceeds threshold {limits["methods"]}.','Split responsibilities into cohesive classes.')
    # Numeric constants in executable expressions; named constant assignments are excluded.
    parents = {c:n for n in ast.walk(tree) for c in ast.iter_child_nodes(n)}
    for n in ast.walk(tree):
        if isinstance(n, ast.Constant) and type(n.value) in (int,float) and abs(n.value) not in (0,1,2):
            parent = parents.get(n)
            assignment = parent if isinstance(parent,(ast.Assign,ast.AnnAssign)) else None
            if assignment and all(isinstance(t,ast.Name) and t.id.isupper() for t in (assignment.targets if isinstance(assignment,ast.Assign) else [assignment.target])): continue
            if isinstance(parent, (ast.BinOp,ast.Compare,ast.Call,ast.UnaryOp)): flag('Magic number',n,f'Numeric literal {n.value} appears in an expression.','Replace unexplained values with descriptive named constants.','low')
    groups = {}
    for n in ast.walk(tree):
        if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and len(n.body)>=3:
            key = hashlib.sha256('|'.join(ast.dump(x,include_attributes=False) for x in n.body).encode()).hexdigest()
            if key in groups: flag('Duplicate implementation',n,f'Body matches {groups[key].name} at line {groups[key].lineno}.','Extract the shared implementation into a reusable function.')
            else: groups[key]=n
    def serialize(n, depth=0):
        label = type(n).__name__
        if hasattr(n,'name'): label += ': '+n.name
        elif isinstance(n,ast.Name): label += ': '+n.id
        return {'label':label,'line':getattr(n,'lineno',None),'children':[serialize(c,depth+1) for c in ast.iter_child_nodes(n)] if depth<14 else []}
    predictions = []
    model_path = __import__('pathlib').Path(__file__).parent/'model.json'
    if model_path.exists():
        from ml import predict
        import json
        model = json.loads(model_path.read_text(encoding='utf-8'))
        predictions = [{'name':f['name'],'line':f['line'],'probability':predict(model['tree'],f)} for f in functions]
    counts = Counter(f['severity'] for f in findings)
    return {'findings': sorted(findings,key=lambda f:f['line']), 'functions':functions,'symbols':symbols,'tokens':tokens,'ast':serialize(tree),'summary':{'lines':len(source.splitlines()),'functions':len(functions),'classes':sum(isinstance(n,ast.ClassDef) for n in ast.walk(tree)),'nodes':sum(1 for _ in ast.walk(tree)), 'tokens':len(tokens),'findings':len(findings),'severity':dict(counts)},'thresholds':limits,'predictions':predictions,'ml_status':'trained' if model_path.exists() else 'not_trained'}
