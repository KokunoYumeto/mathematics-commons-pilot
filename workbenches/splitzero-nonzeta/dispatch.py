#!/usr/bin/env python3
"""Generate offline job specifications. Does not launch agents or make network calls."""
from pathlib import Path
from collections import Counter
import csv
import hashlib
import json

ROOT = Path(__file__).resolve().parent
ROLES = {
    'S': 'Recover the exact primary statement, variants, coefficients, parameters, rights and current status. Record a bounded literature search and exact source identities. Route solved or unresolved-claim scopes to review rather than new-solution attempts.',
    'M': 'Construct the actual source, support diagram, relations, target and morphism on generators. Prove well-definedness and commuting identities. Supply both maps for every equivalence. Retain kernel/cokernel and any unfinished comparison.',
    'E': 'Run one bounded exact experiment on the accepted map. Preserve indexed states, integral coefficients, nilpotents and original norms. Use an independently implemented checker for decisive certificates. Record the exact finite parameter window and failures.',
    'P': 'Attempt one precise advance in the original scope. Supply a complete written argument for the bounded result or identify the exact failed step. Do not replace the target, assume an unproved isomorphism or offer a conditional theorem as a completed result.',
    'R': 'Independently review source semantics, morphisms, experiments and argument. Seek dropped torsion, nilpotents, boundary terms, realization assumptions and unproved uniformity. Model agreement is not verification.',
    'CS': 'Verify the published control theorem or resolve the exact source-status conflict. Preserve all parameter and statement differences.',
    'CE': 'Reproduce the control with exact calculations and an independent checker. Do not claim novelty or label a solved result open.',
    'AS': 'Recover the original problem, complete claimed proof, dependencies, exact formal endpoint and build revision. Keep CLAIMED_UNVERIFIED until independent review.',
    'AP': 'Audit all decisive proof steps and replay available formal sources with axiom checks. Separately verify the map from the formal endpoint to the original statement and every nonformal dependency.',
    'AR': 'Independently review the claim audit and produce an evidence-backed status delta. No automatic publication or contact with maintainers.',
}

def build():
    data = json.loads((ROOT/'intake.json').read_text(encoding='utf-8'))
    with (ROOT/'seeds.psv').open(encoding='utf-8', newline='') as stream:
        rows = list(csv.DictReader(stream, delimiter='|'))
    if len({r['id'] for r in rows}) != len(rows):
        raise ValueError('Duplicate problem ID')
    jobs = []
    for r in rows:
        if None in r or not all(r.values()) or r['source'] not in data['sources']:
            raise ValueError('Malformed or unsourced record: '+str(r))
        seq = ['CS','CE'] if r['tier']=='CONTROL' else ['AS','AP','AR'] if r['tier']=='REVIEW' else ['S','M','E','P','R']
        if r['tier'] not in ('A','B','C','CONTROL','REVIEW'):
            raise ValueError('Unknown tier')
        if r['tier'] in ('A','B','C') and r['status']!='OPEN_IN_SOURCE':
            raise ValueError('Active target has unresolved routing')
        previous = []
        for role in seq:
            jid = r['id']+'-'+role
            jobs.append({'job_id':jid,'problem_id':r['id'],'batch':r['batch'],'tier':r['tier'],'role':role,
                         'state':'READY_FOR_INTAKE' if not previous else 'DEPENDENCY_GATED',
                         'depends_on':previous.copy(),'dispatch_authorized':False,
                         'source':data['sources'][r['source']],'locator':r['locator'],
                         'source_status':r['status'],'canonical_status':'NOT_INDEPENDENTLY_ADMITTED',
                         'task':ROLES[role],'mathematical_entry':r['first_task'],'remaining_obligation':r['blocker'],
                         'gate':'Accept prior source/mathematical evidence, not merely job completion.',
                         'bound':'One certified variant and explicit finite window; default cap 5000 finite objects. Stop with a checkpoint at the cap. No unapproved paid compute.'})
            previous.append(jid)
    for family in data['source_family_coverage']:
        jobs.append({'job_id':'INTAKE-'+family['id'],'problem_id':None,'batch':'INTAKE','tier':'INTAKE','role':'SOURCE_FAMILY',
                     'state':'READY_FOR_INTAKE','depends_on':[],'dispatch_authorized':False,'source':family['url'],
                     'task':family['next'],'actual_previous_coverage':family['read'],
                     'bound':'Create the complete accessible locator index; deeply certify at most 25 numbered statements in this run. Return the exact unreviewed denominator and a continuation cursor. Index scanning is not statement-audit completion.'})
    seen = set()
    for j in jobs:
        if j['job_id'] in seen or not set(j['depends_on']).issubset(seen):
            raise ValueError('Duplicate or invalid dependency: '+j['job_id'])
        seen.add(j['job_id'])
    tiers = dict(Counter(r['tier'] for r in rows))
    summary = {'date':data['date'],'records':len(rows),'tiers':tiers,'source_families':len(data['source_family_coverage']),
               'job_specifications':len(jobs),'ready_intake_jobs':sum(j['state']=='READY_FOR_INTAKE' for j in jobs),
               'dependency_gated_jobs':sum(j['state']=='DEPENDENCY_GATED' for j in jobs),'agents_launched':0,
               'new_resolutions_claimed':0,'seed_sha256':hashlib.sha256((ROOT/'seeds.psv').read_bytes()).hexdigest()}
    expected = {'A':11,'B':19,'C':11,'CONTROL':10,'REVIEW':2}
    if len(rows)!=53 or tiers!=expected or len(jobs)!=245 or summary['ready_intake_jobs']!=67:
        raise ValueError('Unexpected snapshot counts; review and version the manifest rather than ignoring drift')
    return rows,jobs,summary

def main():
    rows,jobs,summary = build()
    out = ROOT/'generated'; packets=out/'packets'; packets.mkdir(parents=True,exist_ok=True)
    expected = {j['job_id']+'.md' for j in jobs}
    stale = {p.name for p in packets.glob('*.md')} - expected
    if stale:
        raise ValueError('Stale packets require review before removal: '+str(sorted(stale)))
    (out/'problems.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (out/'jobs.jsonl').write_text(''.join(json.dumps(j,ensure_ascii=False,sort_keys=True)+'\n' for j in jobs),encoding='utf-8')
    (out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
    for j in jobs:
        text = '# '+j['job_id']+'\n\nRead README.md, METHOD.md and intake.json first. This is a specification, not an execution receipt.\n\n'
        text += '```json\n'+json.dumps(j,ensure_ascii=False,indent=2)+'\n```\n\n'
        text += 'Hand back source_receipt.json, map_and_argument.md, checks.json, status_delta.json and continuation.json, plus exact code/certificates used. Preserve input identities, mathematical scope, actual tests, failures and unresolved obligations. No private transcripts, automatic publication, paid compute or downstream launches. A mathematical claim stays CLAIMED_UNVERIFIED until independent review.\n'
        (packets/(j['job_id']+'.md')).write_text(text,encoding='utf-8')
    print(json.dumps(summary,indent=2))

if __name__=='__main__':
    main()
