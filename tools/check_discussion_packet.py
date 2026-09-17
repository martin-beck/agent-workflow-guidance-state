#!/usr/bin/env python3
import argparse,json,re
from pathlib import Path
def fail(message): raise SystemExit('AWG-DISCUSSION-PACKET-FAIL: '+message)
def check(v):
    if v.get('schema_version')!=1 or not re.fullmatch(r'AR-[0-9]{4}',str(v.get('task_ref'))): fail('invalid identity')
    rev=v.get('task_revision')
    if not isinstance(rev,int) or rev<1: fail('invalid revision')
    points=v.get('points')
    if not isinstance(points,list) or not points: fail('points required')
    ids=[]
    for p in points:
        if not isinstance(p,dict) or not isinstance(p.get('id'),str) or p['id'] in ids: fail('point identity invalid'); ids.append(p.get('id'))
        for key in ('alternatives','evidence_gaps','implications','formal_refs','confidence'):
            if not p.get(key): fail('point '+str(p.get('id'))+' missing '+key)
        if not isinstance(p['alternatives'],list) or len(p['alternatives'])<2: fail('ranked alternatives required')
        if not all(isinstance(p['confidence'].get(k), (int,float)) for k in ('applicability','outcome','downstream')): fail('confidence dimensions required')
        if p.get('task_revision')!=rev: fail('stale point revision')
        response=p.get('response')
        if not isinstance(response,dict) or response.get('disposition') not in {'select','reject-all','clarify','unresolved'}: fail('explicit response required')
        added=response.get('added_proposal')
        if added is not None and not isinstance(added,dict): fail('added proposal malformed')
        if added is not None and not added.get('evaluated'): fail('added proposal must be evaluated')
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('fixture',type=Path); args=ap.parse_args();
    try: value=json.loads(args.fixture.read_text())
    except Exception as e: fail(str(e))
    check(value); print('AWG-DISCUSSION-PACKET-PASS: '+str(args.fixture))
if __name__=='__main__': main()
