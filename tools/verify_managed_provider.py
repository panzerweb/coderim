"""Opt-in paid provider checks; never run automatically in tests or startup."""
import argparse
import base64
import hashlib
import hmac
import json
import os
import sys
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'backend'))
from app.models import Limits
from app.problems import Repository
from app.remote_judge import Judge0Client, RemoteJudge
from app.storage import Storage


def verify(runtime, confirm=False, provider_drained=False):
    if not confirm:
        raise SystemExit('This sends source and test inputs to the provider and consumes executions. Pass --confirm-live to opt in.')
    secret = os.getenv('RELAY_SESSION_SECRET', '')
    if len(secret) < 32:
        raise SystemExit('Set the persistent RELAY_SESSION_SECRET first')
    repo = Repository(ROOT / 'problems')
    if repo.errors:
        raise SystemExit('Validate all packages first')
    provider = Judge0Client(runtime, secret)
    if provider.hold_file.exists():
        if not provider_drained:
            provider.close()
            raise SystemExit('Provider is on hold. Reconcile/cancel outstanding work at the provider, then add --confirm-provider-drained to re-verify.')
        provider.hold_file.unlink()
    capabilities = provider.check_configuration()
    approved_names = {str(item['id']): item.get('name','') for item in capabilities['languages'] if item.get('id') in provider.language_ids.values()}
    print('Selected provider language versions: ' + json.dumps(approved_names), flush=True)
    languages = provider.language_ids
    if not {'python', 'javascript', 'java', 'cpp'} <= languages.keys():
        raise SystemExit('Configure all four approved contest languages')
    store = Storage(runtime / 'history.sqlite3', resume_owned=True)
    judge = RemoteJudge(provider, store)
    count = sum(len(p.cases) for p in repo.published()) * len(languages) + 5
    print(f'Verifying approximately {count} managed executions; budget and quota must support this.', flush=True)
    filenames = {'python': 'reference.py', 'javascript': 'reference.js', 'java': 'Main.java', 'cpp': 'reference.cpp'}
    try:
        for p in repo.published():
            for language in languages:
                path = ROOT / 'problems' / p.meta.id / 'author' / filenames[language]
                # The original formatter has only a Python author reference. The
                # verified public demo solution supplies its JS/Java reference.
                if not path.exists() and language in ('javascript', 'java'):
                    name = 'main.js' if language == 'javascript' else 'Main.java'
                    path = ROOT / 'examples/judge-checks' / language / 'pass-all' / name
                if not path.exists() and p.meta.id == 'broken-code-formatter' and language == 'cpp':
                    code = r'''#include <iostream>
#include <string>
#include <vector>
int main(){std::string s;std::getline(std::cin,s);std::vector<char>a;char q=0;bool e=false,ok=true;
for(char c:s){if(q){if(e)e=false;else if(c=='\\')e=true;else if(c==q)q=0;}
else if(c=='\''||c=='"')q=c;else if(c=='('||c=='['||c=='{')a.push_back(c);
else if(c==')'||c==']'||c=='}'){char t=c==')'?'(':c==']'?'[':'{';if(a.empty()||a.back()!=t){ok=false;break;}a.pop_back();}}
std::cout<<(ok&&a.empty()&&!q&&!e?"VALID":"INVALID")<<'\n';}'''
                else:
                    code = path.read_text(encoding='utf-8')
                result = judge.run(p, language, code)
                if result['verdict'] != 'Accepted':
                    raise RuntimeError(f'Provider failed {p.meta.id}/{language}: {result["verdict"]}')
                print(f'PASS {p.meta.id}/{language}', flush=True)
        p = next(iter(repo.published()))
        p = replace(p, meta=p.meta.model_copy(update={'limits': Limits(time_ms=5000, stdin_bytes=8388608, stdout_bytes=2097152)}))
        probes = [
            ("import sys\nprint(len(sys.stdin.buffer.read()))", 'x' * 8388608, lambda r: r['verdict'] == 'Completed' and r['cases'][0]['stdout'].strip() == '8388608'),
            ("import sys\nsys.stdout.write('x'*2097152)", '', lambda r: r['verdict'] == 'Completed' and len(r['cases'][0]['stdout']) == 2097152),
            ("import socket\ns=socket.socket();s.settimeout(2)\ntry:\n s.connect(('example.com',80));print('NETWORK_ALLOWED')\nexcept OSError:\n print('NETWORK_BLOCKED')", '', lambda r: r['verdict'] == 'Completed' and r['cases'][0]['stdout'].strip() == 'NETWORK_BLOCKED'),
            ("x=bytearray(512*1024*1024)\nprint(len(x))", '', lambda r: r['verdict'] == 'Runtime Error'),
            ((ROOT / 'examples/judge-checks/python/pass-all/main.py').read_text(), '()\n', lambda r: r['verdict'] == 'Completed' and r['cases'][0]['stdout'].strip() == 'VALID'),
        ]
        for source, stdin, check in probes:
            result = judge.run(p, 'python', source, mode='custom', stdin=stdin)
            if not check(result):
                raise RuntimeError('Provider failed size, runtime compatibility, memory, or network isolation check')
        data = {'fingerprint': provider.fingerprint(repo), 'language_versions': approved_names, 'verified_at': datetime.now(timezone.utc).isoformat()}
        data['signature'] = hmac.new(secret.encode(), json.dumps(data, sort_keys=True).encode(), hashlib.sha256).hexdigest()
        provider.receipt.parent.mkdir(parents=True, exist_ok=True)
        temporary = provider.receipt.with_suffix('.tmp')
        temporary.write_text(json.dumps(data), encoding='utf-8'); temporary.replace(provider.receipt)
        print('Managed provider verified. Managed code execution is enabled for this content/configuration.')
    finally:
        provider.close(); store.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--runtime', type=Path, default=Path(os.getenv('RELAY_RUNTIME', ROOT / '.runtime')))
    parser.add_argument('--confirm-live', action='store_true')
    parser.add_argument('--confirm-provider-drained', action='store_true', help='Confirm the operator has reconciled/cancelled every outstanding provider execution')
    args = parser.parse_args()
    verify(args.runtime, args.confirm_live, args.confirm_provider_drained)
