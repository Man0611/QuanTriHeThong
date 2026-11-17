"""Reproducible pedagogical simulator for drift-aware IoT alerts.
No paper's official algorithm, no empirical scientific claim. Python >=3.9, stdlib only.
Run: python driftcost_demo.py
"""
from collections import deque
from statistics import median
import random, math, csv, sys, platform

SEED=20261116

def make_stream(n=1600,seed=SEED):
    rng=random.Random(seed); rows=[]
    for t in range(n):
        shift = 0 if t < 550 else (1.4 if t < 1100 else 0.5)
        y=int((t in range(350,362)) or (t in range(850,865)) or (t in range(1350,1370)))
        x=rng.gauss(shift,0.8)+(3.8 if y else 0)
        rows.append((t,x,y))
    return rows

def robust_med_mad(a):
    m=median(a); return m, max(1.4826*median([abs(v-m) for v in a]),0.1)

def conformal_p(score,sorted_cal):
    # two-sided anomaly score larger is stranger; finite rank p-value
    from bisect import bisect_left
    return (1+len(sorted_cal)-bisect_left(sorted_cal,score))/(len(sorted_cal)+1)

def evaluate(rows, alarms, fp=2.,miss=20.,delay=0.2):
    # episodes contiguous positive labels; one matching alarm within each episode
    intervals=[]; start=None
    for t,_,y in rows:
        if y and start is None: start=t
        if not y and start is not None: intervals.append((start,t-1));start=None
    if start is not None:intervals.append((start,rows[-1][0]))
    false_alarms=sum(1 for t in alarms if rows[t][2]==0)
    detected=[]; delays=[]
    for a,b in intervals:
        matched=[t for t in alarms if a<=t<=b]
        detected.append(bool(matched))
        if matched: delays.append(min(matched)-a)
    missed=len(intervals)-sum(detected)
    cost=fp*false_alarms+miss*missed+delay*sum(delays)
    return dict(alerts=len(alarms),false_alerts=false_alarms,episodes=len(intervals),missed_events=missed,mean_delay=round(sum(delays)/len(delays),3) if delays else 'NA',cost=round(cost,2))

def detector(rows,adaptive=True,budget=4,window=100,refractory=12,alpha=0.025):
    # first 200 points: only normal, frozen calibration and initial reference
    warm=[x for _,x,_ in rows[:200]]
    mu,scale=robust_med_mad(warm)
    cal=sorted([abs(x-mu)/scale for x in warm]); recent=deque(maxlen=60)
    alarm_times=deque(); alarms=[]; last_alert=-10**9; drift_hits=0; freeze_until=-1
    for t,x,y in rows[200:]:
        # NOTE: ground truth y is NEVER used in the online decision.
        score=abs(x-mu)/scale; p=conformal_p(score,cal)
        while alarm_times and alarm_times[0]<=t-window:alarm_times.popleft()
        if p<=alpha and t-last_alert>=refractory and (budget is None or len(alarm_times)<budget):
            alarms.append(t); alarm_times.append(t);last_alert=t
        # drift monitoring on recent observations; trim potential anomalies by score
        if score<2.5: recent.append(x)
        if adaptive and len(recent)==60 and t>=freeze_until:
            med=median(recent)
            if abs(med-mu)>0.75*scale:
                drift_hits+=1
                # re-centering after sustained shift; no true labels used
                mu,scale=robust_med_mad(list(recent))
                cal=sorted([abs(v-mu)/scale for v in recent])
                freeze_until=t+60
    return alarms,drift_hits

def main():
    rows=make_stream()
    for label,adaptive,budget in [('Static/no budget',False,None),('Adaptive/no budget',True,None),('Adaptive/budget',True,4)]:
        alarms,drifts=detector(rows,adaptive=adaptive,budget=budget)
        print(label, 'drift_updates=',drifts, evaluate(rows,alarms))
    with open('demo_stream.csv','w',newline='',encoding='utf-8') as f:
        w=csv.writer(f);w.writerow(['t','sensor','anomaly_label']);w.writerows(rows)
    print('Python:',sys.version.split()[0],'Platform:',platform.platform(),'seed:',SEED)
    print('Output: demo_stream.csv. Illustrative synthetic scenario, not benchmark evidence.')

if __name__=='__main__': main()
