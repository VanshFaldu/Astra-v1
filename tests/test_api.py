import json
import threading
import unittest
from urllib.request import urlopen, Request
from urllib.error import HTTPError
from http.server import ThreadingHTTPServer
from server import Handler

class APITests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
        cls.base=f'http://127.0.0.1:{cls.server.server_port}'
        cls.thread=threading.Thread(target=cls.server.serve_forever,daemon=True)
        cls.thread.start()
    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown(); cls.server.server_close(); cls.thread.join()
    def test_page(self):
        with urlopen(self.base) as response:
            self.assertIn(b'ASTRA',response.read())
    def test_analysis(self):
        request=Request(self.base+'/api/analyze',data=json.dumps({'source':'def f(a,b,c,d,e,f):\n    unused = 42\n    return a\n'}).encode(),headers={'Content-Type':'application/json'})
        with urlopen(request) as response:
            data=json.load(response)
        self.assertEqual(data['summary']['functions'],1)
        self.assertEqual({f['type'] for f in data['findings']},{'Unused local','Long parameter list'})
    def test_model_status(self):
        with urlopen(self.base+'/api/model') as response:
            self.assertIn(json.load(response)['status'],('trained','not_trained'))
    def test_training_validation(self):
        request=Request(self.base+'/api/train',data=b'{"csv":"label\\n1\\n"}',headers={'Content-Type':'application/json'})
        with self.assertRaises(HTTPError) as caught: urlopen(request)
        self.assertEqual(caught.exception.code,400)
        self.assertIn('Missing columns',json.load(caught.exception)['error'])
    def test_syntax_diagnostic(self):
        request=Request(self.base+'/api/analyze',data=b'{"source":"def f("}',headers={'Content-Type':'application/json'})
        with self.assertRaises(HTTPError) as caught: urlopen(request)
        self.assertEqual(caught.exception.code,422)
        self.assertEqual(json.load(caught.exception)['line'],1)
