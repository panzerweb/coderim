"""Managed compilation/execution. No language probes or subprocesses on the API host."""
import base64
import hashlib
import hmac
import json
import math
import os
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from datetime import datetime, timezone
import httpx
from .judge import assessment, normalize
from .problems import Case


class ProviderError(Exception):
    pass


class Judge0Client:
    def __init__(self, runtime, secret, client=None, url=None, headers=None, language_ids=None, poll_seconds=1):
        self.url = (url or os.getenv('JUDGE0_URL', '')).rstrip('/')
        self.headers = headers if headers is not None else json.loads(os.getenv('JUDGE0_HEADERS_JSON', '{}'))
        self.language_ids = language_ids if language_ids is not None else json.loads(os.getenv('JUDGE0_LANGUAGE_IDS_JSON', '{}'))
        self.http = client or httpx.Client(timeout=httpx.Timeout(20, connect=5), follow_redirects=False)
        self.poll_seconds, self.secret = poll_seconds, secret.encode()
        self.receipt = Path(runtime) / 'provider-verification.json'
        self.hold_file = Path(runtime) / 'provider-hold.json'
        self.status = {key: {'id': key, 'label': label, 'editor_language': editor, 'starter': '',
            'available': False, 'reason': 'Managed judge configuration or verification is required'}
            for key, label, editor in [('python', 'Python 3', 'python'), ('javascript', 'JavaScript', 'javascript'),
                ('cpp', 'C++17', 'cpp'), ('java', 'Java', 'java')]}
        self.configured = bool(self.url and self.headers and self.language_ids)

    def configuration_fingerprint(self):
        return hashlib.sha256(json.dumps({'url': self.url, 'languages': self.language_ids,
            'headers_hash': hashlib.sha256(json.dumps(self.headers, sort_keys=True).encode()).hexdigest()}, sort_keys=True).encode()).hexdigest()

    @staticmethod
    def problem_fingerprint(problem):
        # Snapshot packaging may rename private files; hash judging semantics,
        # not the authoring paths used to load the package.
        validated = type(problem.meta).model_validate(problem.meta.model_dump())
        metadata = validated.model_dump(exclude={'statement_file','samples_file','tests_manifest','starters'})
        digest = hashlib.sha256(json.dumps(metadata, sort_keys=True).encode())
        for case in problem.cases:
            digest.update(json.dumps({'id':case.id,'category':case.category,'requirements':case.requirements,'visible':case.visible},sort_keys=True).encode())
            digest.update(case.stdin.encode()); digest.update(b'\0'); digest.update(case.expected.encode()); digest.update(b'\0')
        return digest.hexdigest()

    def fingerprint(self, repository):
        return {'configuration': self.configuration_fingerprint(),
            'problems': sorted(self.problem_fingerprint(p) for p in repository.published())}

    def refresh(self, repository):
        ready = False
        try:
            data = json.loads(self.receipt.read_text(encoding='utf-8'))
            signature = data.pop('signature')
            expected = hmac.new(self.secret, json.dumps(data, sort_keys=True).encode(), hashlib.sha256).hexdigest()
            current = self.fingerprint(repository)
            approved = data['fingerprint']
            ready = hmac.compare_digest(signature, expected) and approved['configuration'] == current['configuration'] and bool(current['problems']) and set(current['problems']) <= set(approved['problems'])
        except (OSError, ValueError, KeyError, TypeError):
            pass
        ready = ready and not self.hold_file.exists()
        for key, item in self.status.items():
            item['available'] = ready and key in self.language_ids
            item['reason'] = '' if item['available'] else 'Complete the opt-in managed-provider verification before opening a contest'
        return ready

    def hold(self):
        # An unresolved remote execution must not be followed by fresh work.
        # This survives restarts and prevents orphaned executions exceeding the
        # configured provider concurrency after an outage/ambiguous delivery.
        self.hold_file.parent.mkdir(parents=True, exist_ok=True)
        self.hold_file.write_text('{"reason":"Reconcile outstanding executions with the provider before re-verifying."}', encoding='utf-8')

    def public(self):
        return [dict(item) for item in self.status.values()]

    def supports(self, language):
        return language in self.language_ids

    def request(self, method, path, **kwargs):
        if not self.url.startswith('https://'):
            raise ProviderError('Managed judge must use HTTPS')
        request_started = time.monotonic()
        try:
            # Bound the response before decoding JSON/base64, including error responses.
            with self.http.stream(method, self.url + path, headers=self.headers, **kwargs) as response:
                if response.status_code == 429:
                    raise ProviderError('Managed judge quota or rate limit reached')
                if response.status_code >= 400:
                    raise ProviderError('Managed judge rejected the request')
                body = bytearray()
                for chunk in response.iter_bytes():
                    if time.monotonic() - request_started > 20:
                        raise ProviderError('Managed judge response timed out')
                    if len(body) + len(chunk) > 8 * 1024 * 1024:
                        raise ProviderError('Managed judge response exceeded its bound')
                    body.extend(chunk)
                return json.loads(body)
        except ProviderError:
            raise
        except (httpx.HTTPError, ValueError, TypeError):
            raise ProviderError('Managed judge transport or response failure') from None

    def check_configuration(self):
        languages = self.request('GET', '/languages')
        config = self.request('GET', '/config_info')
        if not isinstance(languages, list) or not isinstance(config, dict):
            raise ProviderError('Invalid managed judge capabilities')
        ids = {item.get('id') for item in languages if isinstance(item, dict)}
        if not self.language_ids or any(type(v) is not int or v not in ids for v in self.language_ids.values()):
            raise ProviderError('Configure valid approved language IDs')
        for key in self.language_ids:
            if key not in self.status:
                raise ProviderError('Unapproved language mapping')
        if config.get('enable_network') is not False and config.get('allow_enable_network') is not True:
            raise ProviderError('Provider cannot guarantee network-disabled execution')
        if float(config.get('max_cpu_time_limit', 0)) < 5 or int(config.get('max_memory_limit', 0)) < 262144 or int(config.get('max_max_file_size', 0)) < 2048:
            raise ProviderError('Provider limits do not support the current problem packages')
        return {'languages': languages, 'configuration': config}

    def create(self, language, code, stdin, limits):
        if self.hold_file.exists():
            raise ProviderError('Managed provider requires operator reconciliation')
        def encoded(value):
            return base64.b64encode(value.encode()).decode()
        payload = {'source_code': encoded(code), 'stdin': encoded(stdin), 'language_id': self.language_ids[language],
            'enable_network': False, 'number_of_runs': 1, 'redirect_stderr_to_stdout': False,
            'cpu_time_limit': limits.time_ms / 1000, 'wall_time_limit': limits.time_ms / 1000,
            'memory_limit': limits.memory_mb * 1024, 'max_processes_and_or_threads': 64,
            'max_file_size': max(2048, (limits.stdout_bytes + 1023) // 1024)}
        try:
            result = self.request('POST', '/submissions?base64_encoded=true&wait=false', json=payload)
        except Exception:
            self.hold()
            raise
        token = result.get('token') if isinstance(result, dict) else None
        if not isinstance(token, str) or not token or len(token) > 128:
            self.hold()
            raise ProviderError('Managed judge did not return an execution token')
        return token

    def result(self, token):
        from urllib.parse import quote
        return self.request('GET', '/submissions/' + quote(token, safe='') + '?base64_encoded=true&fields=status,stdout,stderr,compile_output,time,exit_code,message')

    def close(self):
        self.http.close()


class RemoteJudge:
    def __init__(self, provider, storage, budget=600, concurrency=2):
        self.provider, self.storage, self.budget = provider, storage, budget
        if concurrency not in (1, 2) or budget <= 0:
            raise ValueError('Managed concurrency must be 1 or 2 and job budget must be positive')
        self.concurrency = concurrency

    def run(self, problem, language, code, mode='submit', stdin='', progress=lambda state: None, cancel=None, attempt_id=None):
        started = time.monotonic()
        budget = self.budget
        if attempt_id:
            persisted = self.storage.remote_job(attempt_id, budget)
            started -= max(0, (datetime.now(timezone.utc) - datetime.fromisoformat(persisted['started_at'])).total_seconds())
            budget = persisted['budget_seconds']
        official = mode == 'submit'
        cases = problem.cases if official else tuple(c for c in problem.cases if c.visible)
        if mode == 'custom':
            cases = (Case('custom', stdin, '', '', (), True),)
        result = {'mode': mode, 'verdict': 'Judge Error', 'attempted': 0, 'passed': 0, 'total': len(cases),
            'duration_ms': 0, 'cases': [], 'assessment': None, 'diagnostics': '', 'incomplete_reason': None}
        outcomes = []
        limits = problem.meta.limits

        def case_result(case):
            if cancel and cancel.is_set():
                raise InterruptedError
            if time.monotonic() - started >= budget:
                raise ProviderError('Managed judging job budget exhausted')
            record = self.storage.provider_case(attempt_id, case.id) if attempt_id else None
            if record and record['state'] == 'completed':
                return json.loads(record['result_json'])
            if record and record['state'] in ('creating', 'delivery_unknown'):
                raise ProviderError('Provider delivery is uncertain; it was not resubmitted')
            token = record['token'] if record else None
            if not token:
                if attempt_id:
                    self.storage.save_provider_case(attempt_id, case.id, 'creating')
                try:
                    token = self.provider.create(language, code, case.stdin, limits)
                except Exception:
                    if attempt_id:
                        self.storage.save_provider_case(attempt_id, case.id, 'delivery_unknown')
                    raise ProviderError('Provider delivery could not be reconciled') from None
                if attempt_id:
                    self.storage.save_provider_case(attempt_id, case.id, 'running', token=token)
            while True:
                if cancel and cancel.is_set():
                    raise InterruptedError
                if time.monotonic() - started >= budget:
                    raise ProviderError('Managed judging job budget exhausted')
                response = self.provider.result(token)
                status = response.get('status', {}).get('id') if isinstance(response, dict) else None
                if status in (1, 2):
                    if cancel:
                        cancel.wait(self.provider.poll_seconds)
                    else:
                        time.sleep(self.provider.poll_seconds)
                    continue
                if status not in range(3, 13) or status == 13:
                    raise ProviderError('Managed judge infrastructure failed')
                def decoded(key):
                    value = response.get(key)
                    if value is None:
                        return ''
                    if not isinstance(value, str):
                        raise ProviderError('Invalid provider output encoding')
                    try:
                        return base64.b64decode(value, validate=True).decode('utf-8', errors='replace')
                    except (ValueError, TypeError):
                        raise ProviderError('Invalid provider output encoding') from None
                stdout, stderr, compile_output = decoded('stdout'), decoded('stderr'), decoded('compile_output')
                verdict = 'Compile Error' if status == 6 else 'Time Limit Exceeded' if status == 5 else 'Output Limit Exceeded' if status == 8 else 'OK' if status == 3 else 'Runtime Error'
                if len(stdout.encode()) > limits.stdout_bytes or len(stderr.encode()) > limits.stderr_bytes:
                    verdict = 'Output Limit Exceeded'
                if verdict == 'OK':
                    verdict = 'Completed' if mode == 'custom' else ('Accepted' if normalize(stdout, problem.meta.checker) == normalize(case.expected, problem.meta.checker) else 'Wrong Answer')
                try:
                    duration = float(response.get('time') or 0) * 1000
                    if not math.isfinite(duration) or duration < 0:
                        raise ValueError
                except (ValueError, TypeError):
                    raise ProviderError('Invalid provider timing') from None
                entry = {'id': case.id, 'verdict': verdict, 'duration_ms': duration,
                    'diagnostics': compile_output.encode()[:limits.stderr_bytes].decode(errors='ignore') if verdict == 'Compile Error' else ''}
                if case.visible:
                    entry.update(stdout=stdout.encode()[:limits.stdout_bytes].decode(errors='ignore'), stderr=stderr.encode()[:limits.stderr_bytes].decode(errors='ignore'),
                        exit_code=response.get('exit_code'), input=case.stdin,
                        expected_output=None if mode == 'custom' else case.expected)
                if attempt_id:
                    self.storage.save_provider_case(attempt_id, case.id, 'completed', token=token, result=entry)
                return entry

        try:
            progress('running')
            # Run the first case alone: a compile failure needs no further paid executions.
            ordered = [case_result(cases[0])]
            if ordered[0]['verdict'] != 'Compile Error':
                with ThreadPoolExecutor(max_workers=self.concurrency) as pool:
                    # Submit in bounded waves; do not launch new work after a failed wave.
                    for offset in range(1, len(cases), self.concurrency):
                        futures = [pool.submit(case_result, c) for c in cases[offset:offset + self.concurrency]]
                        ordered.extend(f.result() for f in futures)
            outcomes = ordered
            compile_failed = any(c['verdict'] == 'Compile Error' for c in outcomes)
            result['diagnostics'] = outcomes[0].get('diagnostics', '')
            result['attempted'] = 0 if compile_failed else len(outcomes)
            result['passed'] = 0 if compile_failed else sum(c['verdict'] == 'Accepted' for c in outcomes)
            result['verdict'] = next((c['verdict'] for c in outcomes if c['verdict'] not in ('Accepted', 'Completed')), 'Completed' if mode == 'custom' else 'Accepted')
            result['cases'] = [{k: v for k, v in c.items() if k != 'diagnostics'} for c in outcomes if 'stdout' in c]
            if official:
                result['assessment'] = assessment(problem, [] if compile_failed else outcomes, True, compile_failed)
        except InterruptedError:
            # Persisted tokens/results are retained; HostedJobs requeues this attempt on restart.
            raise
        except Exception:
            if hasattr(self.provider, 'hold'):
                self.provider.hold()
            result['incomplete_reason'] = 'Managed judging failed, reached a limit, or has uncertain delivery. No automatic local execution or blind provider retry was performed.'
            if attempt_id:
                outcomes = []
                for case in cases:
                    saved = self.storage.provider_case(attempt_id, case.id)
                    if saved and saved['state'] == 'completed':
                        outcomes.append(json.loads(saved['result_json']))
            result['attempted'] = len(outcomes)
            result['passed'] = sum(c['verdict'] == 'Accepted' for c in outcomes)
            if official:
                result['assessment'] = assessment(problem, outcomes, False)
        result['duration_ms'] = round((time.monotonic() - started) * 1000, 2)
        return result
