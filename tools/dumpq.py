# 問題を一覧で表示する（選択肢の手直し用）。python3 tools/dumpq.py 町 [situation|mcq5|bad]
import json, sys
d = json.load(open('data/questions.json'))['questions']
t = sys.argv[1]; kind = sys.argv[2] if len(sys.argv) > 2 else 'situation'
def bad(q): a = len(q['choices'][q['answer']]); o = max(len(c) for i, c in enumerate(q['choices']) if i != q['answer']); return a >= o * 1.3 and a - o >= 5
for q in d:
    if q['town'] != t and not q['id'].startswith(t): continue
    if kind == 'situation' and not (q['kind'] == 'situation' and any(c.startswith('その通り') for c in q['choices'])): continue
    if kind in ('mcq5', 'bad') and q['kind'] != 'mcq5': continue
    if kind == 'bad' and not bad(q): continue
    print(q['id'], '|', q['question'])
    for i, (c, e) in enumerate(zip(q['choices'], q['choice_explanations'])): print('   ', '◎' if i == q['answer'] else '・', c, '  //', e)
