# 衛生管理者RPGの問題データ（data/questions.json）を作る。Claudeの下書き（review_status=draft）
# 問題文はすべて自作。過去の公表問題は傾向の参考にとどめ、文章は使わない
import json, sys, os, glob
H = os.path.dirname(os.path.abspath(__file__))
DV = '2026.11.22-proto'
SRC = {
    'SEIRI': ('労働生理（試験科目。内容は一般的な生理学の知識）', 'https://www.exam.or.jp/', '試験科目：労働生理'),
    'ANEI12': ('労働安全衛生法（e-Gov法令検索）', 'https://laws.e-gov.go.jp/law/347AC0000000057', '労働安全衛生法 第12条、労働安全衛生法施行令 第4条'),
    'SOKU': ('労働安全衛生規則（e-Gov法令検索）', 'https://laws.e-gov.go.jp/law/347M50002000032', '労働安全衛生規則'),
    'REI': ('労働安全衛生法施行令（e-Gov法令検索）', 'https://laws.e-gov.go.jp/law/347CO0000000318', '労働安全衛生法施行令'),
    'HOU': ('労働安全衛生法（e-Gov法令検索）', 'https://laws.e-gov.go.jp/law/347AC0000000057', '労働安全衛生法'),
    'EXAM': ('衛生管理者試験の案内（安全衛生技術試験協会）', 'https://www.exam.or.jp/', '試験の合格基準（科目ごと40%以上・合計60%以上）'),
}
Q = []
def q(id, kid, topic, stage, kind, question, choices, answer, expl, cexp, hint='', src='SEIRI', enemy=None, pool='practice', town='S1', subject=None, shuffle='all'):
    assert 0 <= answer < len(choices) and len(cexp) == len(choices), id
    assert id not in {x['id'] for x in Q}, id
    t, u, ref = SRC[src]
    subj = subject or {'S': '労働生理', 'K': '関係法令', 'E': '労働衛生', 'Y': '労働衛生（有害）', 'Z': '関係法令（有害）', 'V': '導入'}[town[0]]
    Q.append(dict(id=id, pool=pool, kind=kind, enemy=enemy, mock_set=None, subject=subj, topic=topic,
        knowledge_id=kid, town=town, stage=stage, difficulty=1, question=question, choices=choices,
        answer=answer, shuffle=shuffle, hint=hint, weakness_tag=None, explanation=expl,
        choice_explanations=cexp, source_title=t, source_url=u, legal_reference=ref,
        checked_date='2026-11-22', effective_from=None, drafted_by='Claude', checked_by=None,
        approved_by=None, review_status='draft', data_version=DV))
def m5(id, kid, topic, stage, question, choices, ans, expl, cexp, hint='', src='SEIRI', town='S1', ref=None):
    q(id, kid, topic, stage, 'mcq5', question, choices, ans, expl, cexp, hint, src, town=town)
    if ref: Q[-1]['legal_reference'] = ref
def sit(id, kid, topic, stage, enemy, text, ch, ans, expl, ce, src='SEIRI', town='S1', ref=None):
    q(id, kid, topic, stage, 'situation', text, ch, ans, expl, ce, src=src, enemy=enemy, town=town)
    if ref: Q[-1]['legal_reference'] = ref
def ident(enemy, town, stage, kid, text, ch, ans, expl, ce, src='SEIRI', ref=None):
    q('ID-' + enemy, kid, 'identify', stage, 'situation', text, ch, ans, expl, ce, src=src, enemy=enemy, town=town)
    if ref: Q[-1]['legal_reference'] = ref

for p in sorted(glob.glob(os.path.join(H, 'eq_*.py'))):
    exec(open(p).read())
# 模試専用問題の分野名（topic）は、同じ知識の冒険の問題からもらう
TOPIC = {}
for x in Q:
    if x['pool'] == 'practice' and x['topic'] != 'identify': TOPIC.setdefault(x['knowledge_id'], x['topic'])
for x in Q:
    if x['pool'] == 'mock':
        assert x['knowledge_id'] in TOPIC, x['id']
        x['topic'] = TOPIC[x['knowledge_id']]

json.dump({'data_version': DV, 'questions': Q}, open(sys.argv[1], 'w'), ensure_ascii=False, indent=1)
from collections import Counter
print(len(Q), Counter(x['kind'] for x in Q), Counter(x['town'] for x in Q))
