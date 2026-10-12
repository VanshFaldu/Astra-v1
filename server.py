from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
import json
from analyzer import analyze

ROOT=Path(__file__).parent
class Handler(SimpleHTTPRequestHandler):
    def __init__(self,*args,**kwargs): super().__init__(*args,directory=str(ROOT/'web'),**kwargs)
    def end_headers(self):
        self.send_header('Cache-Control', 'no-store, max-age=0')
        super().end_headers()
    def guess_type(self, path):
        mime = super().guess_type(path)
        if mime in ('text/html', 'text/css', 'text/javascript', 'application/javascript'):
            return mime + '; charset=utf-8'
        return mime
    def respond(self,result,code=200):
        body=json.dumps(result).encode(); self.send_response(code); self.send_header('Content-Type','application/json'); self.send_header('Cache-Control','no-store'); self.send_header('Content-Length',str(len(body))); self.end_headers(); self.wfile.write(body)
    def do_GET(self):
        if self.path=='/api/model':
            path=ROOT/'model.json'
            try:
                model=json.loads(path.read_text(encoding='utf-8')) if path.exists() else None
                self.respond({'status':'trained' if model else 'not_trained','evaluation':model.get('evaluation') if model else None,'dataset_kind':model.get('dataset_kind') if model else None,'provenance':model.get('provenance') if model else None})
            except (ValueError,OSError): self.respond({'error':'Model file cannot be read.'},500)
        else: super().do_GET()
    def do_POST(self):
        if self.path not in ('/api/analyze','/api/train'): self.send_error(404); return
        try:
            size=int(self.headers.get('Content-Length','0'))
            maximum=2000000 if self.path=='/api/train' else 200000
            if size<1 or size>maximum: raise ValueError(f'Request size must be 1–{maximum} bytes.')
            data=json.loads(self.rfile.read(size))
            if not isinstance(data,dict): raise ValueError('Request must be a JSON object.')
            if self.path=='/api/train':
                from ml import fit_csv, save_model
                content=data.get('csv')
                if not isinstance(content,str): raise ValueError('Supply dataset CSV text.')
                result=fit_csv(content); save_model(result); result={'status':'trained','evaluation':result['evaluation']}
            else:
                source=data.get('source','')
                if not isinstance(source,str) or not source.strip(): raise ValueError('Enter Python source to analyze.')
                if data.get('thresholds') is not None and not isinstance(data['thresholds'],dict): raise ValueError('Thresholds must be an object.')
                result=analyze(source,data.get('thresholds'))
            code=200
        except SyntaxError as e: result={'error':e.msg,'line':e.lineno,'column':e.offset}; code=422
        except (ValueError,TypeError,RecursionError) as e: result={'error':str(e)}; code=400
        except OSError: result={'error':'Local model could not be saved or read.'}; code=500
        self.respond(result,code)
if __name__=='__main__':
    print('ASTRA ready at http://127.0.0.1:8000',flush=True)
    ThreadingHTTPServer(('127.0.0.1',8000),Handler).serve_forever()
