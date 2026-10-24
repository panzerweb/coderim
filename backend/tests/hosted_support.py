import base64
import threading
import uuid


class FakeProvider:
    """Deterministic fake: interprets fixture markers, never executes submitted source."""
    poll_seconds = .001
    def __init__(self, repository):
        self.expected = {c.stdin: c.expected for p in repository.published() for c in p.cases}
        self.records = {}
        self.calls = []
        self.lock = threading.Lock()
        self.gate = threading.Event(); self.gate.set()
        self.started = threading.Event()
        self.ready = True
        self.maximum = 0
        self.outstanding = set()
        self.status = {key: {'id':key,'label':label,'editor_language':editor,'available':True,'reason':'','starter':''}
            for key,label,editor in [('python','Python 3','python'),('javascript','JavaScript','javascript'),('java','Java','java'),('cpp','C++17','cpp')]}

    def refresh(self, repository):
        return self.ready

    def public(self): return list(self.status.values())
    def close(self): pass

    def create(self, language, code, stdin, limits):
        self.started.set()
        if code == 'DELIVERY_UNKNOWN': raise TimeoutError('simulated lost response')
        token = str(uuid.uuid4())
        with self.lock:
            self.calls.append((language,code,stdin))
            self.records[token] = (code,stdin,0)
            self.outstanding.add(token); self.maximum=max(self.maximum,len(self.outstanding))
        return token

    def result(self, token):
        if not self.gate.wait(.02): return {'status':{'id':1}}
        with self.lock:
            code,stdin,polls = self.records[token]
            self.records[token]=(code,stdin,polls+1)
            if polls==0:return {'status':{'id':2}}
            self.outstanding.discard(token)
        if code == 'INFRA':return {'status':{'id':13},'message':'private provider error'}
        status = {'COMPILE':6,'CRASH':7,'TIMEOUT':5}.get(code,3)
        stdout = self.expected.get(stdin, stdin) if code == 'ACCEPT' else stdin if code=='ECHO' else 'WRONG\n'
        if code == 'OUTPUT':stdout='x'*(2*1024*1024+1)
        enc=lambda text:base64.b64encode(text.encode()).decode()
        return {'status':{'id':status},'stdout':enc(stdout),'stderr':None,
            'compile_output':enc('syntax issue') if status==6 else None,'time':'0.01','exit_code':0 if status==3 else 1}
