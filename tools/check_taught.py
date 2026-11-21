# 「教える前に問わない」チェック：戦闘・確認で出る問題の知識が、出題より前のステージの説明で扱われているか
import json, sys
w=json.load(open('data/world.json')); Q=[q for q in json.load(open('data/questions.json'))['questions'] if q['pool']!='mock']  # 模試専用問題は冒険では出ない
order=['V0']+[k for k in w['stages']]  # 世界データのステージ順
taught_topics=set(); problems=[]
topic_of_stage={}
for q in Q:
    topic_of_stage.setdefault((q['town'],q['stage']),set()).add(q['topic'])
seen=set()
TOWNS=['S1','S2','S3','S4','K1','K2','K3','K4','E1','E2','E3','E4','Y1','Y2','Y3','Y4','Z1','Z2','Z3']
key=lambda s:(TOWNS.index(s.split('-')[0]) if s.split('-')[0] in TOWNS else 99, 9 if s.endswith('boss') else int(s.split('-')[1]))
for sid in sorted(w['stages'],key=key):
    S=w['stages'][sid]
    town,n=sid.split('-')
    if n!='boss': taught_topics |= topic_of_stage.get((town,int(n)),set()) - {'identify'}
    pool=[x for x in Q if x.get('enemy')==S['enemy']]
    for x in pool:
        if x['topic']!='identify' and x['topic'] not in taught_topics: problems.append((sid,x['id'],x['topic']))
    if S.get('boss'):
        for x in Q:
            if x['town']==town and x['kind']=='mcq5' and x['topic'] not in taught_topics: problems.append((sid,x['id'],x['topic']))
print('教える前に問う問題：', len(problems)); [print(' ',p) for p in problems[:30]]
sys.exit(1 if problems else 0)
