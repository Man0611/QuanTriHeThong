"""Independent teaching demo: drift detection and alert episodes.
NOT code from any cited paper. Python 3.10+ standard library only.
Run: python demo_drift_cost_iot.py
"""
import math
import random
from collections import deque

random.seed(7)
# normal regime at 25C, changed benign regime at 30C, attacks are spikes.
T=400
attack_intervals=[(140,145),(320,325)]
def is_attack(t): return any(a<=t<b for a,b in attack_intervals)
values=[]
for t in range(T):
    baseline=25.0 if t<220 else 30.0
    x=baseline+random.gauss(0,0.65)
    if is_attack(t): x+=12
    values.append(x)

BUDGET=5
ref=deque(values[:60],maxlen=60)
recent=deque(maxlen=20)
alerts=[]; warnings=[]; drift_events=[]
active=False; cooldown=0
for t,x in enumerate(values[60:],60):
    mu=sum(ref)/len(ref)
    v=sum((a-mu)**2 for a in ref)/len(ref)
    sd=max(math.sqrt(v),0.35)
    score=abs(x-mu)/sd
    # Alarm decision precedes model update (prequential).
    raw_warning=score>5
    # Episode starts only once, and only if outside cooldown.
    if cooldown>0: cooldown-=1
    if raw_warning and not active and cooldown==0:
        alerts.append(t); active=True
    if not raw_warning and active:
        active=False; cooldown=4
    warnings.append(int(raw_warning))
    recent.append(x)
    # Simple didactic drift test: sustained shift in recent window,
    # exclude extreme anomalous points from baseline adaptation.
    if len(recent)==20:
        valid=[v for v in recent if abs(v-mu)<8]
        if len(valid)>=15:
            rmu=sum(valid)/len(valid)
            if abs(rmu-mu)>2:
                drift_events.append(t)
                ref.clear();ref.extend(valid)
                recent.clear()
                continue
    if score<3: ref.append(x)  # quarantine suspected anomalies

# match alerts to attack intervals; earliest valid episode per event
matched=set()
for t in alerts:
    for j,(a,b) in enumerate(attack_intervals):
        if a<=t<b: matched.add(j)
false_episodes=sum(not is_attack(t) for t in alerts)
missed=len(attack_intervals)-len(matched)
FP_COST=1;FN_COST=15;DRIFT_UPDATE_COST=0.2
cost=FP_COST*false_episodes+FN_COST*missed+DRIFT_UPDATE_COST*len(drift_events)
print('Educational demo: NOT paper reproduction')
print('Alert episode starts:',alerts)
print('Drift triggers:',drift_events)
print('Detected events:',len(matched),'/',len(attack_intervals))
print('False episodes:',false_episodes,'Missed events:',missed)
print('Time in warning:',round(sum(warnings)/len(warnings),3))
print('Budget episodes allowed:',BUDGET,'Violation:',len(alerts)>BUDGET)
print('Illustrative cost:',round(cost,2))
