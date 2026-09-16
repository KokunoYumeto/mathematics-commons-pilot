#!/usr/bin/env python3
"""Build a dated, source-bound queue. No network calls or agent execution."""
from __future__ import annotations
from collections import Counter
from pathlib import Path
import csv
import hashlib
import json

ROOT = Path(__file__).resolve().parent
ROLES = {
    'S': 'Certify the exact original statement and current source status. Read the attached prior-work and status receipts first. Preserve all coefficient, parameter and variant differences.',
    'M': 'Extend the displayed original-source morphisms. Prove well-definedness, commuting identities and both inverse laws for equivalences. Keep original kernels, boundaries, torsion and nilpotents.',
    'E': 'Extend the bounded exact calculations beyond the attached certified window. Preserve source objects and executable certificates; use an independently implemented checker.',
    'P': 'Prove one precise advance in the original scope with a complete argument. Otherwise identify the exact failed step. No conditional theorem or altered target counts as a completed result.',
    'R': 'Independently audit the statement, maps, computation and argument. Check realization, signs, torsion, boundary terms and uniformity. Model agreement is not verification.',
    'CS': 'Review the matching published theorem and its exact scope, using the attached status history and existing reproduction. Do not reopen a resolved statement.',
    'CE': 'Independently replay or extend the published-result control. Identify the actual maps and finite scope; do not claim novelty.',
    'AS': 'Read the pinned claim and original statement. Continue from the recorded source-reading boundary, rather than merely finding the claim again.',
    'AP': 'Audit the complete claimed proof and exact formal dependency closure. Replay trust-zero/axiom checks where available and verify the original-statement comparison.',
    'AR': 'Independently review the claim audit and produce an evidence-backed status delta. A finite test alone cannot establish the full claim.',
}

def load(path):
    return json.loads((ROOT/path).read_text(encoding='utf-8'))

def build():
    intake = load('intake.json')
    delta = load('review/catalog/dispatch-delta.json')
    status = load('review/catalog/status-delta.json')
    progress = load('review/catalog/progress.json')
    coverage = load('review/catalog/coverage-delta.json')
    seed = ROOT/'seeds.psv'
    digest = hashlib.sha256(seed.read_bytes()).hexdigest()
    if digest != delta['baseline_seed_sha256']:
        raise ValueError('Baseline seed drift: reconcile and version the delta first')
    with seed.open(encoding='utf-8', newline='') as stream:
        rows = list(csv.DictReader(stream, delimiter='|'))
    rows.extend(delta['added_records'])
    by_id = {r['id']:r for r in rows}
    if len(by_id) != len(rows):
        raise ValueError('Duplicate problem identifier')
    changes = {r['id']:r for r in status['rows']}
    if len(changes) != len(status['rows']) or not set(changes).issubset(by_id):
        raise ValueError('Invalid status-delta identifiers')
    if not set(progress).issubset(by_id):
        raise ValueError('Orphan prior-work entry')
    for key, change in changes.items():
        row = by_id[key]
        row['baseline_status'] = row['status']
        row['status'], row['tier'] = change['status'], change['route']
    jobs = []
    for row in rows:
        if None in row or not all(row.values()) or row['source'] not in intake['sources']:
            raise ValueError('Malformed or unsourced record: '+str(row))
        tier = row['tier']
        if tier not in ('A','B','C','CONTROL','REVIEW'):
            raise ValueError('Unknown tier')
        if tier in ('A','B','C') and row['status'] != 'OPEN_IN_SOURCE':
            raise ValueError('Active target has unresolved status routing')
        prior = progress.get(row['id'])
        if prior:
            if not (ROOT/prior['artifact'].split('#',1)[0]).is_file():
                raise ValueError('Missing prior-work artifact')
            row['baseline_first_task'] = row['first_task']
            row['first_task'] = prior['next']
        roles = ['CS','CE'] if tier=='CONTROL' else ['AS','AP','AR'] if tier=='REVIEW' else ['S','M','E','P','R']
        previous = []
        for role in roles:
            jid = row['id']+'-'+role
            jobs.append({'job_id':jid,'problem_id':row['id'],'tier':tier,'batch':row['batch'],
                         'role':role,'generation':delta['generation'],
                         'state':'READY_FOR_INTAKE' if not previous else 'DEPENDENCY_GATED',
                         'depends_on':previous.copy(),'dispatch_authorized':False,
                         'source':intake['sources'][row['source']],'locator':row['locator'],
                         'source_status':row['status'],'canonical_status':'NOT_INDEPENDENTLY_ADMITTED',
                         'task':ROLES[role],'mathematical_entry':row['first_task'],
                         'remaining_obligation':row['blocker'],'prior_work':prior,
                         'status_receipt':changes.get(row['id']),
                         'gate':'Accept actual prior source/mathematical evidence, not a completed job flag.',
                         'bound':'One certified variant and an explicit finite window; default cap 5000 newly inspected finite objects. Preserve existing larger certificates. Return a checkpoint at the cap. No paid compute or downstream launches.'})
            previous.append(jid)
    for family in intake['source_family_coverage']:
        jobs.append({'job_id':'INTAKE-'+family['id'],'problem_id':None,'batch':'INTAKE',
                     'tier':'INTAKE','role':'SOURCE_FAMILY','generation':delta['generation'],
                     'state':'READY_FOR_INTAKE','depends_on':[],'dispatch_authorized':False,
                     'source':family['url'],'task':family['next'],
                     'baseline_coverage':family['read'],'current_coverage_delta':coverage,
                     'bound':'Read current coverage first; its dated continuation supersedes old cursors. Certify at most 25 further numbered statements, preserve the unreviewed denominator and return a cursor. Index scanning is not statement-audit completion.'})
    seen = set()
    for job in jobs:
        if job['job_id'] in seen or not set(job['depends_on']).issubset(seen):
            raise ValueError('Invalid dependency order')
        seen.add(job['job_id'])
    summary = {'generation':delta['generation'],'records':len(rows),
               'tiers':dict(Counter(r['tier'] for r in rows)),
               'source_families':len(intake['source_family_coverage']),
               'job_specifications':len(jobs),
               'ready_intake_jobs':sum(j['state']=='READY_FOR_INTAKE' for j in jobs),
               'dependency_gated_jobs':sum(j['state']=='DEPENDENCY_GATED' for j in jobs),
               'agents_launched':0,'new_full_open_problem_resolutions':0,
               'baseline_seed_sha256':digest}
    for key, value in delta['expected'].items():
        if summary[key] != value:
            raise ValueError('Versioned snapshot count mismatch: '+key)
    return rows,jobs,summary

def main():
    rows,jobs,summary = build()
    out = ROOT/'generated'/summary['generation']
    packets = out/'packets'
    packets.mkdir(parents=True,exist_ok=True)
    expected = {j['job_id']+'.md' for j in jobs}
    stale = {p.name for p in packets.glob('*.md')}-expected
    if stale:
        raise ValueError('Stale packets require an explicit generation transition')
    for name,obj in [('problems.json',rows),('summary.json',summary)]:
        (out/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (out/'jobs.jsonl').write_text(''.join(json.dumps(j,ensure_ascii=False,sort_keys=True)+'\n' for j in jobs),encoding='utf-8')
    for job in jobs:
        text = '# '+job['job_id']+'\n\nRead README.md, METHOD.md and review/PROGRESS.md first. This specification records no execution.\n\n'
        text += '```json\n'+json.dumps(job,ensure_ascii=False,indent=2)+'\n```\n\n'
        text += 'Return source_receipt.json, map_and_argument.md, checks.json, status_delta.json and continuation.json plus executable certificates. Preserve exact inputs, failures and reading boundaries. No private transcripts, automatic publication or downstream agent launch. New claims remain CLAIMED_UNVERIFIED pending independent review.\n'
        (packets/(job['job_id']+'.md')).write_text(text,encoding='utf-8')
    (ROOT/'generated'/'CURRENT.json').write_text(json.dumps({'generation':summary['generation'],'summary':summary['generation']+'/summary.json'},indent=2)+'\n',encoding='utf-8')
    print(json.dumps(summary,indent=2))

if __name__=='__main__':
    main()
