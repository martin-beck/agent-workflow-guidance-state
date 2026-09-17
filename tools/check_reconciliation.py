#!/usr/bin/env python3
import argparse,json,re
from pathlib import Path
SHA=re.compile(r'^sha256:[0-9a-f]{64}$')
ARTIFACTS=('work_plan','design_document','specifications','dependency_graph','affected_ars')
def fail(message): raise SystemExit('AWG-RECONCILIATION-FAIL: '+message)
def artifact(v,name,rev):
    if not isinstance(v,dict) or any(k not in v for k in ('ref','version','digest','task_revision')): fail(name+' incomplete')
    if not isinstance(v['ref'],str) or not v['ref'] or v['ref'].startswith('/') or '..' in v['ref'].split('/'): fail(name+' unsafe')
    if not isinstance(v['version'],int) or v['version']<1 or not SHA.fullmatch(v['digest']): fail(name+' invalid version/digest')
    if v['task_revision']!=rev: fail(name+' stale')
def check(v):
    if v.get('schema_version')!=1 or not re.fullmatch(r'AR-[0-9]{4}',str(v.get('task_ref'))): fail('invalid identity')
    rev=v.get('task_revision')
    if not isinstance(rev,int) or rev<1: fail('invalid task revision')
    for side in ('before','after'):
        group=v.get(side)
        if not isinstance(group,dict): fail('missing '+side)
        for key in ARTIFACTS: artifact(group.get(key),side+'.'+key,rev)
    changes=v.get('changes')
    if not isinstance(changes,list) or not changes: fail('impact analysis required')
    for change in changes:
        if not isinstance(change,dict) or not all(change.get(k) for k in ('scope','impact','provenance')) or 'affected_ars' not in change: fail('incomplete impact analysis')
        if not isinstance(change['affected_ars'],list) or not all(re.fullmatch(r'AR-[0-9]{4}',str(x)) for x in change['affected_ars']): fail('invalid affected AR')
    contradictions=v.get('contradictions',[])
    if not isinstance(contradictions,list) or any(not isinstance(c,dict) or c.get('status') not in {'resolved','unresolved'} for c in contradictions): fail('malformed contradiction')
    unresolved=[c for c in contradictions if c['status']=='unresolved']
    disposition=v.get('disposition')
    if disposition not in {'reconciled','reopen','discussion-required'}: fail('invalid disposition')
    if disposition=='reconciled' and unresolved: fail('unresolved contradiction silently continued')
    if disposition in {'reopen','discussion-required'} and not v.get('affected_ars'): fail('reopen must name affected ARs')
    if disposition=='reconciled' and v.get('discussion_required'): fail('new discussion required but reconciliation continued')
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('fixture',type=Path); args=ap.parse_args()
    try: v=json.loads(args.fixture.read_text())
    except Exception as e: fail(str(e))
    check(v); print('AWG-RECONCILIATION-PASS: '+str(args.fixture))
if __name__=='__main__': main()
