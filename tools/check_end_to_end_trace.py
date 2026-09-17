#!/usr/bin/env python3
import argparse,json,re
from pathlib import Path
STAGES=('intake','planning-review','discussion','specification-review','reconciliation','implementation','quality','handoff')
def fail(m): raise SystemExit('AWG-END-TO-END-FAIL: '+m)
def check(v):
 if v.get('schema_version')!=1 or not re.fullmatch(r'AR-[0-9]{4}',str(v.get('task_ref'))): fail('invalid identity')
 rev=v.get('task_revision'); events=v.get('events')
 if not isinstance(rev,int) or rev<1 or not isinstance(events,list) or [e.get('stage') for e in events if isinstance(e,dict)]!=list(STAGES): fail('mandatory stage order is incomplete')
 for e in events:
  if not isinstance(e,dict) or e.get('task_revision')!=rev or not e.get('evidence_ref') or e.get('evidence_class') not in {'intake','oracle','formal-check','implementation','quality','handoff'}: fail('invalid event evidence')
 if v.get('unresolved_guidance') is True: fail('unresolved guidance blocks handoff')
 if v.get('status')!='handoff': fail('trace is not handed off')
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('fixture',type=Path); args=ap.parse_args();
 try: v=json.loads(args.fixture.read_text())
 except Exception as e: fail(str(e))
 check(v); print('AWG-END-TO-END-PASS: '+str(args.fixture))
if __name__=='__main__': main()
